from sqlmodel import Field, SQLModel, create_engine
import os

engine = create_engine(os.getenv("DATABASE_URL"))


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)
    team_id: int | None = Field(default=None, foreign_key="team.id")


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
