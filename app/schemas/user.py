import re
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from app.models.user import GanEnum

PHONE_REGEX = r'^\+?[1-9]\d{1,14}$'

class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    gotra: Optional[str] = None
    gan: Optional[GanEnum] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    country: Optional[str] = None
    whatsapp_opt_in: Optional[bool] = False

    @validator('pin_code')
    @classmethod
    def validate_pin_code(cls, v: str) -> str:
        if v and not v.isdigit():
            raise ValueError("PIN code must contain only digits")
        return v

class UserCreate(UserBase):
    phone_number: str

    @validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        if not re.match(PHONE_REGEX, v):
            raise ValueError('Invalid phone format. Use E.164: +919876543210')
        return v

class UserUpdate(UserBase):
    pass

class UserInDBBase(UserBase):
    id: int
    phone_number: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass