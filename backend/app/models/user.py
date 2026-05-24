from typing import Optional
from sqlalchemy import BigInteger, String, Boolean, Integer, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column
import datetime
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    github_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    github_username: Mapped[str] = mapped_column(String(100), nullable=False)
    github_token: Mapped[str] = mapped_column(String(500), nullable=False)  # encrypted
    github_token_exp: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    wakatime_token: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    wakatime_refresh: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    leetcode_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    level: Mapped[int] = mapped_column(Integer, default=1)
    total_xp: Mapped[int] = mapped_column(Integer, default=0)
    streak_current: Mapped[int] = mapped_column(Integer, default=0)
    streak_longest: Mapped[int] = mapped_column(Integer, default=0)
    streak_last_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    streak_freezes: Mapped[int] = mapped_column(Integer, default=0)

    developer_score: Mapped[int] = mapped_column(Integer, default=0)

    weekly_goal_hours: Mapped[int] = mapped_column(Integer, default=20)
    weekly_goal_problems: Mapped[int] = mapped_column(Integer, default=10)

    notify_streak_risk: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_badge_unlock: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_weekly_digest: Mapped[bool] = mapped_column(Boolean, default=True)

    last_synced_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)