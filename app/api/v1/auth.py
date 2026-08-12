from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import jwt, JWTError
from pydantic import ValidationError

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import OTPRequest, OTPVerify, Token, TokenPayload
from app.services.auth import (
    generate_otp, save_otp, verify_otp,
    send_otp_via_whatsapp,
    check_rate_limit
)
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings

router = APIRouter()

@router.post("/otp/request", status_code=status.HTTP_200_OK)
async def request_otp(
    payload: OTPRequest,
    db: AsyncSession = Depends(get_db)
):
    phone = payload.phone_number
    if not await check_rate_limit(phone):
        raise HTTPException(status_code=429, detail="Too many OTP requests. Try again later.")

    otp = await generate_otp()
    await save_otp(phone, otp)

    wa_success = await send_otp_via_whatsapp(phone, otp)
    if not wa_success:
        raise HTTPException(status_code=500, detail="Failed to send OTP.")

    return {"message": "OTP sent successfully."}

@router.post("/otp/verify", response_model=Token)
async def verify_otp_endpoint(
    payload: OTPVerify,
    db: AsyncSession = Depends(get_db)
):
    phone = payload.phone_number
    is_valid = await verify_otp(phone, payload.otp)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")

    # Find or create user
    from app.models.user import get_hash
    phone_hash = get_hash(phone)
    
    result = await db.execute(select(User).where(User.phone_number_hash == phone_hash))
    user = result.scalars().first()

    if not user:
        user = User(phone_number=phone, phone_number_hash=phone_hash)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token(subject=user.id, is_admin=user.is_admin)
    refresh_token = create_refresh_token(subject=user.id, is_admin=user.is_admin)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=Token)
async def refresh_token(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        payload_data = jwt.decode(
            payload.refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload_data.get("type") != "refresh":
            raise HTTPException(status_code=403, detail="Invalid token type")
        token_data = TokenPayload(**payload_data)
    except (JWTError, ValidationError):
        raise HTTPException(status_code=403, detail="Invalid or expired refresh token")

    result = await db.execute(select(User).where(User.id == token_data.sub))
    user = result.scalars().first()

    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token(subject=user.id, is_admin=user.is_admin)
    refresh_token = create_refresh_token(subject=user.id, is_admin=user.is_admin)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
