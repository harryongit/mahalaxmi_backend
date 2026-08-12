import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class PaymentVerificationSource(str, enum.Enum):
    FRONTEND_VERIFIED = "FRONTEND_VERIFIED"
    WEBHOOK_VERIFIED = "WEBHOOK_VERIFIED"
    MANUAL_VERIFIED = "MANUAL_VERIFIED"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), unique=True, nullable=False)
    
    razorpay_order_id = Column(String(100), unique=True, index=True, nullable=False)
    razorpay_payment_id = Column(String(100), unique=True, index=True, nullable=True)
    
    amount = Column(Integer, nullable=False) # In paise
    status = Column(String(50), default="PENDING") # COMPLETED, FAILED, PENDING
    
    verification_source = Column(Enum(PaymentVerificationSource), nullable=True)
    payment_method = Column(String(50), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    payment_date = Column(DateTime(timezone=True), nullable=True)
    
    order = relationship("Order", back_populates="payment")
