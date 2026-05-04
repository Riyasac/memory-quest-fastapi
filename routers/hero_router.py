from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.hero import Hero
from models.team import Team
from schemas.hero_schema import HeroCreate, HeroRead
from dependencies.session import get_session

router = APIRouter(prefix="/heroes", tags=["heroes"])


@router.post("/", response_model=Hero)
async def create_hero(hero: HeroCreate, session: AsyncSession = Depends(get_session)):
    db_hero = Hero(**hero.dict())

    # Check if team exists
    result = await session.execute(select(Team).where(Team.id == db_hero.team_id))
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )

    session.add(db_hero)
    await session.commit()
    await session.refresh(db_hero)
    return db_hero


@router.get("/", response_model=list[Hero])
async def read_heroes(
    session: AsyncSession = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=10, le=100),
):
    result = await session.execute(select(Hero).offset(offset).limit(limit))
    heroes = result.scalars().all()
    return heroes


@router.get("/{hero_id}", response_model=HeroRead)
async def get_hero(hero_id: int, session: AsyncSession = Depends(get_session)):
    hero = await session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found"
        )
    return hero


@router.put("/{hero_id}", response_model=Hero)
async def update_hero(
    hero_id: int, hero: Hero, session: AsyncSession = Depends(get_session)
):
    db_hero = await session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found"
        )

    hero_data = hero.model_dump(exclude_unset=True)
    db_hero.sqlmodel_update(hero_data)

    session.add(db_hero)
    await session.commit()
    await session.refresh(db_hero)
    return db_hero


@router.delete("/{hero_id}", response_model=Hero)
async def delete_hero(hero_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Hero).where(Hero.id == hero_id))
    hero = result.scalar_one_or_none()
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found"
        )

    await session.delete(hero)
    await session.commit()
    return hero
