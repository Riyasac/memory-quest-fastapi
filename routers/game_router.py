import datetime
import json
import random

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from dependencies.session import get_session
from models.game import Game

router = APIRouter(prefix="/game", tags=["game"])
templates = Jinja2Templates(directory="templates")
MAX_LEVEL = 100


@router.get("/", response_class=HTMLResponse)
async def game(request: Request):
    return templates.TemplateResponse(
        name="game.html", request=request, context={"request": request}
    )


@router.get("/levels", response_class=HTMLResponse)
async def game_levels(request: Request):
    return templates.TemplateResponse(
        name="levels.html", request=request, context={"request": request}
    )

@router.get("/ranks", response_class=HTMLResponse)
async def game_ranks(request: Request):
    return templates.TemplateResponse(
        name="ranks.html", request=request, context={"request": request}
    )


@router.get("/profile", response_class=HTMLResponse)
async def game_profile(request: Request):
    return templates.TemplateResponse(
        name="profile.html", request=request, context={"request": request}
    )


@router.get("/about", response_class=HTMLResponse)
async def game_about(request: Request):
    return templates.TemplateResponse(
        name="about.html", request=request, context={"request": request}
    )


def normalize_indices(indices: list, deck_size: int) -> list[int]:
    normalized: list[int] = []
    for value in indices:
        try:
            index = int(value)
        except (TypeError, ValueError):
            continue
        if 0 <= index < deck_size and index not in normalized:
            normalized.append(index)
    return normalized


def parse_board_state(board_state: str) -> dict:
    parsed = json.loads(board_state)
    if isinstance(parsed, dict):
        deck = parsed.get("deck", [])
        matched = parsed.get("matched", [])
        revealed = parsed.get("revealed", [])
    else:
        deck = parsed
        matched = []
        revealed = []

    if not isinstance(deck, list):
        deck = []
    deck_size = len(deck)
    matched = normalize_indices(matched if isinstance(matched, list) else [], deck_size)
    revealed = normalize_indices(
        revealed if isinstance(revealed, list) else [], deck_size
    )
    revealed = [index for index in revealed if index not in matched]
    return {"deck": deck, "matched": matched, "revealed": revealed}


def serialize_board_state(deck: list, matched: list[int], revealed: list[int]) -> str:
    return json.dumps({"deck": deck, "matched": matched, "revealed": revealed})


def masked_board(deck: list, matched: list[int], revealed: list[int]) -> list:
    visible = set(matched + revealed)
    return [card if index in visible else "?" for index, card in enumerate(deck)]


async def get_player_progress(
    player_name: str, session: AsyncSession
) -> tuple[int, set[int], set[int]]:
    completed_result = await session.execute(
        select(Game.level).where(
            Game.player_name == player_name,
            Game.completed == True,  # noqa: E712
        )
    )
    completed_levels = {
        level for level in completed_result.scalars().all() if isinstance(level, int)
    }
    highest_completed = max(completed_levels) if completed_levels else 0
    unlocked_level = min(max(1, highest_completed + 1), MAX_LEVEL)

    in_progress_result = await session.execute(
        select(Game.level).where(
            Game.player_name == player_name,
            Game.completed == False,  # noqa: E712
        )
    )
    in_progress_levels = {
        level for level in in_progress_result.scalars().all() if isinstance(level, int)
    }
    return unlocked_level, completed_levels, in_progress_levels


