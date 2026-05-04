from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime


class AbstractBaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)
