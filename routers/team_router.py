from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.team import Team
from dependencies.session import get_session

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=Team)
async def create_team(team: Team, session: AsyncSession = Depends(get_session)):
    session.add(team)
    await session.commit()
    await session.refresh(team)
    return team


@router.get("/", response_model=list[Team])
async def read_teams(
    session: AsyncSession = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=10, le=100),
):
    result = await session.execute(select(Team).offset(offset).limit(limit))
    teams = result.scalars().all()
    return teams


@router.get("/{team_id}", response_model=Team)
async def get_team(team_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    return team


@router.put("/{team_id}", response_model=Team)
async def update_team(
    team_id: int, team: Team, session: AsyncSession = Depends(get_session)
):
    db_team = await session.get(Team, team_id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    team_data = team.model_dump(exclude_unset=True)
    db_team.sqlmodel_update(team_data)
    session.add(db_team)
    await session.commit()
    await session.refresh(db_team)
    return db_team


@router.delete("/{team_id}", response_model=Team)
async def delete_team(team_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    await session.delete(team)
    await session.commit()
    return team
