import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.stats import GitHubStats, WakaTimeStats, LeetCodeStats
from app.models.badges import Badge, UserBadge, XPEvent

logger = logging.getLogger(__name__)

# Badge definitions as per Section 1.6
BADGE_DEFINITIONS = [
    {"slug": "first-blood", "name": "First Blood", "description": "First commit ever tracked", "xp": 50, "category": "github", "color": "#10B981"},
    {"slug": "on-fire", "name": "On Fire", "description": "7-day GitHub commit streak", "xp": 100, "category": "streak", "color": "#F59E0B"},
    {"slug": "unstoppable", "name": "Unstoppable", "description": "30-day commit streak", "xp": 500, "category": "streak", "color": "#F59E0B"},
    {"slug": "century", "name": "Century", "description": "100 problems solved on LeetCode", "xp": 300, "category": "leetcode", "color": "#06B6D4"},
    {"slug": "hard-mode", "name": "Hard Mode", "description": "10 Hard LeetCode problems solved", "xp": 400, "category": "leetcode", "color": "#EF4444"},
    {"slug": "night-owl", "name": "Night Owl", "description": "50% of coding hours after midnight", "xp": 150, "category": "wakatime", "color": "#A78BFA"},
    {"slug": "early-bird", "name": "Early Bird", "description": "50% of coding hours before 7am", "xp": 150, "category": "wakatime", "color": "#FBBF24"},
    {"slug": "polyglot", "name": "Polyglot", "description": "Active in 5+ programming languages", "xp": 200, "category": "github", "color": "#7C3AED"},
    {"slug": "marathon", "name": "Marathon", "description": "10+ coding hours in a single day", "xp": 250, "category": "wakatime", "color": "#10B981"},
    {"slug": "open-source-hero", "name": "Open Source Hero", "description": "5+ PRs merged in a single month", "xp": 200, "category": "github", "color": "#7C3AED"},
    {"slug": "grinder", "name": "Grinder", "description": "500 total LeetCode submissions", "xp": 350, "category": "leetcode", "color": "#06B6D4"},
    {"slug": "full-stack", "name": "Full Stack", "description": "All 3 integrations connected", "xp": 100, "category": "special", "color": "#7C3AED"},
    {"slug": "legend", "name": "Legend", "description": "Reach 10,000 XP total", "xp": 1000, "category": "special", "color": "#FBBF24"},
]

async def seed_badges(db: AsyncSession):
    """Call this once during startup or migration."""
    for b in BADGE_DEFINITIONS:
        exists = await db.execute(select(Badge).where(Badge.slug == b["slug"]))
        if not exists.scalar_one_or_none():
            badge = Badge(
                slug=b["slug"],
                name=b["name"],
                description=b["description"],
                xp_reward=b["xp"],
                category=b["category"],
                color=b["color"],
            )
            db.add(badge)
    await db.commit()

async def check_and_award_badges(user_id: UUID, db: AsyncSession, github: Optional[GitHubStats], wakatime: Optional[WakaTimeStats], leetcode: Optional[LeetCodeStats], user: User):
    """Check all badge conditions and award any new badges."""
    # Fetch all badges from DB
    badges = (await db.execute(select(Badge))).scalars().all()
    badge_map = {b.slug: b for b in badges}

    # Get already earned badge slugs for this user
    earned = await db.execute(
        select(UserBadge.badge_id).join(Badge).where(UserBadge.user_id == user_id)
    )
    earned_slugs = {badge_map[b_id].slug for b_id in earned.scalars().all() if b_id in badge_map}

    # Condition functions
    conditions = {
        "first-blood": lambda: (github and github.total_commits > 0) and "first-blood" not in earned_slugs,
        "on-fire": lambda: user.streak_current >= 7,
        "unstoppable": lambda: user.streak_current >= 30,
        "century": lambda: leetcode and leetcode.total_solved >= 100,
        "hard-mode": lambda: leetcode and leetcode.hard_solved >= 10,
        "night-owl": lambda: False,  # requires hourly data, implement later
        "early-bird": lambda: False,
        "polyglot": lambda: github and github.top_languages and len(github.top_languages) >= 5,
        "marathon": lambda: wakatime and wakatime.best_day_seconds >= 10 * 3600,
        "open-source-hero": lambda: github and github.prs_merged_30d >= 5,
        "grinder": lambda: leetcode and leetcode.total_submissions >= 500,
        "full-stack": lambda: bool(user.wakatime_token and user.leetcode_username),
        "legend": lambda: user.total_xp >= 10000,
    }

    newly_awarded = []
    for slug, condition in conditions.items():
        if slug in earned_slugs:
            continue
        if condition():
            badge = badge_map.get(slug)
            if badge:
                # Award badge
                user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
                db.add(user_badge)
                # Award XP
                xp_event = XPEvent(
                    user_id=user_id,
                    source="badge",
                    amount=badge.xp_reward,
                    description=f"Awarded badge: {badge.name}"
                )
                db.add(xp_event)
                user.total_xp += badge.xp_reward
                newly_awarded.append(badge)
                logger.info(f"Awarded badge {badge.slug} to user {user_id}")

    await db.commit()
    return newly_awarded   # will be used for push notifications later