"""Initial migration - create all tables and enable pg_trgm

Revision ID: 0001_initial
Revises: 
Create Date: 2026-06-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pg_trgm extension for fuzzy search
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')

    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verification_token', sa.String(length=255), nullable=True),
        sa.Column('refresh_token', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Anime table
    op.create_table(
        'anime',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mal_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('title_english', sa.String(length=512), nullable=True),
        sa.Column('synopsis', sa.Text(), nullable=True),
        sa.Column('cover_image_url', sa.String(length=1024), nullable=False),
        sa.Column('genres', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('simple_avg', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('bayesian_avg', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('vote_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_anime_mal_id', 'anime', ['mal_id'], unique=True)

    # GIN indexes for fuzzy search using pg_trgm
    op.execute("CREATE INDEX ix_anime_title_trgm ON anime USING gin (title gin_trgm_ops)")
    op.execute("CREATE INDEX ix_anime_title_english_trgm ON anime USING gin (title_english gin_trgm_ops)")

    # Ratings table
    op.create_table(
        'ratings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('anime_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['anime_id'], ['anime.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'anime_id', name='uq_user_anime_rating'),
    )
    op.create_index('ix_ratings_user_id', 'ratings', ['user_id'])
    op.create_index('ix_ratings_anime_id', 'ratings', ['anime_id'])


def downgrade() -> None:
    op.drop_table('ratings')
    op.drop_table('anime')
    op.drop_table('users')
    op.execute('DROP EXTENSION IF EXISTS pg_trgm')
