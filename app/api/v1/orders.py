from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Any, List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.service import Service
from app.schemas.order import OrderCreate, OrderOut
from app.api.deps import get_current_user, get_current_active_admin
from app.utils.helpers import generate_order_id

router = APIRouter()

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Validate at least one item
    if not order_in.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    # Validate that all requested services exist
    service_ids = list({item.service_id for item in order_in.items})
    result = await db.execute(select(Service.id).where(Service.id.in_(service_ids)))
    found_ids = set(result.scalars().all())
    missing = [sid for sid in service_ids if sid not in found_ids]
    if missing:
        raise HTTPException(status_code=400, detail=f"Invalid service_id: service(s) {missing} not found")

    # Calculate total amount based on items provided
    total_amount = sum([item.amount for item in order_in.items])
    
    order = Order(
        order_id=generate_order_id(),
        user_id=current_user.id,
        total_amount=total_amount,
        notes=order_in.notes,
        booking_date=datetime.utcnow()
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    # Add order items
    for item_in in order_in.items:
        order_item = OrderItem(
            order_id=order.id,
            service_id=item_in.service_id,
            devotee_name=item_in.devotee_name,
            gotra=item_in.gotra,
            scheduled_date=item_in.scheduled_date,
            amount=item_in.amount
        )
        db.add(order_item)
    
    await db.commit()

    from app.worker.tasks import send_whatsapp_notification
    if current_user.whatsapp_opt_in:
        send_whatsapp_notification.delay(current_user.phone_number, f"Your order {order.order_id} has been placed! We will notify you once confirmed.")
    
    # Refresh to get items loaded
    stmt = select(Order).options(selectinload(Order.items).selectinload(OrderItem.service)).where(Order.id == order.id)
    res = await db.execute(stmt)
    return res.scalars().first()

@router.get("/", response_model=List[OrderOut])
async def list_user_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Order).options(selectinload(Order.items).selectinload(OrderItem.service)).where(Order.user_id == current_user.id)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{order_id}", response_model=OrderOut)
async def get_order_detail(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Order).options(selectinload(Order.items).selectinload(OrderItem.service)).where(Order.order_id == order_id)
    result = await db.execute(stmt)
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return order

@router.patch("/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Order).where(Order.order_id == order_id, Order.user_id == current_user.id)
    result = await db.execute(stmt)
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending orders can be cancelled")
        
    order.status = OrderStatus.CANCELLED
    db.add(order)
    await db.commit()
    
    return {"message": "Order cancelled successfully"}

@router.get("/{order_id}/invoice")
async def download_invoice(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Order).options(selectinload(Order.items).selectinload(OrderItem.service)).where(Order.order_id == order_id)
    result = await db.execute(stmt)
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    if order.payment_status != PaymentStatus.PAID:
        raise HTTPException(status_code=400, detail="Invoice only available for paid orders")

    # Assuming user name is decrypted automatically or just pass hash. We'll fetch user to get name.
    stmt_user = select(User).where(User.id == order.user_id)
    res_user = await db.execute(stmt_user)
    user = res_user.scalars().first()
    
    user_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    if not user_name:
        user_name = "Devotee"

    from app.services.pdf import generate_invoice_pdf
    from fastapi.responses import FileResponse
    import os
    
    pdf_path = generate_invoice_pdf(order, user_name)
    
    return FileResponse(
        pdf_path, 
        media_type='application/pdf', 
        filename=f"Invoice_{order.order_id}.pdf"
    )

@router.get("/admin/list", response_model=List[OrderOut], dependencies=[Depends(get_current_active_admin)])
async def list_all_orders(
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Order).options(selectinload(Order.items).selectinload(OrderItem.service))
    result = await db.execute(stmt)
    return result.scalars().all()

class AdminOrderStatusUpdate(BaseModel):
    status: OrderStatus
    payment_status: Optional[PaymentStatus] = None

@router.patch("/admin/{order_id}/status", dependencies=[Depends(get_current_active_admin)])
async def admin_update_order_status(
    order_id: str,
    status_in: AdminOrderStatusUpdate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Order).options(selectinload(Order.items).selectinload(OrderItem.service)).where(Order.order_id == order_id)
    result = await db.execute(stmt)
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status_in.status
    if status_in.payment_status:
        order.payment_status = status_in.payment_status

    db.add(order)
    await db.commit()
    await db.refresh(order)

    stmt = select(Order).options(selectinload(Order.items).selectinload(OrderItem.service)).where(Order.id == order.id)
    res = await db.execute(stmt)
    return res.scalars().first()
