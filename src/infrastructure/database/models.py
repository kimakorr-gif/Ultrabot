"""SQLAlchemy ORM models for database."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    INT,
    VARCHAR,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class FeedModel(Base):
    """ORM model for RSS feed source."""

    __tablename__ = "feeds"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(VARCHAR(255), nullable=False, unique=True)
    url = Column(VARCHAR(2048), nullable=False, unique=True)
    enabled = Column(Boolean, default=True, index=True)
    priority_weight = Column(INT, default=5)

    # Tracking
    last_fetch_at = Column(DateTime, default=datetime.utcnow)
    last_fetch_success = Column(Boolean, default=True)
    consecutive_failures = Column(INT, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_feeds_enabled", "enabled"),
        Index("ix_feeds_last_fetch_at", "last_fetch_at"),
    )


class NewsItemModel(Base):
    """ORM model for news item."""

    __tablename__ = "news_items"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    feed_id = Column(PGUUID(as_uuid=True), ForeignKey("feeds.id"), nullable=False)

    # Content
    title_en = Column(Text, nullable=False)
    title_ru = Column(Text, nullable=True)
    content_en = Column(Text, nullable=False)
    content_ru = Column(Text, nullable=True)

    # Deduplication & Scoring
    dedup_hash = Column(VARCHAR(32), nullable=False, unique=True, index=True)
    score = Column(INT, default=0, index=True)

    # Source
    source_url = Column(VARCHAR(2048), nullable=False)
    source_name = Column(VARCHAR(255), nullable=False)
    source_weight = Column(INT, default=5)

    # Media
    image_urls = Column(JSON, default=list)
    video_urls = Column(JSON, default=list)
    hashtags = Column(JSON, default=list)

    # State
    is_published = Column(Boolean, default=False, index=True)
    published_at = Column(DateTime, nullable=True)
    publication_attempts = Column(INT, default=0)

    # Timestamps
    published_at_source = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_news_items_feed_id", "feed_id"),
        Index("ix_news_items_dedup_hash", "dedup_hash"),
        Index("ix_news_items_is_published", "is_published"),
        Index("ix_news_items_score", "score"),
        Index("ix_news_items_created_at", "created_at"),
        UniqueConstraint("dedup_hash", name="uq_news_items_dedup_hash"),
    )


class PublicationModel(Base):
    """ORM model for publication record."""

    __tablename__ = "publications"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    news_item_id = Column(PGUUID(as_uuid=True), ForeignKey("news_items.id"), unique=True, index=True)

    # Telegram
    telegram_message_id = Column(BigInteger, nullable=True, unique=True)
    telegram_html_text = Column(Text, default="")

    # Media
    image_urls = Column(JSON, default=list)
    video_urls = Column(JSON, default=list)
    hashtags = Column(JSON, default=list)

    # Status
    status = Column(
        VARCHAR(20),
        default="pending",
        index=True,
    )  # pending, published, failed, retrying

    # Error handling
    last_error = Column(Text, nullable=True)
    retry_count = Column(INT, default=0)
    next_retry_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_publications_news_item_id", "news_item_id"),
        Index("ix_publications_status", "status"),
        Index("ix_publications_created_at", "created_at"),
        Index("ix_publications_next_retry_at", "next_retry_at"),
    )


class MetricsLogModel(Base):
    """ORM model for metrics logging."""

    __tablename__ = "metrics_logs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    event_type = Column(VARCHAR(50), nullable=False, index=True)
    source = Column(VARCHAR(100), nullable=False)
    duration_ms = Column(INT, nullable=True)
    status = Column(VARCHAR(20), nullable=False)  # success, error, timeout
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("ix_metrics_logs_event_type", "event_type"),
        Index("ix_metrics_logs_timestamp", "timestamp"),
    )


def create_db_engine(database_url: str, **kwargs):
    """Create SQLAlchemy engine.

    Args:
        database_url: Database connection URL
        **kwargs: Additional engine parameters

    Returns:
        SQLAlchemy Engine
    """
    return create_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        **kwargs,
    )


def create_session_factory(engine):
    """Create session factory.

    Args:
        engine: SQLAlchemy Engine

    Returns:
        Session factory
    """
    return sessionmaker(bind=engine, expire_on_commit=False)
