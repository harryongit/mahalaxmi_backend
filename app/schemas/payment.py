from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.payment import PaymentVerificationSource

class PaymentCreate(BaseModel):
    order_id: int

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class PaymentOut(BaseModel):
    id: int
    order_id: int
    razorpay_order_id: str
    razorpay_payment_id: Optional[str] = None
    amount: int
    status: str
    verification_source: Optional[PaymentVerificationSource] = None
    payment_method: Optional[str] = None
    created_at: datetime
    payment_date: Optional[datetime] = None

    class Config:
        from_attributes = True
