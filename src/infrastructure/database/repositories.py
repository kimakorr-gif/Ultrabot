"""Repository implementations using SQLAlchemy."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.logger import get_logger
from ...domain.entities.feed import FeedSource
from ...domain.entities.news_item import ContentLanguage, NewsContent, NewsItem, NewsMetadata
from ...domain.entities.publication import Publication, PublicationStatus
from ...domain.repositories import FeedRepository, NewsRepository, PublicationRepository
from .models import FeedModel, NewsItemModel, PublicationModel

logger = get_logger(__name__)


class PostgresNewsRepository(NewsRepository):
    """PostgreSQL implementation of NewsRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def save(self, news_item: NewsItem) -> None:
        """Save news item to database.

        Args:
            news_item: News item to save
        """
        model = NewsItemModel(
            id=news_item.id,
            feed_id=UUID("00000000-0000-0000-0000-000000000000"),  # TODO: Get from metadata
            title_en=news_item.content.original_title,
            title_ru=news_item.content.translated_title,
            content_en=news_item.content.original_content,
            content_ru=news_item.content.translated_content,
            dedup_hash=news_item.metadata.dedup_hash or "",
            score=news_item.metadata.score,
            source_url=news_item.metadata.source_url,
            source_name=news_item.metadata.source_name,
            source_weight=news_item.metadata.source_weight,
            image_urls=news_item.image_urls,
            video_urls=news_item.video_urls,
            hashtags=news_item.hashtags,
            is_published=news_item.is_published,
            published_at=news_item.published_at,
            published_at_source=news_item.metadata.published_at,
        )

        self.session.add(model)
        await self.session.commit()

    async def get_by_id(self, news_id: UUID) -> Optional[NewsItem]:
        """Get news item by ID.

        Args:
            news_id: News item ID

        Returns:
            News item or None
        """
        result = await self.session.execute(select(NewsItemModel).where(NewsItemModel.id == news_id))
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._model_to_entity(model)

    async def get_by_dedup_hash(self, dedup_hash: str) -> Optional[NewsItem]:
        """Get news item by dedup hash.

        Args:
            dedup_hash: Dedup hash

        Returns:
            News item or None
        """
        result = await self.session.execute(
            select(NewsItemModel).where(NewsItemModel.dedup_hash == dedup_hash)
        )
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._model_to_entity(model)

    async def find_unpublished(self, limit: int = 100) -> list[NewsItem]:
        """Find unpublished news items.

        Args:
            limit: Maximum number of items

        Returns:
            List of unpublished news items
        """
        result = await self.session.execute(
            select(NewsItemModel)
            .where(NewsItemModel.is_published == False)
            .order_by(NewsItemModel.score.desc())
            .limit(limit)
        )
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def cleanup_old(self, days: int = 7) -> int:
        """Delete news older than specified days.

        Args:
            days: Age threshold in days

        Returns:
            Number of deleted items
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        result = await self.session.execute(
            select(NewsItemModel).where(NewsItemModel.created_at < cutoff_date)
        )
        old_items = result.scalars().all()

        for item in old_items:
            await self.session.delete(item)

        await self.session.commit()
        return len(old_items)

    @staticmethod
    def _model_to_entity(model: NewsItemModel) -> NewsItem:
        """Convert model to entity.

        Args:
            model: SQLAlchemy model

        Returns:
            News item entity
        """
        content = NewsContent(
            original_title=model.title_en,
            original_content=model.content_en,
            translated_title=model.title_ru,
            translated_content=model.content_ru,
        )

        metadata = NewsMetadata(
            source_url=model.source_url,
            source_name=model.source_name,
            published_at=model.published_at_source,
            score=model.score,
            source_weight=model.source_weight,
            dedup_hash=model.dedup_hash,
        )

        return NewsItem(
            id=model.id,
            content=content,
            metadata=metadata,
            image_urls=model.image_urls or [],
            video_urls=model.video_urls or [],
            hashtags=model.hashtags or [],
            is_published=model.is_published,
            published_at=model.published_at,
        )


class PostgresFeedRepository(FeedRepository):
    """PostgreSQL implementation of FeedRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def save(self, feed: FeedSource) -> None:
        """Save feed source.

        Args:
            feed: Feed to save
        """
        model = FeedModel(
            id=feed.id,
            name=feed.name,
            url=feed.url,
            enabled=feed.enabled,
            priority_weight=feed.priority_weight,
        )

        self.session.add(model)
        await self.session.commit()

    async def get_by_id(self, feed_id: UUID) -> Optional[FeedSource]:
        """Get feed source by ID.

        Args:
            feed_id: Feed ID

        Returns:
            Feed source or None
        """
        result = await self.session.execute(select(FeedModel).where(FeedModel.id == feed_id))
        model = result.scalar_one_or_none()

        return self._model_to_entity(model) if model else None

    async def get_all_enabled(self) -> list[FeedSource]:
        """Get all enabled feeds.

        Returns:
            List of enabled feeds
        """
        result = await self.session.execute(select(FeedModel).where(FeedModel.enabled == True))
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def update(self, feed: FeedSource) -> None:
        """Update feed source.

        Args:
            feed: Updated feed
        """
        result = await self.session.execute(select(FeedModel).where(FeedModel.id == feed.id))
        model = result.scalar_one_or_none()

        if model:
            model.enabled = feed.enabled
            model.last_fetch_at = feed.last_fetch_at
            model.last_fetch_success = feed.last_fetch_success
            model.consecutive_failures = feed.consecutive_failures
            model.updated_at = datetime.utcnow()

            await self.session.commit()

    @staticmethod
    def _model_to_entity(model: FeedModel) -> FeedSource:
        """Convert model to entity.

        Args:
            model: SQLAlchemy model

        Returns:
            Feed source entity
        """
        return FeedSource(
            id=model.id,
            name=model.name,
            url=model.url,
            enabled=model.enabled,
            priority_weight=model.priority_weight,
            last_fetch_at=model.last_fetch_at,
            last_fetch_success=model.last_fetch_success,
            consecutive_failures=model.consecutive_failures,
        )


