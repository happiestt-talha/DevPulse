from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.redis import redis_client
from app.models.user import User
from app.models.stats import GitHubStats, WakaTimeStats, LeetCodeStats
import json
from datetime import datetime, timezone

router = APIRouter()

async def get_current_user_id(request: Request, db: AsyncSession) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401)
    token = auth_header.split(" ")[1]
    from app.core.auth import decode_token
    payload = decode_token(token)
    return payload["sub"]

@router.get("/github")
async def get_github_stats(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await get_current_user_id(request, db)
    # Try cache
    cache_key = f"dashboard:github:{user_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    # Query DB
    stmt = select(GitHubStats).where(GitHubStats.user_id == user_id).order_by(GitHubStats.synced_at.desc())
    result = await db.execute(stmt)
    stats = result.scalar_one_or_none()
    if not stats:
        # No stats yet – trigger sync (async via Celery)
        from app.workers.sync_github import sync_github_for_user
        user_stmt = select(User).where(User.id == user_id)
        user_res = await db.execute(user_stmt)
        user = user_res.scalar_one()
        sync_github_for_user.delay(str(user.id), user.github_token, user.github_username)
        raise HTTPException(status_code=202, detail="Sync started, please retry in a few seconds")
    response_data = {
        "total_commits": stats.total_commits,
        "total_prs_merged": stats.total_prs_merged,
        "total_issues_closed": stats.total_issues_closed,
        "total_stars_earned": stats.total_stars_earned,
        "top_languages": stats.top_languages,
        "commits_30d": stats.commits_30d,
        "prs_merged_30d": stats.prs_merged_30d,
        "reviews_given_30d": stats.reviews_given_30d,
        "active_repos_30d": stats.active_repos_30d,
        "most_active_day": stats.most_active_day,
        "most_active_hour": stats.most_active_hour,
        "contribution_data": stats.contribution_data,
        "synced_at": stats.synced_at.isoformat(),
    }
    await redis_client.setex(cache_key, 3600, json.dumps(response_data))
    return response_data

@router.get("/overview")
async def get_overview(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await get_current_user_id(request, db)
    cache_key = f"dashboard:overview:{user_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    # Get user
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one()
    # Fetch latest stats
    github = await db.execute(select(GitHubStats).where(GitHubStats.user_id == user_id).order_by(GitHubStats.synced_at.desc()))
    github_stats = github.scalar_one_or_none()
    wakatime = await db.execute(select(WakaTimeStats).where(WakaTimeStats.user_id == user_id).order_by(WakaTimeStats.synced_at.desc()))
    wakatime_stats = wakatime.scalar_one_or_none()
    leetcode = await db.execute(select(LeetCodeStats).where(LeetCodeStats.user_id == user_id).order_by(LeetCodeStats.synced_at.desc()))
    leetcode_stats = leetcode.scalar_one_or_none()

    problems_solved_today = 0
    if leetcode_stats and leetcode_stats.recent_submissions:
        today_date = datetime.now(timezone.utc).date()
        for sub in leetcode_stats.recent_submissions:
            try:
                sub_date = datetime.fromtimestamp(int(sub.get("timestamp", 0)), tz=timezone.utc).date()
                if sub_date == today_date:
                    problems_solved_today += 1
            except:
                pass

    response = {
        "developer_score": user.developer_score,
        "streak_current": user.streak_current,
        "streak_longest": user.streak_longest,
        "level": user.level,
        "total_xp": user.total_xp,
        "weekly_goal_hours": user.weekly_goal_hours,
        "weekly_goal_problems": user.weekly_goal_problems,
        "today": {
            "commits": github_stats.commits_30d if github_stats else 0,  # approximate
            "coding_minutes": (wakatime_stats.today_seconds // 60) if wakatime_stats else 0,
            "problems_solved": problems_solved_today
        }
    }
    await redis_client.setex(cache_key, 3600, json.dumps(response))
    return response


@router.get("/wakatime")
async def get_wakatime_stats(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await get_current_user_id(request, db)
    cache_key = f"dashboard:wakatime:{user_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    stmt = select(WakaTimeStats).where(WakaTimeStats.user_id == user_id).order_by(WakaTimeStats.synced_at.desc())
    result = await db.execute(stmt)
    stats = result.scalar_one_or_none()
    if not stats:
        # Trigger sync if never synced
        user_stmt = select(User).where(User.id == user_id)
        user_res = await db.execute(user_stmt)
        user = user_res.scalar_one()
        if user.wakatime_token:
            from app.workers.sync_wakatime import sync_wakatime_for_user
            sync_wakatime_for_user.delay(str(user.id), user.wakatime_token)
        raise HTTPException(status_code=202, detail="Sync started, please retry")
    response = {
        "total_seconds": stats.total_seconds,
        "today_seconds": stats.today_seconds,
        "week_seconds": stats.week_seconds,
        "languages": stats.languages,
        "projects": stats.projects,
        "editors": stats.editors,
        "daily_breakdown": stats.daily_breakdown,
        "best_day_seconds": stats.best_day_seconds,
        "best_day_date": stats.best_day_date.isoformat() if stats.best_day_date else None,
        "synced_at": stats.synced_at.isoformat(),
    }
    await redis_client.setex(cache_key, 3600, json.dumps(response))
    return response


@router.get("/leetcode")
async def get_leetcode_stats(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await get_current_user_id(request, db)
    cache_key = f"dashboard:leetcode:{user_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    stmt = select(LeetCodeStats).where(LeetCodeStats.user_id == user_id).order_by(LeetCodeStats.synced_at.desc())
    result = await db.execute(stmt)
    stats = result.scalar_one_or_none()
    if not stats:
        user_stmt = select(User).where(User.id == user_id)
        user_res = await db.execute(user_stmt)
        user = user_res.scalar_one()
        if user.leetcode_username:
            from app.workers.sync_leetcode import sync_leetcode_for_user
            sync_leetcode_for_user.delay(str(user.id), user.leetcode_username)
        raise HTTPException(status_code=202, detail="Sync started, please retry")
    response = {
        "total_solved": stats.total_solved,
        "easy_solved": stats.easy_solved,
        "medium_solved": stats.medium_solved,
        "hard_solved": stats.hard_solved,
        "acceptance_rate": stats.acceptance_rate,
        "total_submissions": stats.total_submissions,
        "ranking": stats.ranking,
        "ranking_percentile": stats.ranking_percentile,
        "top_languages": stats.top_languages,
        "recent_submissions": stats.recent_submissions,
        "contest_rating": stats.contest_rating,
        "synced_at": stats.synced_at.isoformat(),
    }
    await redis_client.setex(cache_key, 3600, json.dumps(response))
    return response