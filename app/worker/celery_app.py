from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

from celery.schedules import crontab

celery_app.conf.task_routes = {
    "app.worker.tasks.*": "main-queue"
}

celery_app.conf.beat_schedule = {
    "reconcile-payments-nightly": {
        "task": "app.worker.tasks.reconcile_payments",
        "schedule": crontab(hour=2, minute=0), # 2 AM every day
    }
}
