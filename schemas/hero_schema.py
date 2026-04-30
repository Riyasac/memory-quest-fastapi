from typing import Optional
from pydantic import BaseModel


class HeroCreate(BaseModel):
    name: str
    secret_name: str
    age: Optional[int] = None
    team_id: Optional[int] = None


class HeroRead(BaseModel):
    id: int
    name: str
    secret_name: str
    age: Optional[int]
    team_id: Optional[int]
