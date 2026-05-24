import asyncio
import json
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.stats import GitHubStats, WakaTimeStats, LeetCodeStats
from app.models.user import User

async def run():
    async with AsyncSessionLocal() as db:
        users_result = await db.execute(select(User))
        users = users_result.scalars().all()
        
        print("\n--- USERS ---")
        for u in users:
            print(f"User: {u.github_username} | XP: {u.total_xp} | Score: {u.developer_score} | Level: {u.level}")

        print("\n--- GITHUB STATS ---")
        gh_result = await db.execute(select(GitHubStats))
        gh_stats = gh_result.scalars().all()
        for s in gh_stats:
            print(f"User ID: {s.user_id}")
            print(f"  Total Commits: {s.total_commits}")
            print(f"  30-day Commits: {s.commits_30d}")
            print(f"  Total PRs Merged: {s.total_prs_merged}")
            print(f"  Top Languages: {s.top_languages}")
            print(f"  Synced At: {s.synced_at}")
            
        print("\n--- WAKATIME STATS ---")
        wk_result = await db.execute(select(WakaTimeStats))
        wk_stats = wk_result.scalars().all()
        if not wk_stats:
            print("  (No WakaTime stats yet)")
        for w in wk_stats:
            print(f"User ID: {w.user_id}")
            print(f"  Today Seconds: {w.today_seconds}")
            
        print("\n--- LEETCODE STATS ---")
        lc_result = await db.execute(select(LeetCodeStats))
        lc_stats = lc_result.scalars().all()
        if not lc_stats:
            print("  (No LeetCode stats yet)")
        for l in lc_stats:
            print(f"User ID: {l.user_id}")
            print(f"  Total Solved: {l.total_solved}")

if __name__ == "__main__":
    asyncio.run(run())
