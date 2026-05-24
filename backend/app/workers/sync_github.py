import asyncio
from celery import shared_task
from sqlalchemy import select
from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.core.encryption import decrypt_token
from app.core.redis import redis_client
from app.models.user import User
from app.models.stats import GitHubStats
from app.integrations.github_client import GitHubClient
from app.services.score_updater import update_user_score
from app.services.challenge_service import update_challenge_progress
from app.services.badge_engine import check_and_award_badges
from app.services.xp_engine import recalc_level
from uuid import UUID
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def _sync_single_user(user_id: str, github_token_enc: str, github_username: str):
    token = decrypt_token(github_token_enc)
    client = GitHubClient(token)
    try:
        # Fetch data
        lifetime = await client.get_lifetime_stats(github_username)
        events = await client.get_events_stats(github_username)
        calendar = await client.get_contribution_calendar(github_username)

        async with AsyncSessionLocal() as db:
            # Update or create GitHubStats
            stmt = select(GitHubStats).where(GitHubStats.user_id == user_id)
            result = await db.execute(stmt)
            stats = result.scalar_one_or_none()
            if not stats:
                stats = GitHubStats(user_id=user_id, synced_at=datetime.now(timezone.utc).replace(tzinfo=None))
            # Fill fields
            stats.total_commits = lifetime["total_commits"]
            stats.total_prs_merged = lifetime["total_prs_merged"]
            stats.total_issues_closed = lifetime["total_issues_closed"]
            stats.total_stars_earned = lifetime["total_stars_earned"]
            stats.top_languages = lifetime["top_languages"]
            stats.commits_30d = events["commits_30d"]
            stats.prs_merged_30d = events["prs_merged_30d"]
            stats.reviews_given_30d = events["reviews_given_30d"]
            stats.active_repos_30d = events["active_repos_30d"]
            stats.contribution_data = calendar
            stats.synced_at = datetime.now(timezone.utc).replace(tzinfo=None)
            db.add(stats)

            # Update user last_synced_at
            user_stmt = select(User).where(User.id == user_id)
            user_res = await db.execute(user_stmt)
            user = user_res.scalar_one()
            user.last_synced_at = datetime.now(timezone.utc).replace(tzinfo=None)
            db.add(user)

            await db.commit()
            
            # Recalculate and update the user's score
            await update_user_score(user_id)
            
            await update_challenge_progress(UUID(user_id), db, stats, None, None)
            
            await check_and_award_badges(UUID(user_id), db, stats, None, None, user)
            recalc_level(user)
            await db.commit()
            
            # Clear cache
            await redis_client.delete(f"dashboard:github:{user_id}")
            await redis_client.delete(f"dashboard:overview:{user_id}")
            
            logger.info(f"Synced GitHub stats for user {github_username}")
    except Exception as e:
        logger.exception(f"Failed to sync GitHub for {github_username}: {e}")

@celery_app.task(bind=True, max_retries=3)
def sync_github_for_user(self, user_id: str, github_token_enc: str, github_username: str):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_sync_single_user(user_id, github_token_enc, github_username))

@celery_app.task
def sync_all_users_github():
    async def _sync_all():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.github_token.isnot(None)))
            users = result.scalars().all()
        for user in users:
            sync_github_for_user.delay(str(user.id), user.github_token, user.github_username)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_sync_all())