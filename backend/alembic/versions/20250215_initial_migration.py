"""initial migration

Revision ID: 20250215_initial
Revises:
Create Date: 2025-02-15 12:00:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250215_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('github_id', sa.BigInteger(), nullable=False),
        sa.Column('github_username', sa.String(length=100), nullable=False),
        sa.Column('github_token', sa.String(length=500), nullable=False),
        sa.Column('github_token_exp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('wakatime_token', sa.String(length=500), nullable=True),
        sa.Column('wakatime_refresh', sa.String(length=500), nullable=True),
        sa.Column('leetcode_username', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('display_name', sa.String(length=200), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('total_xp', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('streak_current', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('streak_longest', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('streak_last_date', sa.Date(), nullable=True),
        sa.Column('streak_freezes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('developer_score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('weekly_goal_hours', sa.Integer(), nullable=False, server_default='20'),
        sa.Column('weekly_goal_problems', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('notify_streak_risk', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notify_badge_unlock', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notify_weekly_digest', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('github_id')
    )
    op.create_table('github_stats',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('synced_at', sa.DateTime(), nullable=False),
        sa.Column('total_commits', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_prs_merged', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_issues_closed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_stars_earned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('top_languages', sa.JSON(), nullable=True),
        sa.Column('commits_30d', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('prs_merged_30d', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reviews_given_30d', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('active_repos_30d', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('most_active_day', sa.String(length=10), nullable=True),
        sa.Column('most_active_hour', sa.Integer(), nullable=True),
        sa.Column('contribution_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_github_stats_user_id'), 'github_stats', ['user_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_github_stats_user_id'), table_name='github_stats')
    op.drop_table('github_stats')
    op.drop_table('users')