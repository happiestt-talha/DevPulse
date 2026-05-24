from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.stats import GitHubStats, WakaTimeStats, LeetCodeStats
from app.services.score_engine import calculate_developer_score

async def update_user_score(user_id: str):
    async with AsyncSessionLocal() as db:
        # Fetch user and all stats
        user_stmt = select(User).where(User.id == user_id)
        user_res = await db.execute(user_stmt)
        user = user_res.scalar_one()
        github_stmt = select(GitHubStats).where(GitHubStats.user_id == user_id).order_by(GitHubStats.synced_at.desc())
        github_res = await db.execute(github_stmt)
        github = github_res.scalar_one_or_none()
        waka_stmt = select(WakaTimeStats).where(WakaTimeStats.user_id == user_id).order_by(WakaTimeStats.synced_at.desc())
        waka_res = await db.execute(waka_stmt)
        wakatime = waka_res.scalar_one_or_none()
        leet_stmt = select(LeetCodeStats).where(LeetCodeStats.user_id == user_id).order_by(LeetCodeStats.synced_at.desc())
        leet_res = await db.execute(leet_stmt)
        leetcode = leet_res.scalar_one_or_none()
        new_score = calculate_developer_score(user, github, wakatime, leetcode)
        user.developer_score = new_score
        db.add(user)
        await db.commit()
