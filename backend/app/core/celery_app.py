from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "holiday_planner",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.prediction_tasks",
        "app.tasks.itinerary_tasks",
        "app.tasks.weather_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,  # 1 hour
)
