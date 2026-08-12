from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.db.session import get_db
from app.models.user import User, get_hash
from app.schemas.user import User as UserSchema
from app.api.deps import get_current_active_admin
from app.core.security import get_password_hash
import phonenumbers
from pydantic import BaseModel, EmailStr, field_validator

router = APIRouter()

class UserStatusUpdate(BaseModel):
    is_active: bool

class AdminUserCreate(BaseModel):
    phone_number: str
    email: Optional[EmailStr] = None
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        try:
            parsed = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number")

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value

@router.get("/", response_model=List[UserSchema], dependencies=[Depends(get_current_active_admin)])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_active_admin)])
async def create_admin_user(
    user_in: AdminUserCreate,
    db: AsyncSession = Depends(get_db)
):
    phone_hash = get_hash(user_in.phone_number)
    existing = await db.execute(select(User).where(User.phone_number_hash == phone_hash))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="User with this phone number already exists")

    if user_in.email:
        email_hash = get_hash(user_in.email)
        existing_email = await db.execute(select(User).where(User.email_hash == email_hash))
        if existing_email.scalars().first():
            raise HTTPException(status_code=409, detail="User with this email already exists")

    user = User(
        phone_number=user_in.phone_number,
        phone_number_hash=phone_hash,
        email=user_in.email,
        email_hash=get_hash(user_in.email) if user_in.email else None,
        hashed_password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        is_admin=True,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/{id}", response_model=UserSchema, dependencies=[Depends(get_current_active_admin)])
async def get_user(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{id}/status", response_model=UserSchema, dependencies=[Depends(get_current_active_admin)])
async def update_user_status(id: int, status_in: UserStatusUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_active = status_in.is_active
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