def generate_deck(level: int):
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    numbers = [str(i) for i in range(1, 51)]
    symbols = [
        "★",
        "♥",
        "♦",
        "♣",
        "♠",
        "☀",
        "☂",
        "☯",
        "⚡",
        "✔",
        "✖",
        "✿",
        "☮",
        "☢",
        "☣",
    ]
    emojis = [
        "😀",
        "🐱",
        "🚀",
        "🍕",
        "⚽",
        "🎵",
        "🌈",
        "🔥",
        "🐶",
        "🐼",
        "🍔",
        "🍩",
        "🎮",
        "🎧",
        "📚",
        "✈️",
        "🎉",
        "💡",
        "🧩",
        "🕹",
    ]

    if level <= 10:
        pool = letters[:8] if level % 2 == 1 else emojis[:8]
        pairs = 8
    elif level <= 20:
        pool = numbers[:18] if level % 2 == 0 else symbols[:15] + numbers[:3]
        pairs = 18
    elif level <= 30:
        pool = (letters + emojis + symbols)[:32]
        pairs = 32
    elif level <= 40:
        pool = (emojis + numbers + symbols + letters)[:50]
        pairs = 50
    elif level <= 50:
        pool = (letters + emojis + symbols + numbers)[:72]
        pairs = 72
    else:
        pool = letters[:8]
        pairs = 8

    deck = pool[:pairs] * 2
    random.shuffle(deck)
    return deck


@router.post("/start")
async def start_game(
    player_name: str = Query(..., min_length=1),
    level: int = Query(default=1, ge=1, le=MAX_LEVEL),
    session: AsyncSession = Depends(get_session),
):
    unlocked_level, _, _ = await get_player_progress(
        player_name=player_name, session=session
    )
    if level > unlocked_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Level {level} is locked. Unlocked levels are up to {unlocked_level}.",
        )

    result = await session.execute(
        select(Game)
        .where(
            Game.player_name == player_name,
            Game.level == level,
            Game.completed == False,  # noqa: E712
        )
        .order_by(Game.start_time.desc())
    )
    game = result.scalars().first()

    if not game:
        deck = generate_deck(level)
        game = Game(
            player_name=player_name,
            level=level,
            board_state=serialize_board_state(deck, [], []),
        )
        session.add(game)
        await session.commit()
        await session.refresh(game)

    state = parse_board_state(game.board_state)
    return {
        "game_id": game.id,
        "board": masked_board(state["deck"], state["matched"], state["revealed"]),
        "level": game.level,
        "moves": game.moves,
        "matched": state["matched"],
        "revealed": state["revealed"],
        "completed": game.completed,
        "start_time": game.start_time.isoformat(),
    }


@router.post("/flip")
async def flip_card(
    game_id: int,
    index: int,
    session: AsyncSession = Depends(get_session),
):
    game = await session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.completed:
        raise HTTPException(status_code=400, detail="Game already completed")

    state = parse_board_state(game.board_state)
    deck = state["deck"]
    matched = state["matched"]
    revealed = state["revealed"]

    if index < 0 or index >= len(deck):
        raise HTTPException(status_code=400, detail="Invalid card index")

    if index not in matched and index not in revealed:
        if len(revealed) >= 2:
            raise HTTPException(
                status_code=400,
                detail="Two cards are already revealed. Please check match first.",
            )
        revealed.append(index)
        game.board_state = serialize_board_state(deck, matched, revealed)
        session.add(game)
        await session.commit()

    return {"card": deck[index]}


@router.post("/check")
async def check_match(
    game_id: int,
    first: int,
    second: int,
    session: AsyncSession = Depends(get_session),
):
    game = await session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.completed:
        raise HTTPException(status_code=400, detail="Game already completed")

    state = parse_board_state(game.board_state)
    deck = state["deck"]
    matched = state["matched"]
    revealed = state["revealed"]

    if first == second:
        raise HTTPException(status_code=400, detail="Select two different cards")
    if min(first, second) < 0 or max(first, second) >= len(deck):
        raise HTTPException(status_code=400, detail="Invalid card index")

    if first not in revealed:
        revealed.append(first)
    if second not in revealed:
        revealed.append(second)

    game.moves += 1
    is_match = deck[first] == deck[second]
    if is_match:
        if first not in matched:
            matched.append(first)
        if second not in matched:
            matched.append(second)
        revealed = [idx for idx in revealed if idx not in (first, second)]

        if len(matched) == len(deck):
            game.completed = True
            game.end_time = datetime.datetime.utcnow()
    else:
        revealed = [idx for idx in revealed if idx not in (first, second)]

    game.board_state = serialize_board_state(deck, matched, revealed)
    session.add(game)
    await session.commit()
    await session.refresh(game)
    return {
        "match": is_match,
        "value": deck[first],
        "moves": game.moves,
        "completed": game.completed,
        "matched": matched,
        "revealed": revealed,
        "board": masked_board(deck, matched, revealed),
    }


