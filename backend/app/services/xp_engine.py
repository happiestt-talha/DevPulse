from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

LEVEL_THRESHOLDS = [0, 500, 1500, 3500, 7000, 13000, 20000]   # Intern to Legend
LEVEL_TITLES = ["Intern", "Junior Developer", "Mid Developer", "Senior Developer", "Staff Engineer", "Principal Engineer", "Legend"]

def get_level_and_progress(xp: int):
    """Returns (level_index, level_title, xp_to_next_level) where level_index is 1‑based."""
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp < threshold:
            prev = LEVEL_THRESHOLDS[i-1] if i > 0 else 0
            xp_to_next = threshold - xp
            return i, LEVEL_TITLES[i-1], xp_to_next
    # Max level
    return len(LEVEL_THRESHOLDS), LEVEL_TITLES[-1], 0

def recalc_level(user: User) -> bool:
    """Update user.level based on total_xp. Returns True if level changed."""
    new_level, new_title, _ = get_level_and_progress(user.total_xp)
    if new_level != user.level:
        user.level = new_level
        return True
    return False