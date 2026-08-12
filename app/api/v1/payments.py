import razorpay
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Any
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.payment import Payment, PaymentVerificationSource
from app.schemas.payment import PaymentCreate, PaymentVerify, PaymentOut
from app.api.deps import get_current_user, get_current_active_admin
from app.core.config import settings

router = APIRouter()

# Initialize Razorpay Client
rzp_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@router.post("/create-order", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
async def create_payment_order(
    payload: PaymentCreate,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Get local order
    stmt = select(Order).where(Order.id == payload.order_id, Order.user_id == current_user.id)
    result = await db.execute(stmt)
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order.payment_status == PaymentStatus.PAID:
        raise HTTPException(status_code=400, detail="Order is already paid")
    
    # Check if a payment already exists for this order
    stmt_payment = select(Payment).where(Payment.order_id == order.id)
    res_payment = await db.execute(stmt_payment)
    existing_payment = res_payment.scalars().first()
    
    if existing_payment and existing_payment.status == "PENDING":
        response.status_code = status.HTTP_200_OK
        return existing_payment

    # Create Razorpay Order
    data = {
        "amount": order.total_amount,
        "currency": "INR",
        "receipt": order.order_id,
        "notes": {
            "user_id": current_user.id,
            "order_id": order.id
        }
    }
    
    try:
        rzp_order = rzp_client.order.create(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    payment = Payment(
        order_id=order.id,
        razorpay_order_id=rzp_order['id'],
        amount=order.total_amount,
        status="PENDING"
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    
    return payment

@router.post("/verify")
async def verify_payment(
    payload: PaymentVerify,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    try:
        rzp_client.utility.verify_payment_signature({
            'razorpay_order_id': payload.razorpay_order_id,
            'razorpay_payment_id': payload.razorpay_payment_id,
            'razorpay_signature': payload.razorpay_signature
        })
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Update Payment
    stmt = select(Payment).where(Payment.razorpay_order_id == payload.razorpay_order_id)
    result = await db.execute(stmt)
    payment = result.scalars().first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
        
    if payment.status == "COMPLETED":
        return {"message": "Payment already verified"}

    payment.razorpay_payment_id = payload.razorpay_payment_id
    payment.status = "COMPLETED"
    payment.verification_source = PaymentVerificationSource.FRONTEND_VERIFIED
    payment.payment_date = datetime.utcnow()
    db.add(payment)
    
    # Update Order
    stmt_order = select(Order).where(Order.id == payment.order_id)
    result_order = await db.execute(stmt_order)
    order = result_order.scalars().first()
    
    order.payment_status = PaymentStatus.PAID
    order.status = OrderStatus.CONFIRMED
    db.add(order)
    
    await db.commit()
    
    from app.worker.tasks import send_whatsapp_notification, send_email_notification, dispatch
    if current_user.whatsapp_opt_in:
        dispatch(send_whatsapp_notification, current_user.phone_number, f"Your order {order.order_id} has been confirmed! Thank you for your payment.")
    if current_user.email:
        dispatch(send_email_notification, current_user.email, "Order Confirmed", f"Your order {order.order_id} has been confirmed. Thank you!")
    
    return {"message": "Payment verified successfully"}

@router.post("/webhook")
async def razorpay_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("x-razorpay-signature")
    
    webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET or settings.RAZORPAY_KEY_SECRET
    
    try:
        rzp_client.utility.verify_webhook_signature(payload.decode('utf-8'), signature, webhook_secret)
    except Exception:
        # Ignore invalid webhooks, return 400
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    
    data = await request.json()
    event = data.get("event")
    
    if event == "payment.captured":
        payment_entity = data['payload']['payment']['entity']
        rzp_order_id = payment_entity.get('order_id')
        rzp_payment_id = payment_entity.get('id')
        
        stmt = select(Payment).where(Payment.razorpay_order_id == rzp_order_id)
        result = await db.execute(stmt)
        payment = result.scalars().first()
        
        if payment and payment.status != "COMPLETED":
            payment.razorpay_payment_id = rzp_payment_id
            payment.status = "COMPLETED"
            payment.verification_source = PaymentVerificationSource.WEBHOOK_VERIFIED
            payment.payment_date = datetime.utcnow()
            db.add(payment)
            
            stmt_order = select(Order).where(Order.id == payment.order_id)
            result_order = await db.execute(stmt_order)
            order = result_order.scalars().first()
            if order:
                order.payment_status = PaymentStatus.PAID
                order.status = OrderStatus.CONFIRMED
                db.add(order)
                
            await db.commit()
            
            from app.worker.tasks import send_whatsapp_notification, send_email_notification, dispatch
            stmt_user = select(User).where(User.id == order.user_id)
            result_user = await db.execute(stmt_user)
            user = result_user.scalars().first()
            if user:
                if user.whatsapp_opt_in:
                    dispatch(send_whatsapp_notification, user.phone_number, f"Your order {order.order_id} has been confirmed! Thank you for your payment.")
                if user.email:
                    dispatch(send_email_notification, user.email, "Order Confirmed", f"Your order {order.order_id} has been confirmed. Thank you!")
            
    # Always return 200 OK for webhook idempotency
    return {"status": "ok"}

@router.post("/admin/{id}/refund", dependencies=[Depends(get_current_active_admin)])
async def process_refund(
    id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Payment).where(Payment.id == id)
    result = await db.execute(stmt)
    payment = result.scalars().first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
        
    if payment.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="Only completed payments can be refunded")
        
    try:
        # Razorpay refund API
        refund = rzp_client.payment.refund(payment.razorpay_payment_id, {
            "amount": payment.amount
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refund failed: {str(e)}")
        
    payment.status = "REFUNDED"
    db.add(payment)
    
    stmt_order = select(Order).where(Order.id == payment.order_id)
    result_order = await db.execute(stmt_order)
    order = result_order.scalars().first()
    if order:
        order.payment_status = PaymentStatus.REFUNDED
        db.add(order)
        
    await db.commit()
    return {"message": "Refund processed successfully", "refund_id": refund.get("id")}
