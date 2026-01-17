"""NewsItem entity - represents a news article."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class ContentLanguage(str, Enum):
    """Supported content languages."""

    EN = "en"
    RU = "ru"


@dataclass
class NewsContent:
    """News content with original and translated versions."""

    original_title: str
    original_content: str
    original_language: ContentLanguage = ContentLanguage.EN

    translated_title: Optional[str] = None
    translated_content: Optional[str] = None
    translated_language: Optional[ContentLanguage] = None

    def is_translated(self) -> bool:
        """Check if content is translated."""
        return self.translated_title is not None and self.translated_content is not None


@dataclass
class NewsMetadata:
    """Metadata for a news item."""

    source_url: str
    source_name: str
    published_at: datetime
    fetched_at: datetime = field(default_factory=datetime.utcnow)

    # Scoring
    score: int = 0
    keyword_matches: dict[str, int] = field(default_factory=dict)
    source_weight: int = 5

    # Deduplication
    dedup_hash: Optional[str] = None


@dataclass
class NewsItem:
    """Domain entity for news item."""

    id: UUID = field(default_factory=uuid4)
    content: NewsContent
    metadata: NewsMetadata

    # Media
    image_urls: list[str] = field(default_factory=list)
    video_urls: list[str] = field(default_factory=list)

    # Tags and categorization
    hashtags: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)

    # State
    is_published: bool = False
    published_at: Optional[datetime] = None
    publication_attempts: int = 0

    def calculate_score(self) -> int:
        """Calculate relevance score."""
        score = self.metadata.score
        score += self.metadata.source_weight

        # Bonus for fresh news (<15 min)
        age_minutes = (datetime.utcnow() - self.metadata.published_at).total_seconds() / 60
        if age_minutes < 15:
            score += 5

        return score

    def mark_published(self, telegram_message_id: Optional[int] = None) -> None:
        """Mark news as published."""
        self.is_published = True
        self.published_at = datetime.utcnow()

    def increment_publication_attempts(self) -> None:
        """Track failed publication attempts."""
        self.publication_attempts += 1

    def __hash__(self) -> int:
        """Hash based on dedup_hash."""
        if self.metadata.dedup_hash:
            return hash(self.metadata.dedup_hash)
        return hash(self.id)
