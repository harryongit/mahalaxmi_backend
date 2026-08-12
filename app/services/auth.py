import random
import string
from datetime import timedelta
from typing import Optional
from app.core.redis import get_redis
from app.core.config import settings
from app.core.logging import logger
from app.worker.tasks import send_email_notification

OTP_EXPIRY_MINUTES = 5

async def generate_otp() -> str:
    # 6 digit OTP
    return ''.join(random.choices(string.digits, k=6))

async def save_otp(phone_number: str, otp: str) -> None:
    redis_client = await get_redis()
    key = f"otp:{phone_number}"
    await redis_client.setex(key, timedelta(minutes=OTP_EXPIRY_MINUTES), otp)

async def verify_otp(phone_number: str, provided_otp: str) -> bool:
    redis_client = await get_redis()
    key = f"otp:{phone_number}"
    stored_otp = await redis_client.get(key)
    
    if stored_otp and stored_otp == provided_otp:
        # OTP is valid, delete it
        await redis_client.delete(key)
        return True
    return False

import asyncio
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

async def send_otp_via_whatsapp(phone_number: str, otp: str) -> bool:
    if not settings.TWILIO_ACCOUNT_SID:
        logger.info("Twilio not configured — WhatsApp OTP not sent", extra={"phone": phone_number, "otp": otp})
        return True
    
    def _send():
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        return client.messages.create(
            body=f"Your MahalaxmiPuja login OTP is {otp}. Valid for 5 minutes.",
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{phone_number}"
        )
    
    try:
        await asyncio.to_thread(_send)
        return True
    except Exception as e:
        logger.error("WhatsApp sending failed", extra={"phone": phone_number, "error": str(e)})
        return False

async def check_rate_limit(phone_number: str) -> bool:
    redis_client = await get_redis()
    key = f"rate_limit:otp:{phone_number}"
    # Max 5 per hour
    current = await redis_client.get(key)
    if current and int(current) >= 5:
        return False
    
    pipe = redis_client.pipeline()
    pipe.incr(key)
    if not current:
        pipe.expire(key, timedelta(hours=1))
    await pipe.execute()
    return True

async def send_otp_via_email(email: str, otp: str) -> bool:
    from app.worker.tasks import dispatch
    dispatch(send_email_notification, email, "Your OTP Code", f"Your OTP is: {otp}")
    logger.info("Dispatched email OTP via Celery", extra={"email": email})
    return True

async def check_admin_lockout(email: str) -> bool:
    redis_client = await get_redis()
    key = f"admin_lockout:{email}"
    current = await redis_client.get(key)
    if current and int(current) >= 5:
        return False
    return True

async def increment_admin_lockout(email: str) -> None:
    redis_client = await get_redis()
    key = f"admin_lockout:{email}"
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, timedelta(minutes=15))
    await pipe.execute()

async def reset_admin_lockout(email: str) -> None:
    redis_client = await get_redis()
    key = f"admin_lockout:{email}"
    await redis_client.delete(key)
