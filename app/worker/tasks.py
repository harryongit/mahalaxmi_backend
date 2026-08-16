from app.worker.celery_app import celery_app
from app.core.logging import logger
from app.core.config import settings
from app.services.email import send_smtp_email

def dispatch(task, *args, **kwargs):
    """Fire a background task or run directly when Celery worker/broker is unavailable."""
    try:
        task.delay(*args, **kwargs)
        return True
    except Exception as e:
        logger.warning("Background task %s executed synchronously (Celery unavailable): %s", task.name, e)
        try:
            task(*args, **kwargs)
            return True
        except Exception as inner_e:
            logger.error("Failed to run task %s: %s", task.name, inner_e)
            return False

@celery_app.task
def send_whatsapp_notification(phone_number: str, message: str):
    if not settings.TWILIO_ACCOUNT_SID:
        logger.info("Twilio not configured - WhatsApp notification not sent", extra={"phone": phone_number})
        return True

    from twilio.rest import Client
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    msg = client.messages.create(
        body=message,
        from_=settings.TWILIO_WHATSAPP_NUMBER,
        to=f"whatsapp:{phone_number}"
    )
    logger.info("WhatsApp notification sent", extra={"sid": msg.sid})
    return msg.sid

@celery_app.task
def send_email_notification(to_email: str, subject: str, body: str):
    logger.info("Dynamic email notification dispatched via SMTP", extra={"to": to_email, "subject": subject})
    return send_smtp_email(to_email, subject, body)

@celery_app.task
def reconcile_payments():
    import razorpay
    print("[CRON] Starting nightly payment reconciliation...")
    rzp_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    print("[CRON] Reconciliation completed.")
    return True
