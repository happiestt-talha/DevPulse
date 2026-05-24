import asyncio
from celery import shared_task
from sqlalchemy import select
from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.stats import LeetCodeStats
from app.integrations.leetcode_client import LeetCodeClient
from app.services.score_updater import update_user_score
from app.services.challenge_service import update_challenge_progress
from app.services.badge_engine import check_and_award_badges
from app.services.xp_engine import recalc_level
from uuid import UUID
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def _sync_single_user(user_id: str, leetcode_username: str):
    try:
        profile = await LeetCodeClient.get_user_profile(leetcode_username)
        if not profile:
            logger.warning(f"No LeetCode profile found for {leetcode_username}")
            return

        submit_stats = profile.get("submitStats", {})
        ac_submissions = {item["difficulty"]: item["count"] for item in submit_stats.get("acSubmissionNum", [])}
        total_submissions = {item["difficulty"]: item["submissions"] for item in submit_stats.get("totalSubmissionNum", [])}

        total_solved = ac_submissions.get("All", 0)
        easy = ac_submissions.get("Easy", 0)
        medium = ac_submissions.get("Medium", 0)
        hard = ac_submissions.get("Hard", 0)

        # Acceptance rate
        total_ac = sum(ac_submissions.get(d, 0) for d in ["Easy", "Medium", "Hard"])
        total_sub = sum(total_submissions.get(d, 0) for d in ["Easy", "Medium", "Hard"])
        acceptance = (total_ac / total_sub * 100) if total_sub > 0 else 0.0

        ranking = profile.get("profile", {}).get("ranking", 0)

        # Contest ranking
        contest = await LeetCodeClient.get_user_contest_ranking(leetcode_username)
        contest_rating = contest.get("rating", 0.0) if contest else 0.0
        percentile = contest.get("topPercentage", 100.0) if contest else 100.0

        # Recent submissions
        recent = await LeetCodeClient.get_recent_ac_submissions(leetcode_username, 20)

        # Hardcoded top languages – LeetCode doesn't provide this easily; we can omit or approximate.
        top_langs = []  # Will be filled later if needed

        async with AsyncSessionLocal() as db:
            stmt = select(LeetCodeStats).where(LeetCodeStats.user_id == user_id)
            result = await db.execute(stmt)
            lstats = result.scalar_one_or_none()
            if not lstats:
                lstats = LeetCodeStats(user_id=user_id, synced_at=datetime.now(timezone.utc))

            lstats.total_solved = total_solved
            lstats.easy_solved = easy
            lstats.medium_solved = medium
            lstats.hard_solved = hard
            lstats.acceptance_rate = acceptance
            lstats.total_submissions = total_sub
            lstats.ranking = ranking
            lstats.ranking_percentile = percentile
            lstats.top_languages = top_langs
            lstats.recent_submissions = recent
            lstats.contest_rating = contest_rating
            lstats.synced_at = datetime.now(timezone.utc)
            db.add(lstats)
            await db.commit()
            
            # Recalculate and update the user's score
            await update_user_score(user_id)
            
            await update_challenge_progress(UUID(user_id), db, None, None, lstats)
            
            user_stmt = select(User).where(User.id == user_id)
            user_res = await db.execute(user_stmt)
            user = user_res.scalar_one()
            
            await check_and_award_badges(UUID(user_id), db, None, None, lstats, user)
            recalc_level(user)
            await db.commit()
            
            logger.info(f"Synced LeetCode stats for user {leetcode_username}")
    except Exception as e:
        logger.exception(f"Failed to sync LeetCode for {leetcode_username}: {e}")

@celery_app.task(bind=True, max_retries=3)
def sync_leetcode_for_user(self, user_id: str, leetcode_username: str):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_sync_single_user(user_id, leetcode_username))

@celery_app.task
def sync_all_users_leetcode():
    async def _sync_all():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.leetcode_username.isnot(None)))
            users = result.scalars().all()
        for user in users:
            sync_leetcode_for_user.delay(str(user.id), user.leetcode_username)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_sync_all())