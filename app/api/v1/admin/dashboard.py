from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, cast, Date
from datetime import datetime, date, timedelta

from app.db.session import get_db
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.payment import Payment
from app.models.user import User
from app.api.deps import get_current_active_admin

router = APIRouter()

@router.get("/summary", dependencies=[Depends(get_current_active_admin)])
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    users_count = await db.scalar(select(func.count(User.id)))
    orders_count = await db.scalar(select(func.count(Order.id)))
    revenue = await db.scalar(select(func.sum(Order.total_amount)).where(Order.payment_status == PaymentStatus.PAID))
    today_orders = await db.scalar(select(func.count(Order.id)).where(Order.created_at >= today_start, Order.created_at < today_end))
    today_revenue = await db.scalar(select(func.sum(Order.total_amount)).where(Order.payment_status == PaymentStatus.PAID, Order.created_at >= today_start, Order.created_at < today_end))

    return {
        "total_users": users_count,
        "total_orders": orders_count,
        "total_revenue": revenue or 0,
        "today_bookings": today_orders or 0,
        "today_revenue": today_revenue or 0
    }

@router.get("/recent-orders", dependencies=[Depends(get_current_active_admin)])
async def get_recent_orders(db: AsyncSession = Depends(get_db)):
    stmt = select(Order).order_by(Order.created_at.desc()).limit(10)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/recent-payments", dependencies=[Depends(get_current_active_admin)])
async def get_recent_payments(db: AsyncSession = Depends(get_db)):
    stmt = select(Payment).order_by(Payment.created_at.desc()).limit(10)
    result = await db.execute(stmt)
    return result.scalars().all()
