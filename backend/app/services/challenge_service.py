from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.badges import Challenge, UserChallenge
from app.models.user import User
from app.models.stats import GitHubStats, WakaTimeStats, LeetCodeStats
from app.services.xp_engine import recalc_level
from uuid import UUID

async def seed_weekly_challenge(db: AsyncSession):
    """Create a challenge for the current week if none exists."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    # Get Monday of current week
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    exists = await db.execute(select(Challenge).where(Challenge.week_start == start_of_week))
    if exists.scalar_one_or_none():
        return
    # Rotate challenges – simple version: alternate between metrics
    week_number = (now - datetime(2025, 1, 1, tzinfo=timezone.utc)).days // 7
    metric = ["commits", "coding_hours", "problems_solved"][week_number % 3]
    if metric == "commits":
        title = "Commit Crusher"
        description = "Make 15 commits this week"
        target = 15
        xp = 150
    elif metric == "coding_hours":
        title = "Code Marathon"
        description = "Code for 20 hours this week"
        target = 20
        xp = 200
    else:
        title = "Problem Solver"
        description = "Solve 10 LeetCode problems this week"
        target = 10
        xp = 150
    challenge = Challenge(
        week_start=start_of_week,
        title=title,
        description=description,
        target_metric=metric,
        target_value=target,
        xp_reward=xp,
        freeze_reward=1,
    )
    db.add(challenge)
    await db.commit()

async def update_challenge_progress(user_id: UUID, db: AsyncSession, github: GitHubStats, wakatime: WakaTimeStats, leetcode: LeetCodeStats):
    """Update progress for current week's challenge."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    challenge = (await db.execute(select(Challenge).where(Challenge.week_start == start_of_week))).scalar_one_or_none()
    if not challenge:
        return
    user_challenge = (await db.execute(select(UserChallenge).where(UserChallenge.user_id == user_id, UserChallenge.challenge_id == challenge.id))).scalar_one_or_none()
    if not user_challenge:
        user_challenge = UserChallenge(user_id=user_id, challenge_id=challenge.id)
        db.add(user_challenge)
    if user_challenge.completed:
        return

    # Calculate current progress based on metric
    if challenge.target_metric == "commits" and github:
        user_challenge.current_value = github.commits_30d   # approximate for this week – ideally track weekly commits separately
    elif challenge.target_metric == "coding_hours" and wakatime:
        user_challenge.current_value = wakatime.week_seconds // 3600
    elif challenge.target_metric == "problems_solved" and leetcode:
        # Count problems solved this week from recent_submissions
        week_submissions = 0
        for sub in leetcode.recent_submissions or []:
            sub_date = datetime.fromtimestamp(sub["timestamp"], tz=timezone.utc)
            if sub_date >= start_of_week:
                week_submissions += 1
        user_challenge.current_value = week_submissions

    if user_challenge.current_value >= challenge.target_value and not user_challenge.completed:
        user_challenge.completed = True
        user_challenge.completed_at = now
        # Award XP and freeze
        user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
        user.total_xp += challenge.xp_reward
        user.streak_freezes += challenge.freeze_reward
        # Record XP event
        from app.models.badges import XPEvent
        event = XPEvent(user_id=user_id, source="challenge", amount=challenge.xp_reward, description=f"Completed weekly challenge: {challenge.title}")
        db.add(event)
        recalc_level(user)
        await db.commit()
        logger.info(f"User {user_id} completed weekly challenge {challenge.title}")
    else:
        await db.commit()