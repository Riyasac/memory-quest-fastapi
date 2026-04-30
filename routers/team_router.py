from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from models.team import Team
from dependencies.session import get_session

router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("/", response_model=Team)
def create_team(team: Team, session: Session = Depends(get_session)):
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


@router.get("/", response_model=list[Team])
def read_teams(session: Session = Depends(get_session)):
    teams = session.exec(select(Team)).all()
    return teams


@router.get("/{team_id}", response_model=Team)
def get_team(team_id: int, session: Session = Depends(get_session)):
    try:
        team = session.exec(select(Team).where(Team.id == team_id)).one()
        return team
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")


@router.put("/{team_id}", response_model=Team)
def update_team(team_id: int, team: Team, session: Session = Depends(get_session)):
    try:
        team1 = session.exec(select(Team).where(Team.id == team_id)).one()
        team1.name = team.name
        team1.headquarters = team.name
        session.add(team1)
        session.commit()
        session.refresh(team1)
        return team1
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")


@router.delete("/{team_id}", response_model=Team)
def delete_team(team_id: int, session: Session = Depends(get_session)):
    try:
        team1 = session.exec(select(Team).where(Team.id == team_id)).one()
        session.delete(team1)
        session.commit()
        return team1
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
