from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import GanEnum

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

class UserCreate(UserBase):
    phone_number: str

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
