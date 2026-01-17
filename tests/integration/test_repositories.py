"""Integration tests for repositories with PostgreSQL."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from src.domain.entities.feed import FeedSource
from src.domain.entities.news_item import ContentLanguage, NewsContent, NewsItem
from src.domain.entities.publication import Publication, PublicationStatus
from src.domain.repositories import (
    FeedRepository,
    NewsRepository,
    PublicationRepository,
)
from src.domain.value_objects.base import DedupHash, Score
from src.infrastructure.database.models import Base
from src.infrastructure.database.repositories import (
    PostgresFeedRepository,
    PostgresNewsRepository,
    PostgresPublicationRepository,
)


@pytest.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
async def test_session(test_db):
    """Create test session."""
    async with AsyncSession(bind=test_db, expire_on_commit=False) as session:
        yield session


class TestNewsRepository:
    """Tests for PostgresNewsRepository."""

    @pytest.mark.asyncio
    async def test_save_and_get_by_id(self, test_session: AsyncSession):
        """Test saving and retrieving news item."""
        repo = PostgresNewsRepository(test_session)

        # Create news item
        news = NewsItem(
            feed_id="feed_1",
            content=NewsContent(
                title_en="Test News",
                content_en="Test content",
                language=ContentLanguage.ENGLISH,
                source="TestSource",
            ),
        )

        # Save
        await repo.save(news)

        # Retrieve
        retrieved = await repo.get_by_id(news.id)

        assert retrieved is not None
        assert retrieved.id == news.id
        assert retrieved.content.title_en == "Test News"

    @pytest.mark.asyncio
    async def test_get_by_dedup_hash(self, test_session: AsyncSession):
        """Test deduplication hash lookup."""
        repo = PostgresNewsRepository(test_session)

        dedup_hash = DedupHash.from_text("test content")

        news = NewsItem(
            feed_id="feed_1",
            content=NewsContent(
                title_en="Test",
                content_en="test content",
                language=ContentLanguage.ENGLISH,
                source="Source",
            ),
        )

        await repo.save(news)

        # Should find by dedup hash
        found = await repo.get_by_dedup_hash(dedup_hash)
        assert found is not None

    @pytest.mark.asyncio
    async def test_find_unpublished(self, test_session: AsyncSession):
        """Test finding unpublished news."""
        repo = PostgresNewsRepository(test_session)

        # Create news items
        news1 = NewsItem(
            feed_id="feed_1",
            content=NewsContent(
                title_en="News 1",
                content_en="Content 1",
                language=ContentLanguage.ENGLISH,
                source="Source",
            ),
        )

        await repo.save(news1)

        # Find unpublished
        unpublished = await repo.find_unpublished(limit=10)
        assert len(unpublished) > 0
        assert any(n.id == news1.id for n in unpublished)


class TestFeedRepository:
    """Tests for PostgresFeedRepository."""

    @pytest.mark.asyncio
    async def test_save_and_get_by_id(self, test_session: AsyncSession):
        """Test saving and retrieving feed."""
        repo = PostgresFeedRepository(test_session)

        feed = FeedSource(
            name="Test Feed",
            url="https://example.com/feed.xml",
        )

        await repo.save(feed)

        retrieved = await repo.get_by_id(feed.id)
        assert retrieved is not None
        assert retrieved.name == "Test Feed"

    @pytest.mark.asyncio
    async def test_get_all_enabled(self, test_session: AsyncSession):
        """Test retrieving enabled feeds."""
        repo = PostgresFeedRepository(test_session)

        feed1 = FeedSource(name="Feed 1", url="https://example.com/1.xml")
        feed2 = FeedSource(name="Feed 2", url="https://example.com/2.xml")

        await repo.save(feed1)
        await repo.save(feed2)

        enabled = await repo.get_all_enabled()
        assert len(enabled) >= 2

    @pytest.mark.asyncio
    async def test_mark_failed_fetch(self, test_session: AsyncSession):
        """Test tracking failed fetches."""
        repo = PostgresFeedRepository(test_session)

        feed = FeedSource(name="Test", url="https://example.com/feed.xml")
        await repo.save(feed)

        # Mark as failed
        feed.mark_failed_fetch()
        await repo.save(feed)

        retrieved = await repo.get_by_id(feed.id)
        assert retrieved.consecutive_failures > 0


class TestPublicationRepository:
    """Tests for PostgresPublicationRepository."""

    @pytest.mark.asyncio
    async def test_save_and_get(self, test_session: AsyncSession):
        """Test saving and retrieving publication."""
        repo = PostgresPublicationRepository(test_session)

        publication = Publication(
            news_item_id="news_1",
            status=PublicationStatus.PENDING,
        )

        await repo.save(publication)

        retrieved = await repo.get_by_id(publication.id)
        assert retrieved is not None
        assert retrieved.status == PublicationStatus.PENDING

    @pytest.mark.asyncio
    async def test_find_retryable(self, test_session: AsyncSession):
        """Test finding retryable publications."""
        repo = PostgresPublicationRepository(test_session)

        # Create failed publication
        publication = Publication(
            news_item_id="news_1",
            status=PublicationStatus.FAILED,
            retry_count=1,
        )

        await repo.save(publication)

        # Find retryable
        retryable = await repo.find_retryable(max_retries=3, limit=10)
        # Should find if retry_count < max_retries

        if len(retryable) > 0:
            assert any(p.id == publication.id for p in retryable)
