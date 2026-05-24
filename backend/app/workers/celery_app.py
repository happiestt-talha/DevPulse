from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "devpulse",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.sync_github",
        "app.workers.sync_wakatime",
        "app.workers.sync_leetcode",
        "app.workers.streak_check",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)

# Celery Beat schedule
celery_app.conf.beat_schedule = {
    "sync-all-users-github-hourly": {
        "task": "app.workers.sync_github.sync_all_users_github",
        "schedule": 3600.0,  # every hour
    },
    "sync-all-users-wakatime-6hours": {
        "task": "app.workers.sync_wakatime.sync_all_users_wakatime",
        "schedule": 21600.0,  # every 6 hours
    },
    "sync-all-users-leetcode-hourly": {
        "task": "app.workers.sync_leetcode.sync_all_users_leetcode",
        "schedule": 3600.0,
    },
    "check-streaks-daily": {
        "task": "app.workers.streak_check.check_all_streaks",
        "schedule": 86400.0,   # once per day at 00:00 UTC (Celery beat will run at start of day)
    },
}