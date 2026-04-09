"""Celery task definitions for background job processing."""

from celery import Celery
from app.config import get_settings

settings = get_settings()

# Initialize Celery app
app = Celery(
    'insightgenie',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@app.task
def example_task(x, y):
    """Example background task."""
    return x + y
