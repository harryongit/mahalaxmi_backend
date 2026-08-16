from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.user import User, get_hash
from app.schemas.admin_auth import AdminLoginRequest
from app.core.security import verify_password, get_password_hash
from app.core.logging import logger

router = APIRouter()

@router.post("/login")
async def admin_login(
    payload: AdminLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Admin Login Endpoint checking admin@gmail.com / Admin@12345 credentials.
    """
    try:
        email = payload.email.strip().lower()
        password = payload.password

        # Check default designated admin credentials
        if email == "admin@gmail.com":
            if password == "Admin@12345":
                return {
                    "message": "Admin Login Successful!",
                    "admin_id": 1,
                    "access_token": "token_admin_authenticated",
                    "token_type": "bearer"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

        # Also support admin@mahalaxmikolhapur.com / Admin@12345
        if email == "admin@mahalaxmikolhapur.com" and password == "Admin@12345":
            return {
                "message": "Admin Login Successful!",
                "admin_id": 1,
                "access_token": "token_admin_authenticated",
                "token_type": "bearer"
            }

        # Check database for registered admin users
        email_hash = get_hash(email)
        result = await db.execute(select(User).where(User.email_hash == email_hash, User.is_admin == True))
        user = result.scalars().first()

        if user and user.hashed_password:
            if verify_password(password, user.hashed_password):
                return {
                    "message": "Admin Login Successful!",
                    "admin_id": user.id,
                    "access_token": "token_admin_authenticated",
                    "token_type": "bearer"
                }

        # If credentials do not match, return 401 Unauthorized
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except HTTPException as e:
        raise e
    except Exception as err:
        logger.error(f"Login processing error: {err}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
