# Alembic Migration Script Template

"""Initial database schema.

Revision ID: 001
Revises: 
Create Date: 2024-01-17 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Run migration upgrades."""
    # Create feeds table
    op.create_table(
        'feeds',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.VARCHAR(255), nullable=False),
        sa.Column('url', sa.VARCHAR(2048), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('priority_weight', sa.INT(), nullable=False, server_default='5'),
        sa.Column('last_fetch_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('last_fetch_success', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('consecutive_failures', sa.INT(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', name='uq_feeds_name'),
        sa.UniqueConstraint('url', name='uq_feeds_url'),
    )
    op.create_index('ix_feeds_enabled', 'feeds', ['enabled'])
    op.create_index('ix_feeds_last_fetch_at', 'feeds', ['last_fetch_at'])

    # Create news_items table
    op.create_table(
        'news_items',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('feed_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title_en', sa.Text(), nullable=False),
        sa.Column('title_ru', sa.Text(), nullable=True),
        sa.Column('content_en', sa.Text(), nullable=False),
        sa.Column('content_ru', sa.Text(), nullable=True),
        sa.Column('dedup_hash', sa.VARCHAR(32), nullable=False),
        sa.Column('score', sa.INT(), nullable=False, server_default='0'),
        sa.Column('source_url', sa.VARCHAR(2048), nullable=False),
        sa.Column('source_name', sa.VARCHAR(255), nullable=False),
        sa.Column('source_weight', sa.INT(), nullable=False, server_default='5'),
        sa.Column('image_urls', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('video_urls', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('hashtags', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('publication_attempts', sa.INT(), nullable=False, server_default='0'),
        sa.Column('published_at_source', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['feed_id'], ['feeds.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('dedup_hash', name='uq_news_items_dedup_hash'),
    )
    op.create_index('ix_news_items_feed_id', 'news_items', ['feed_id'])
    op.create_index('ix_news_items_dedup_hash', 'news_items', ['dedup_hash'])
    op.create_index('ix_news_items_is_published', 'news_items', ['is_published'])
    op.create_index('ix_news_items_score', 'news_items', ['score'])
    op.create_index('ix_news_items_created_at', 'news_items', ['created_at'])

    # Create publications table
    op.create_table(
        'publications',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('news_item_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('telegram_message_id', sa.BigInteger(), nullable=True),
        sa.Column('telegram_html_text', sa.Text(), nullable=False, server_default=''),
        sa.Column('image_urls', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('video_urls', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('hashtags', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('status', sa.VARCHAR(20), nullable=False, server_default='pending'),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.INT(), nullable=False, server_default='0'),
        sa.Column('next_retry_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('failed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['news_item_id'], ['news_items.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('news_item_id', name='uq_publications_news_item_id'),
        sa.UniqueConstraint('telegram_message_id', name='uq_publications_telegram_message_id'),
    )
    op.create_index('ix_publications_news_item_id', 'publications', ['news_item_id'])
    op.create_index('ix_publications_status', 'publications', ['status'])
    op.create_index('ix_publications_created_at', 'publications', ['created_at'])
    op.create_index('ix_publications_next_retry_at', 'publications', ['next_retry_at'])

    # Create metrics_logs table
    op.create_table(
        'metrics_logs',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metric_name', sa.VARCHAR(255), nullable=False),
        sa.Column('metric_value', sa.BigInteger(), nullable=False),
        sa.Column('labels', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_metrics_logs_metric_name', 'metrics_logs', ['metric_name'])
    op.create_index('ix_metrics_logs_timestamp', 'metrics_logs', ['timestamp'])


def downgrade() -> None:
    """Run migration downgrades."""
    op.drop_table('metrics_logs')
    op.drop_table('publications')
    op.drop_table('news_items')
    op.drop_table('feeds')
