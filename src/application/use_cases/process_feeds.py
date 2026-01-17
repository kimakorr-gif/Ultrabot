"""Process RSS feeds use case."""

from logging import getLogger
from typing import Optional

from ...core.exceptions import RSSParsingError
from ...core.metrics import (
    NEWS_PROCESSED_TOTAL,
    NEWS_SCORE_DISTRIBUTION,
    RSS_ENTRIES_COUNT,
    RSS_FETCH_DURATION,
    RSS_FETCH_ERRORS,
)
from ...domain.entities.feed import FeedSource
from ...domain.entities.news_item import ContentLanguage, NewsContent, NewsItem, NewsMetadata
from ...domain.repositories import FeedRepository, NewsRepository
from ...domain.services.scoring_service import ScoringService
from ...domain.value_objects.base import DedupHash
from ..ports import RSSParserPort
from .base import UseCase

logger = getLogger(__name__)


class ProcessFeedsUseCase(UseCase):
    """Use case for processing RSS feeds."""

    def __init__(
        self,
        rss_parser: RSSParserPort,
        feed_repository: FeedRepository,
        news_repository: NewsRepository,
        scoring_service: ScoringService,
        min_score_threshold: int = 8,
    ) -> None:
        """Initialize use case.

        Args:
            rss_parser: RSS parser implementation
            feed_repository: Feed repository
            news_repository: News repository
            scoring_service: Scoring service
            min_score_threshold: Minimum score for publication
        """
        self.rss_parser = rss_parser
        self.feed_repository = feed_repository
        self.news_repository = news_repository
        self.scoring_service = scoring_service
        self.min_score_threshold = min_score_threshold

    async def execute(self, feed: Optional[FeedSource] = None) -> ProcessFeedsResult:
        """Execute feed processing.

        Args:
            feed: Specific feed to process, or None for all enabled feeds

        Returns:
            Processing result
        """
        feeds = [feed] if feed else await self.feed_repository.get_all_enabled()

        total_processed = 0
        total_published = 0
        total_errors = 0

        for feed_source in feeds:
            try:
                processed, published = await self._process_feed(feed_source)
                total_processed += processed
                total_published += published
            except Exception as e:
                logger.error(f"Error processing feed {feed_source.name}: {e}")
                total_errors += 1
                feed_source.mark_failed_fetch()
                await self.feed_repository.update(feed_source)

        return ProcessFeedsResult(
            total_processed=total_processed,
            total_published=total_published,
            total_errors=total_errors,
        )

    async def _process_feed(self, feed_source: FeedSource) -> tuple[int, int]:
        """Process single feed source.

        Args:
            feed_source: Feed to process

        Returns:
            Tuple of (total_processed, total_published)
        """
        import time

        start_time = time.time()

        try:
            # Parse feed
            feed_data = await self.rss_parser.fetch_feed(feed_source.url)
            entries = feed_data.get("entries", [])

            RSS_ENTRIES_COUNT.labels(feed_name=feed_source.name).set(len(entries))

            processed = 0
            published = 0

            # Process each entry
            for entry in entries:
                try:
                    news_item = await self._create_news_item(entry, feed_source)

                    # Check for duplicates
                    existing = await self.news_repository.get_by_dedup_hash(
                        news_item.metadata.dedup_hash or ""
                    )
                    if existing:
                        NEWS_PROCESSED_TOTAL.labels(
                            source=feed_source.name,
                            status="duplicate",
                        ).inc()
                        logger.debug(f"Duplicate news detected: {news_item.content.original_title}")
                        continue

                    # Score news
                    score = self.scoring_service.calculate_score(news_item)
                    news_item.metadata.score = score
                    NEWS_SCORE_DISTRIBUTION.observe(score)

                    # Save to repository
                    await self.news_repository.save(news_item)
                    processed += 1

                    # Check if meets threshold
                    if score >= self.min_score_threshold:
                        published += 1
                        NEWS_PROCESSED_TOTAL.labels(
                            source=feed_source.name,
                            status="ok",
                        ).inc()
                    else:
                        NEWS_PROCESSED_TOTAL.labels(
                            source=feed_source.name,
                            status="filtered",
                        ).inc()

                except Exception as e:
                    logger.warning(f"Error processing entry from {feed_source.name}: {e}")
                    continue

            # Mark successful fetch
            feed_source.mark_successful_fetch()
            await self.feed_repository.update(feed_source)

            # Record metrics
            duration = time.time() - start_time
            RSS_FETCH_DURATION.labels(feed_name=feed_source.name).observe(duration)

            return processed, published

        except RSSParsingError as e:
            logger.error(f"RSS parsing error for {feed_source.name}: {e}")
            RSS_FETCH_ERRORS.labels(
                feed_name=feed_source.name,
                error_type="parse_error",
            ).inc()
            feed_source.mark_failed_fetch()
            await self.feed_repository.update(feed_source)
            raise

    async def _create_news_item(
        self,
        entry: dict,
        feed_source: FeedSource,
    ) -> NewsItem:
        """Create NewsItem from RSS entry.

        Args:
            entry: RSS entry
            feed_source: Source feed

        Returns:
            NewsItem domain object
        """
        import hashlib
        from datetime import datetime

        # Extract content
        title = entry.get("title", "Untitled")
        summary = entry.get("summary", entry.get("description", ""))
        link = entry.get("link", "")
        published_str = entry.get("published", None)

        # Parse published date
        try:
            from email.utils import parsedate_to_datetime

            published_at = parsedate_to_datetime(published_str) if published_str else datetime.utcnow()
        except Exception:
            published_at = datetime.utcnow()

        # Create dedup hash
        dedup_content = f"{title}{summary[:500]}".encode()
        dedup_hash = hashlib.md5(dedup_content).hexdigest()

        # Create content
        content = NewsContent(
            original_title=title,
            original_content=summary,
            original_language=ContentLanguage.EN,
        )

        # Create metadata
        metadata = NewsMetadata(
            source_url=link,
            source_name=feed_source.name,
            published_at=published_at,
            dedup_hash=dedup_hash,
            source_weight=feed_source.priority_weight,
        )

        # Create news item
        news_item = NewsItem(
            content=content,
            metadata=metadata,
        )

        return news_item


class ProcessFeedsResult:
    """Result of feed processing."""

    def __init__(self, total_processed: int, total_published: int, total_errors: int) -> None:
        """Initialize result.

        Args:
            total_processed: Total items processed
            total_published: Items published (met threshold)
            total_errors: Processing errors
        """
        self.total_processed = total_processed
        self.total_published = total_published
        self.total_errors = total_errors

    def __str__(self) -> str:
        """String representation."""
        return (
            f"ProcessFeedsResult(processed={self.total_processed}, "
            f"published={self.total_published}, errors={self.total_errors})"
        )
