from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
from datetime import datetime
from app.models.base import Base

class Badge(Base):
    __tablename__ = "badges"

    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False)
    icon_url: Mapped[str] = mapped_column(String(500), nullable=True)   # will be populated later
    color: Mapped[str] = mapped_column(String(7), nullable=True)        # hex, e.g. "#7C3AED"
    category: Mapped[str] = mapped_column(String(50), nullable=False)   # 'streak', 'github', 'wakatime', 'leetcode', 'special'


class UserBadge(Base):
    __tablename__ = "user_badges"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_id: Mapped[UUID] = mapped_column(ForeignKey("badges.id", ondelete="CASCADE"), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class XPEvent(Base):
    __tablename__ = "xp_events"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)   # 'badge', 'streak', 'challenge', 'commit', 'problem'
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Challenge(Base):
    __tablename__ = "challenges"

    week_start: Mapped[datetime] = mapped_column(nullable=False)   # Monday of the week (UTC)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    target_metric: Mapped[str] = mapped_column(String(50), nullable=False)   # 'commits', 'coding_hours', 'problems_solved'
    target_value: Mapped[int] = mapped_column(Integer, nullable=False)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False)
    freeze_reward: Mapped[int] = mapped_column(Integer, default=1)   # number of streak freezes awarded on completion


class UserChallenge(Base):
    __tablename__ = "user_challenges"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    challenge_id: Mapped[UUID] = mapped_column(ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    current_value: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(default=False)
    completed_at: Mapped[datetime] = mapped_column(nullable=True)