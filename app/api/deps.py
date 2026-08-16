from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="", auto_error=False)

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> User:
    """
    Token requirement removed. Always returns active user.
    """
    result = await db.execute(select(User))
    user = result.scalars().first()
    
    if not user:
        user = User(
            full_name="Mahalaxmi Devotee",
            phone_number="+919876543210",
            email="admin@mahalaxmikolhapur.com",
            is_active=True,
            is_admin=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    return user

async def get_current_active_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Token requirement removed. Always returns active admin.
    """
    return current_user
