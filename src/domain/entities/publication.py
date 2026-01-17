"""Publication entity."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class PublicationStatus(str, Enum):
    """Publication status."""

    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Publication:
    """Represents a published (or pending) news item in Telegram."""

    id: UUID = field(default_factory=uuid4)
    news_item_id: UUID
    status: PublicationStatus = PublicationStatus.PENDING

    telegram_message_id: Optional[int] = None
    telegram_html_text: str = ""

    # Media
    image_urls: list[str] = field(default_factory=list)
    video_urls: list[str] = field(default_factory=list)

    # Hashtags
    hashtags: list[str] = field(default_factory=list)

    # Tracking
    created_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None

    # Error handling
    last_error: Optional[str] = None
    retry_count: int = 0
    next_retry_at: Optional[datetime] = None

    def mark_published(self, message_id: int) -> None:
        """Mark as successfully published."""
        self.status = PublicationStatus.PUBLISHED
        self.telegram_message_id = message_id
        self.published_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        """Mark as failed."""
        self.status = PublicationStatus.FAILED
        self.failed_at = datetime.utcnow()
        self.last_error = error

    def schedule_retry(self, next_retry_at: datetime) -> None:
        """Schedule next retry attempt."""
        self.status = PublicationStatus.RETRYING
        self.next_retry_at = next_retry_at
        self.retry_count += 1
