from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from models.hero import Hero
from models.team import Team
from schemas.hero_schema import HeroCreate, HeroRead
from dependencies.session import get_session

router = APIRouter(prefix="/heroes", tags=["heroes"])

@router.post("/", response_model=Hero)
def create_hero(hero: HeroCreate, session: Session = Depends(get_session)):
    hero = Hero(**hero.dict())
    try:
        team = session.exec(select(Team).where(Team.id == hero.team_id)).one()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.get("/", response_model=list[Hero])
async def read_heroes(session: Session = Depends(get_session)):
    heroes = session.exec(select(Hero)).all()
    return heroes


@router.get("/{hero_id}", response_model=HeroRead)
def get_hero(hero_id: int, session: Session = Depends(get_session)):
    hero = session.exec(select(Hero).where(Hero.id == hero_id)).first()
    if not hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
    return hero


@router.put("/{hero_id}", response_model=Hero)
def update_hero(hero_id: int, hero: Hero, session: Session = Depends(get_session)):
    try:
        hero_1 = session.exec(select(Hero).where(Hero.id == hero_id)).one()
        hero_1.name = hero.name
        hero_1.secret_name = hero.secret_name
        hero_1.age = hero.age
        hero_1.team_id = hero.team_id
        session.add(hero_1)
        session.commit()
        session.refresh(hero_1)
        return hero_1
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")


@router.delete("/{hero_id}", response_model=Hero)
def delete_hero(hero_id: int, session: Session = Depends(get_session)):
    hero_1 = session.exec(select(Hero).where(Hero.id == hero_id)).first()
    if not hero_1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
    
    session.delete(hero_1)
    session.commit()
    return hero_1
