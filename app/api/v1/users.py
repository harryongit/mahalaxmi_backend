from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Any

from app.db.session import get_db
from app.models.user import User
from app.models.order import Order, OrderStatus, PaymentStatus
from app.schemas.user import User as UserSchema, UserUpdate
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/me", response_model=UserSchema)
async def read_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    return current_user

@router.put("/me", response_model=UserSchema)
async def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    from app.models.user import get_hash
    
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
        
    if "email" in update_data:
        current_user.email_hash = get_hash(update_data["email"])
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.get("/me/stats")
async def read_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    total = await db.scalar(select(func.count(Order.id)).where(Order.user_id == current_user.id))
    completed = await db.scalar(select(func.count(Order.id)).where(Order.user_id == current_user.id, Order.status == OrderStatus.COMPLETED))
    active = await db.scalar(select(func.count(Order.id)).where(Order.user_id == current_user.id, Order.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS])))
    spent = await db.scalar(select(func.coalesce(func.sum(Order.total_amount), 0)).where(Order.user_id == current_user.id, Order.payment_status == PaymentStatus.PAID))

    return {
        "total_orders": total or 0,
        "completed_orders": completed or 0,
        "active_orders": active or 0,
        "total_spent": spent or 0
    }
