from pydantic import BaseModel, EmailStr, constr, field_validator
from datetime import date
from typing import Optional
from fastapi import HTTPException

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=8)  # plain text here, hash before saving
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    dob: Optional[date] = None
    profile_image: Optional[str] = None  # URL or file path
    address: Optional[str] = None
    is_active: Optional[bool] = True

    # Password strength validation
    @field_validator("password")
    def validate_password_strength(cls, v: str) -> str:
        if not any(char.isdigit() for char in v):
            raise HTTPException(400, "Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise HTTPException(400, "Password must contain at least one uppercase letter")
        return v

    # Phone number format validation
    @field_validator("phone_number")
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.isdigit():
            raise HTTPException(400, "Phone number must contain only digits")
        return v

    # Date of birth validation
    @field_validator("dob")
    def validate_dob(cls, v: Optional[date]) -> Optional[date]:
        if v and v > date.today():
            raise HTTPException(400, "Date of birth cannot be in the future")
        return v
