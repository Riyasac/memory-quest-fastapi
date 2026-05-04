from sqlmodel import Field
from typing import Optional
from datetime import date
from .base_model import AbstractBaseModel


class User(AbstractBaseModel, table=True):
    username: str = Field(index=True, unique=True, nullable=False)
    password: str = Field(nullable=False) # store hashed password
    email: str = Field(index=True, unique=True, nullable=False)
    full_name: Optional[str] = Field(default=None) 
    phone_number: Optional[str] = Field(default=None)
    dob: Optional[date] = Field(default=None)  # Date of Birth
    profile_image: Optional[str] = Field(default=None)  # URL to profile image
    address: Optional[str] = Field(default=None)
