from pydantic import BaseModel, Field
from enum import Enum

class Image(BaseModel):
    url: str
    name: str


class Item(BaseModel):
    name: str
    price: float
    description: str | None = Field(default=None, examples=["A very nice Item"])
    tax: float | None = None
    is_active: bool = True
    tags: list = []
    image: Image | None = None


class OrderStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"
