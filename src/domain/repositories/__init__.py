"""Repository interfaces (Ports)."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from ..entities.feed import FeedSource
from ..entities.news_item import NewsItem
from ..entities.publication import Publication


class NewsRepository(ABC):
    """Port for news item repository."""

    @abstractmethod
    async def save(self, news_item: NewsItem) -> None:
        """Save news item to repository.

        Args:
            news_item: News item to save
        """
        pass

    @abstractmethod
    async def get_by_id(self, news_id: UUID) -> Optional[NewsItem]:
        """Get news item by ID.

        Args:
            news_id: News item ID

        Returns:
            News item or None if not found
        """
        pass

    @abstractmethod
    async def get_by_dedup_hash(self, dedup_hash: str) -> Optional[NewsItem]:
        """Check if news exists by dedup hash.

        Args:
            dedup_hash: Deduplication hash

        Returns:
            News item or None if not found
        """
        pass

    @abstractmethod
    async def find_unpublished(self, limit: int = 100) -> list[NewsItem]:
        """Find unpublished news items.

        Args:
            limit: Maximum number of items to return

        Returns:
            List of unpublished news items
        """
        pass

    @abstractmethod
    async def cleanup_old(self, days: int = 7) -> int:
        """Delete news older than specified days.

        Args:
            days: Age threshold in days

        Returns:
            Number of deleted items
        """
        pass


class FeedRepository(ABC):
    """Port for feed source repository."""

    @abstractmethod
    async def save(self, feed: FeedSource) -> None:
        """Save feed source.

        Args:
            feed: Feed source to save
        """
        pass

    @abstractmethod
    async def get_by_id(self, feed_id: UUID) -> Optional[FeedSource]:
        """Get feed source by ID.

        Args:
            feed_id: Feed ID

        Returns:
            Feed source or None
        """
        pass

    @abstractmethod
    async def get_all_enabled(self) -> list[FeedSource]:
        """Get all enabled feed sources.

        Returns:
            List of enabled feeds
        """
        pass

    @abstractmethod
    async def update(self, feed: FeedSource) -> None:
        """Update feed source.

        Args:
            feed: Updated feed source
        """
        pass


class PublicationRepository(ABC):
    """Port for publication repository."""

    @abstractmethod
    async def save(self, publication: Publication) -> None:
        """Save publication record.

        Args:
            publication: Publication to save
        """
        pass

    @abstractmethod
    async def get_by_news_id(self, news_id: UUID) -> Optional[Publication]:
        """Get publication record for news.

        Args:
            news_id: News item ID

        Returns:
            Publication or None
        """
        pass

    @abstractmethod
    async def find_retryable(self, limit: int = 100) -> list[Publication]:
        """Find publications ready for retry.

        Args:
            limit: Maximum number of items to return

        Returns:
            List of publications ready for retry
        """
        pass

    @abstractmethod
    async def update(self, publication: Publication) -> None:
        """Update publication record.

        Args:
            publication: Updated publication
        """
        pass
