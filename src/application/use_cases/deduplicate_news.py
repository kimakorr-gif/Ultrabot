"""Deduplicate news use case."""

from dataclasses import dataclass

from src.application.use_cases.base import UseCase
from src.core.logger import get_logger
from src.core.metrics import NEWS_DEDUPLICATED_TOTAL
from src.domain.entities.news_item import NewsItem
from src.domain.repositories import NewsRepository

logger = get_logger(__name__)


@dataclass
class DeduplicateNewsResult:
    """Result of deduplication operation."""

    success: bool
    is_duplicate: bool = False
    existing_news_id: str | None = None
    error: str | None = None


class DeduplicateNewsUseCase(UseCase):
    """Check for duplicate news items and cleanup old ones."""

    def __init__(self, news_repository: NewsRepository) -> None:
        """Initialize use case.

        Args:
            news_repository: Repository for accessing news data
        """
        self.news_repository = news_repository

    async def execute(self, news_item: NewsItem) -> DeduplicateNewsResult:
        """Check if news is duplicate and cleanup old entries.

        Args:
            news_item: News item to check for duplicates

        Returns:
            DeduplicateNewsResult with duplicate status

        Raises:
            Exception: If deduplication check fails
        """
        try:
            # Get dedup hash
            dedup_hash = news_item.metadata.dedup_hash

            # Check if already exists
            existing = await self.news_repository.get_by_dedup_hash(dedup_hash)

            if existing:
                logger.warning(
                    "Duplicate news detected",
                    extra={
                        "news_id": news_item.id,
                        "existing_id": existing.id,
                        "dedup_hash": str(dedup_hash),
                    },
                )

                NEWS_DEDUPLICATED_TOTAL.labels(
                    action="duplicate_detected"
                ).inc()

                return DeduplicateNewsResult(
                    success=True,
                    is_duplicate=True,
                    existing_news_id=existing.id,
                )

            # Cleanup old news (older than configured days)
            # This is handled by a separate cleanup job, not here
            # But we track that this item is new
            logger.info(
                "News is unique",
                extra={
                    "news_id": news_item.id,
                    "dedup_hash": str(dedup_hash),
                },
            )

            NEWS_DEDUPLICATED_TOTAL.labels(
                action="new_item"
            ).inc()

            return DeduplicateNewsResult(
                success=True,
                is_duplicate=False,
            )

        except Exception as e:
            error_msg = f"Deduplication check failed: {str(e)}"

            logger.error(
                error_msg,
                extra={"news_id": news_item.id},
                exc_info=True,
            )

            NEWS_DEDUPLICATED_TOTAL.labels(
                action="error"
            ).inc()

            return DeduplicateNewsResult(
                success=False,
                error=error_msg,
            )

    async def cleanup_old_news(self, days: int = 30) -> dict[str, int]:
        """Clean up old news items from database.

        Args:
            days: Delete news older than N days (default: 30)

        Returns:
            Dictionary with cleanup statistics
        """
        try:
            deleted_count = await self.news_repository.cleanup_old(days=days)

            logger.info(
                "Cleaned up old news",
                extra={
                    "days": days,
                    "deleted_count": deleted_count,
                },
            )

            return {
                "success": True,
                "deleted_count": deleted_count,
            }

        except Exception as e:
            error_msg = f"Cleanup failed: {str(e)}"

            logger.error(
                error_msg,
                exc_info=True,
            )

            return {
                "success": False,
                "deleted_count": 0,
                "error": error_msg,
            }