class PostgresPublicationRepository(PublicationRepository):
    """PostgreSQL implementation of PublicationRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def save(self, publication: Publication) -> None:
        """Save publication record.

        Args:
            publication: Publication to save
        """
        model = PublicationModel(
            id=publication.id,
            news_item_id=publication.news_item_id,
            telegram_message_id=publication.telegram_message_id,
            telegram_html_text=publication.telegram_html_text,
            image_urls=publication.image_urls,
            video_urls=publication.video_urls,
            hashtags=publication.hashtags,
            status=publication.status.value,
            last_error=publication.last_error,
            retry_count=publication.retry_count,
        )

        self.session.add(model)
        await self.session.commit()

    async def get_by_news_id(self, news_id: UUID) -> Optional[Publication]:
        """Get publication record for news.

        Args:
            news_id: News item ID

        Returns:
            Publication or None
        """
        result = await self.session.execute(
            select(PublicationModel).where(PublicationModel.news_item_id == news_id)
        )
        model = result.scalar_one_or_none()

        return self._model_to_entity(model) if model else None

    async def find_retryable(self, limit: int = 100) -> list[Publication]:
        """Find publications ready for retry.

        Args:
            limit: Maximum number of items

        Returns:
            List of publications ready for retry
        """
        result = await self.session.execute(
            select(PublicationModel)
            .where(
                and_(
                    PublicationModel.status == "retrying",
                    PublicationModel.next_retry_at <= datetime.utcnow(),
                )
            )
            .order_by(PublicationModel.next_retry_at)
            .limit(limit)
        )
        models = result.scalars().all()

        return [self._model_to_entity(model) for model in models]

    async def update(self, publication: Publication) -> None:
        """Update publication record.

        Args:
            publication: Updated publication
        """
        result = await self.session.execute(
            select(PublicationModel).where(PublicationModel.id == publication.id)
        )
        model = result.scalar_one_or_none()

        if model:
            model.status = publication.status.value
            model.telegram_message_id = publication.telegram_message_id
            model.last_error = publication.last_error
            model.retry_count = publication.retry_count
            model.next_retry_at = publication.next_retry_at
            model.published_at = publication.published_at
            model.updated_at = datetime.utcnow()

            await self.session.commit()

    @staticmethod
    def _model_to_entity(model: PublicationModel) -> Publication:
        """Convert model to entity.

        Args:
            model: SQLAlchemy model

        Returns:
            Publication entity
        """
        return Publication(
            id=model.id,
            news_item_id=model.news_item_id,
            status=PublicationStatus(model.status),
            telegram_message_id=model.telegram_message_id,
            telegram_html_text=model.telegram_html_text,
            image_urls=model.image_urls or [],
            video_urls=model.video_urls or [],
            hashtags=model.hashtags or [],
            last_error=model.last_error,
            retry_count=model.retry_count,
            next_retry_at=model.next_retry_at,
        )
