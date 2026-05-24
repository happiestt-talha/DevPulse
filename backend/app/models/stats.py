from typing import Optional, Any
from sqlalchemy import ForeignKey, Integer, String, JSON, BigInteger, Float, Date
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID
from datetime import datetime, date
from app.models.base import Base

class GitHubStats(Base):
    __tablename__ = "github_stats"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    synced_at: Mapped[datetime] = mapped_column(nullable=False)

    # Lifetime
    total_commits: Mapped[int] = mapped_column(Integer, default=0)
    total_prs_merged: Mapped[int] = mapped_column(Integer, default=0)
    total_issues_closed: Mapped[int] = mapped_column(Integer, default=0)
    total_stars_earned: Mapped[int] = mapped_column(Integer, default=0)
    top_languages: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)  # list of {language, percent}

    # Last 30 days
    commits_30d: Mapped[int] = mapped_column(Integer, default=0)
    prs_merged_30d: Mapped[int] = mapped_column(Integer, default=0)
    reviews_given_30d: Mapped[int] = mapped_column(Integer, default=0)
    active_repos_30d: Mapped[int] = mapped_column(Integer, default=0)

    # Behavioral
    most_active_day: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    most_active_hour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    contribution_data: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)  # [{date, count}]


class WakaTimeStats(Base):
    __tablename__ = "wakatime_stats"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    synced_at: Mapped[datetime] = mapped_column(nullable=False)

    total_seconds: Mapped[int] = mapped_column(BigInteger, default=0)
    today_seconds: Mapped[int] = mapped_column(Integer, default=0)
    week_seconds: Mapped[int] = mapped_column(Integer, default=0)

    languages: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)   # [{name, percent}]
    projects: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)    # [{name, hours}]
    editors: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)     # [{name, percent}]
    daily_breakdown: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)  # [{date, seconds}]

    best_day_seconds: Mapped[int] = mapped_column(Integer, default=0)
    best_day_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)


class LeetCodeStats(Base):
    __tablename__ = "leetcode_stats"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    synced_at: Mapped[datetime] = mapped_column(nullable=False)

    total_solved: Mapped[int] = mapped_column(Integer, default=0)
    easy_solved: Mapped[int] = mapped_column(Integer, default=0)
    medium_solved: Mapped[int] = mapped_column(Integer, default=0)
    hard_solved: Mapped[int] = mapped_column(Integer, default=0)

    acceptance_rate: Mapped[float] = mapped_column(Float, default=0.0)
    total_submissions: Mapped[int] = mapped_column(Integer, default=0)

    ranking: Mapped[int] = mapped_column(Integer, default=0)
    ranking_percentile: Mapped[float] = mapped_column(Float, default=0.0)

    top_languages: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)   # [{lang, problems}]
    recent_submissions: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)  # list of {title, status, timestamp, lang}
    activity_calendar: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)    # [{timestamp, submissionCount}]

    contest_rating: Mapped[float] = mapped_column(Float, default=0.0)