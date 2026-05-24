from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.redis import redis_client
from app.models.user import User
from app.models.badges import Badge, UserBadge, XPEvent, Challenge, UserChallenge
from app.services.xp_engine import get_level_and_progress
import json

router = APIRouter()

async def get_current_user_id(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401)
    token = auth_header.split(" ")[1]
    from app.core.auth import decode_token
    payload = decode_token(token)
    return payload["sub"]

@router.get("/badges")
async def get_badges(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await get_current_user_id(request)
    cache_key = f"gamification:badges:{user_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Get all badges
    badges = (await db.execute(select(Badge))).scalars().all()
    # Get earned badge IDs for this user
    earned = await db.execute(select(UserBadge.badge_id).where(UserBadge.user_id == user_id))
    earned_set = {str(bid) for bid in earned.scalars().all()}

    # For locked badges, calculate progress (simplified)
    # For MVP, we'll return hardcoded progress based on user stats.
    # We'll fetch user stats from DB.
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
    from app.models.stats import GitHubStats, WakaTimeStats, LeetCodeStats
    github = (await db.execute(select(GitHubStats).where(GitHubStats.user_id == user_id).order_by(GitHubStats.synced_at.desc()))).scalar_one_or_none()
    wakatime = (await db.execute(select(WakaTimeStats).where(WakaTimeStats.user_id == user_id).order_by(WakaTimeStats.synced_at.desc()))).scalar_one_or_none()
    leetcode = (await db.execute(select(LeetCodeStats).where(LeetCodeStats.user_id == user_id).order_by(LeetCodeStats.synced_at.desc()))).scalar_one_or_none()

    badge_list = []
    for badge in badges:
        earned_flag = str(badge.id) in earned_set
        progress = None
        if not earned_flag:
            # Calculate progress based on badge slug
            slug = badge.slug
            if slug == "first-blood":
                progress = min(100, (github.total_commits if github else 0) * 100)
            elif slug == "on-fire":
                progress = min(100, (user.streak_current / 7) * 100)
            elif slug == "unstoppable":
                progress = min(100, (user.streak_current / 30) * 100)
            elif slug == "century":
                progress = min(100, (leetcode.total_solved / 100) * 100 if leetcode else 0)
            elif slug == "hard-mode":
                progress = min(100, (leetcode.hard_solved / 10) * 100 if leetcode else 0)
            elif slug == "polyglot":
                lang_count = len(github.top_languages) if github and github.top_languages else 0
                progress = min(100, (lang_count / 5) * 100)
            elif slug == "marathon":
                best = wakatime.best_day_seconds / 3600 if wakatime else 0
                progress = min(100, (best / 10) * 100)
            elif slug == "open-source-hero":
                progress = min(100, (github.prs_merged_30d / 5) * 100 if github else 0)
            elif slug == "grinder":
                progress = min(100, (leetcode.total_submissions / 500) * 100 if leetcode else 0)
            elif slug == "full-stack":
                connected = (user.wakatime_token is not None) + (user.leetcode_username is not None) + 1  # +1 for GitHub always
                progress = min(100, (connected / 3) * 100)
            elif slug == "legend":
                progress = min(100, (user.total_xp / 10000) * 100)
            else:
                progress = 0
        badge_list.append({
            "id": str(badge.id),
            "slug": badge.slug,
            "name": badge.name,
            "description": badge.description,
            "xp_reward": badge.xp_reward,
            "color": badge.color,
            "category": badge.category,
            "earned": earned_flag,
            "earned_at": None,   # could query UserBadge.earned_at
            "progress": progress,
        })
    response = {"badges": badge_list}
    await redis_client.setex(cache_key, 3600, json.dumps(response))
    return response

@router.get("/xp")
async def get_xp(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await get_current_user_id(request)
    cache_key = f"gamification:xp:{user_id}"
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
    level, title, xp_to_next = get_level_and_progress(user.total_xp)
    # Get recent XP events
    events = (await db.execute(select(XPEvent).where(XPEvent.user_id == user_id).order_by(XPEvent.created_at.desc()).limit(20))).scalars().all()
    response = {
        "total_xp": user.total_xp,
        "level": level,
        "level_title": title,
        "xp_to_next_level": xp_to_next,
        "recent_events": [{"source": e.source, "amount": e.amount, "description": e.description, "created_at": e.created_at.isoformat()} for e in events],
    }
    await redis_client.setex(cache_key, 3600, json.dumps(response))
    return response

@router.get("/challenges")
async def get_challenges(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await get_current_user_id(request)
    # Get current week's challenge
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    challenge = (await db.execute(select(Challenge).where(Challenge.week_start == start_of_week))).scalar_one_or_none()
    if not challenge:
        return {"challenges": []}
    user_challenge = (await db.execute(select(UserChallenge).where(UserChallenge.user_id == user_id, UserChallenge.challenge_id == challenge.id))).scalar_one_or_none()
    response = {
        "id": str(challenge.id),
        "title": challenge.title,
        "description": challenge.description,
        "target_metric": challenge.target_metric,
        "target_value": challenge.target_value,
        "xp_reward": challenge.xp_reward,
        "freeze_reward": challenge.freeze_reward,
        "current_value": user_challenge.current_value if user_challenge else 0,
        "completed": user_challenge.completed if user_challenge else False,
    }
    return {"challenges": [response]}

@router.post("/streak-freeze")
async def use_streak_freeze(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = await get_current_user_id(request)
    user = (await db.execute(select(User).where(User.id == user_id))).scalar_one()
    if user.streak_freezes <= 0:
        raise HTTPException(status_code=400, detail="No streak freezes available")
    # Apply freeze for today – mark that today should be protected
    # We'll implement by setting a flag or just decrement now; the streak check task will auto-apply if missing.
    # Simpler: just decrement and log. The streak check will see freeze > 0 and preserve streak for missing day.
    user.streak_freezes -= 1
    await db.commit()
    return {"status": "streak freeze applied", "remaining": user.streak_freezes}