@router.post("/shuffle")
async def shuffle_hard_level(
    game_id: int,
    session: AsyncSession = Depends(get_session),
):
    game = await session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    if game.completed:
        raise HTTPException(status_code=400, detail="Game already completed")
    if game.level < 21:
        raise HTTPException(
            status_code=400,
            detail="Shuffle is available only for hard levels (21+).",
        )

    state = parse_board_state(game.board_state)
    deck = state["deck"]
    matched = state["matched"]
    matched_set = set(matched)

    unmatched_indices = [idx for idx in range(len(deck)) if idx not in matched_set]
    if len(unmatched_indices) <= 1:
        return {
            "board": masked_board(deck, matched, []),
            "matched": matched,
            "revealed": [],
            "level": game.level,
            "moves": game.moves,
        }

    unmatched_values = [deck[idx] for idx in unmatched_indices]
    random.shuffle(unmatched_values)
    for idx, value in zip(unmatched_indices, unmatched_values):
        deck[idx] = value

    revealed: list[int] = []
    game.board_state = serialize_board_state(deck, matched, revealed)
    session.add(game)
    await session.commit()
    await session.refresh(game)

    return {
        "board": masked_board(deck, matched, revealed),
        "matched": matched,
        "revealed": revealed,
        "level": game.level,
        "moves": game.moves,
    }


@router.get("/state")
async def game_state(game_id: int, session: AsyncSession = Depends(get_session)):
    game = await session.get(Game, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    state = parse_board_state(game.board_state)
    return {
        "game_id": game.id,
        "level": game.level,
        "board_state": game.board_state,
        "board": masked_board(state["deck"], state["matched"], state["revealed"]),
        "matched": state["matched"],
        "revealed": state["revealed"],
        "moves": game.moves,
        "completed": game.completed,
        "start_time": game.start_time.isoformat(),
    }


@router.get("/levels/status")
async def levels_status(
    player_name: str = Query(..., min_length=1),
    session: AsyncSession = Depends(get_session),
):
    unlocked_level, completed_levels, in_progress_levels = await get_player_progress(
        player_name=player_name, session=session
    )
    levels = []
    for level in range(1, MAX_LEVEL + 1):
        levels.append(
            {
                "level": level,
                "locked": level > unlocked_level,
                "completed": level in completed_levels,
                "in_progress": level in in_progress_levels,
            }
        )
    return {
        "player_name": player_name,
        "max_level": MAX_LEVEL,
        "unlocked_level": unlocked_level,
        "levels": levels,
    }


@router.get("/leaderboard")
async def leaderboard(session: AsyncSession = Depends(get_session)):
    # Fetch all completed games ordered by performance
    result = await session.execute(
        select(Game)
        .where(Game.completed == True)
        .order_by(Game.level.desc(), Game.moves, Game.end_time)
    )
    games = result.scalars().all()

    # Group by player to get their best level and performance
    player_stats = {}
    for game in games:
        if game.player_name not in player_stats:
            player_stats[game.player_name] = {
                "player_name": game.player_name,
                "best_level": game.level,
                "moves": game.moves,
                "time": (game.end_time - game.start_time).total_seconds(),
            }

    # Sort players by best level, then moves, then time
    sorted_players = sorted(
        player_stats.values(), key=lambda g: (-g["best_level"], g["moves"], g["time"])
    )

    # Assign rank numbers
    leaderboard = []
    for rank, player in enumerate(sorted_players, start=1):
        leaderboard.append(
            {
                "rank": rank,
                "player_name": player["player_name"],
                "level": player["best_level"],
                "moves": player["moves"],
                "time": player["time"],
            }
        )
    return leaderboard
