import asyncio
from datetime import date, datetime, timezone, timedelta
from celery import shared_task
from sqlalchemy import select, update
from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.stats import GitHubStats, WakaTimeStats, LeetCodeStats
import logging

logger = logging.getLogger(__name__)

async def _check_user_streak(user_id: str):
    async with AsyncSessionLocal() as db:
        user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date()
        # Check if user had activity yesterday
        # Activity defined as: any commit (GitHubStats.commits_30d > 0 on that date) OR coding minute (WakaTime) OR LeetCode submission
        # For simplicity, we'll rely on last_synced_at and compare with contribution_data
        # We'll assume the sync tasks populate a "last_activity_date" column; but spec doesn't have it.
        # Alternative: query the stats tables for yesterday's activity.
        # Let's implement a helper that looks at contribution_data JSON.
        # For now, we'll use a simpler method: if user.last_synced_at is yesterday and there is any data for that day.
        # But to be accurate, we'll check GitHubStats.contribution_data.
        github = (await db.execute(select(GitHubStats).where(GitHubStats.user_id == user_id).order_by(GitHubStats.synced_at.desc()))).scalar_one_or_none()
        wakatime = (await db.execute(select(WakaTimeStats).where(WakaTimeStats.user_id == user_id).order_by(WakaTimeStats.synced_at.desc()))).scalar_one_or_none()
        leetcode = (await db.execute(select(LeetCodeStats).where(LeetCodeStats.user_id == user_id).order_by(LeetCodeStats.synced_at.desc()))).scalar_one_or_none()

        active = False
        if github and github.contribution_data:
            for day in github.contribution_data:
                if day["date"] == yesterday.isoformat() and day["count"] > 0:
                    active = True
                    break
        if not active and wakatime and wakatime.daily_breakdown:
            for day in wakatime.daily_breakdown:
                if day["date"] == yesterday.isoformat() and day["seconds"] > 0:
                    active = True
                    break
        if not active and leetcode and leetcode.recent_submissions:
            for sub in leetcode.recent_submissions:
                sub_date = datetime.fromtimestamp(sub["timestamp"], tz=timezone.utc).date()
                if sub_date == yesterday:
                    active = True
                    break

        # Update streak
        if active:
            user.streak_current += 1
            if user.streak_current > user.streak_longest:
                user.streak_longest = user.streak_current
            user.streak_last_date = yesterday
        else:
            if user.streak_freezes > 0:
                # Auto-apply freeze
                user.streak_freezes -= 1
                logger.info(f"Applied streak freeze for user {user_id}, streak {user.streak_current} preserved")
            else:
                user.streak_current = 0
                user.streak_last_date = None
        await db.commit()

@celery_app.task
def check_all_streaks():
    async def _check():
        async with AsyncSessionLocal() as db:
            users = (await db.execute(select(User))).scalars().all()
        for user in users:
            await _check_user_streak(str(user.id))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_check())