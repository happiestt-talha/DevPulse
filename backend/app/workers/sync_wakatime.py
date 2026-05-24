import asyncio
from celery import shared_task
from sqlalchemy import select
from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.core.encryption import decrypt_token
from app.models.user import User
from app.models.stats import WakaTimeStats
from app.integrations.wakatime_client import WakaTimeClient
from app.services.score_updater import update_user_score
from app.services.challenge_service import update_challenge_progress
from app.services.badge_engine import check_and_award_badges
from app.services.xp_engine import recalc_level
from uuid import UUID
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def _sync_single_user(user_id: str, wakatime_token_enc: str):
    token = decrypt_token(wakatime_token_enc)
    client = WakaTimeClient(token)

    try:
        # Get all‑time total
        all_time = await client.get_all_time_since_today()
        total_seconds = all_time.get("data", {}).get("total_seconds", 0)

        # Get last 30 days stats
        stats = await client.get_stats("last_30_days")
        data = stats.get("data", {})
        languages = []
        for lang in data.get("languages", []):
            languages.append({"name": lang["name"], "percent": lang["percent"]})
        projects = []
        for proj in data.get("projects", [])[:10]:
            projects.append({"name": proj["name"], "hours": proj.get("hours", 0)})
        editors = []
        for ed in data.get("editors", []):
            editors.append({"name": ed["name"], "percent": ed["percent"]})

        # Today and week seconds
        today_seconds = 0
        week_seconds = 0
        summaries = await client.get_summaries(
            (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d"),
            datetime.now(timezone.utc).strftime("%Y-%m-%d")
        )
        for day in summaries.get("data", []):
            secs = day["grand_total"]["total_seconds"]
            if day["range"]["date"] == datetime.now(timezone.utc).strftime("%Y-%m-%d"):
                today_seconds = secs
            week_seconds += secs

        daily_breakdown = await client.get_daily_breakdown(30)

        best_day = max(daily_breakdown, key=lambda x: x["seconds"]) if daily_breakdown else None

        async with AsyncSessionLocal() as db:
            stmt = select(WakaTimeStats).where(WakaTimeStats.user_id == user_id)
            result = await db.execute(stmt)
            wstats = result.scalar_one_or_none()
            if not wstats:
                wstats = WakaTimeStats(user_id=user_id, synced_at=datetime.now(timezone.utc))

            wstats.total_seconds = total_seconds
            wstats.today_seconds = today_seconds
            wstats.week_seconds = week_seconds
            wstats.languages = languages
            wstats.projects = projects
            wstats.editors = editors
            wstats.daily_breakdown = daily_breakdown
            if best_day:
                wstats.best_day_seconds = best_day["seconds"]
                wstats.best_day_date = best_day["date"]
            wstats.synced_at = datetime.now(timezone.utc)
            db.add(wstats)
            await db.commit()
            
            # Recalculate and update the user's score
            await update_user_score(user_id)
            
            await update_challenge_progress(UUID(user_id), db, None, wstats, None)
            
            user_stmt = select(User).where(User.id == user_id)
            user_res = await db.execute(user_stmt)
            user = user_res.scalar_one()
            
            await check_and_award_badges(UUID(user_id), db, None, wstats, None, user)
            recalc_level(user)
            await db.commit()
            
            logger.info(f"Synced WakaTime stats for user {user_id}")
    except Exception as e:
        logger.exception(f"Failed to sync WakaTime for user {user_id}: {e}")

@celery_app.task(bind=True, max_retries=3)
def sync_wakatime_for_user(self, user_id: str, wakatime_token_enc: str):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_sync_single_user(user_id, wakatime_token_enc))

@celery_app.task
def sync_all_users_wakatime():
    async def _sync_all():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.wakatime_token.isnot(None)))
            users = result.scalars().all()
        for user in users:
            sync_wakatime_for_user.delay(str(user.id), user.wakatime_token)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_sync_all())