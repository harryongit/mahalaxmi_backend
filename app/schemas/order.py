from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderStatus, PaymentStatus
from app.schemas.service import ServiceOut

class OrderItemCreate(BaseModel):
    service_id: int
    devotee_name: Optional[str] = None
    gotra: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    amount: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    notes: Optional[str] = None

class OrderItemOut(BaseModel):
    id: int
    service_id: int
    devotee_name: Optional[str] = None
    gotra: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    amount: int
    status: str
    service: Optional[ServiceOut] = None
    
    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    order_id: str
    user_id: int
    status: OrderStatus
    payment_status: PaymentStatus
    total_amount: int
    notes: Optional[str] = None
    booking_date: Optional[datetime] = None
    created_at: datetime
    items: List[OrderItemOut] = []
    
    class Config:
        from_attributes = True
