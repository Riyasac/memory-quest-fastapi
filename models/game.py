from sqlmodel import SQLModel, Field
from typing import Optional
import datetime


class Game(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    player_name: str = Field(index=True)
    level: int = Field(default=1)
    board_state: str  # JSON string of cards (hidden/revealed)
    moves: int = Field(default=0)
    completed: bool = Field(default=False)
    start_time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    end_time: Optional[datetime.datetime] = None
