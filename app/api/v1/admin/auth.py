from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.user import User, get_hash
from app.schemas.admin_auth import AdminLoginRequest, AdminLoginResponse, AdminVerify2FA
from app.schemas.auth import Token
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.services.auth import (
    check_admin_lockout, increment_admin_lockout, reset_admin_lockout,
    generate_otp, save_otp, verify_otp, send_otp_via_email
)

router = APIRouter()

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    payload: AdminLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    if not await check_admin_lockout(payload.email):
        raise HTTPException(status_code=429, detail="Too many failed login attempts. Account locked for 15 minutes.")

    email_hash = get_hash(payload.email)
    result = await db.execute(select(User).where(User.email_hash == email_hash, User.is_admin == True))
    user = result.scalars().first()

    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        await increment_admin_lockout(payload.email)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    await reset_admin_lockout(payload.email)

    # Generate 2FA OTP
    otp = await generate_otp()
    # Save OTP using admin's ID or email as key
    await save_otp(f"admin_{user.id}", otp)
    
    # In production, send via email or SMS
    await send_otp_via_email(payload.email, otp)

    return {"message": "2FA OTP sent", "admin_id": user.id}

@router.post("/verify-2fa", response_model=Token)
async def admin_verify_2fa(
    payload: AdminVerify2FA,
    db: AsyncSession = Depends(get_db)
):
    is_valid = await verify_otp(f"admin_{payload.admin_id}", payload.otp)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    result = await db.execute(select(User).where(User.id == payload.admin_id, User.is_admin == True))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Admin not found")

    access_token = create_access_token(subject=user.id, is_admin=True)
    refresh_token = create_refresh_token(subject=user.id, is_admin=True)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
