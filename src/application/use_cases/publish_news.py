"""Publish news use case."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from src.application.use_cases.base import UseCase
from src.core.logger import get_logger
from src.core.metrics import TELEGRAM_PUBLISH_DURATION, TELEGRAM_PUBLISH_ERRORS
from src.domain.entities.news_item import NewsItem
from src.domain.entities.publication import Publication, PublicationStatus
from src.domain.repositories import PublicationRepository
from src.infrastructure.external.telegram_client import TelegramClientAdapter

logger = get_logger(__name__)


class PublicationStrategy(str, Enum):
    """Publication strategy."""

    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    QUEUED = "queued"


@dataclass
class PublishNewsResult:
    """Result of publication operation."""

    success: bool
    publication_id: str | None = None
    message_id: int | None = None
    status: PublicationStatus | None = None
    error: str | None = None
    duration_seconds: float = 0.0
    retry_count: int = 0


class PublishNewsUseCase(UseCase):
    """Publish news item to Telegram channel."""

    def __init__(
        self,
        telegram_client: TelegramClientAdapter,
        publication_repository: PublicationRepository,
        strategy: PublicationStrategy = PublicationStrategy.DELAYED,
        delay_seconds: int = 600,
        max_retries: int = 3,
    ) -> None:
        """Initialize use case.

        Args:
            telegram_client: Telegram client adapter
            publication_repository: Publication repository
            strategy: Publication strategy (immediate, delayed, queued)
            delay_seconds: Delay before publishing (for DELAYED strategy)
            max_retries: Maximum retry attempts on failure
        """
        self.telegram_client = telegram_client
        self.publication_repository = publication_repository
        self.strategy = strategy
        self.delay_seconds = delay_seconds
        self.max_retries = max_retries

    async def execute(self, news_item: NewsItem) -> PublishNewsResult:
        """Publish news item to Telegram.

        Args:
            news_item: News item to publish

        Returns:
            PublishNewsResult with publication details

        Raises:
            Exception: If publication fails after retries
        """
        import time

        start_time = time.time()

        try:
            # Create publication record
            publication = Publication(
                news_item_id=news_item.id,
                status=PublicationStatus.PENDING,
            )

            # Determine publish time based on strategy
            publish_at = None
            if self.strategy == PublicationStrategy.DELAYED:
                publish_at = datetime.utcnow() + timedelta(
                    seconds=self.delay_seconds
                )
            elif self.strategy == PublicationStrategy.IMMEDIATE:
                publish_at = datetime.utcnow()

            # Save publication record
            await self.publication_repository.save(publication)

            logger.info(
                "Publication record created",
                extra={
                    "publication_id": publication.id,
                    "news_id": news_item.id,
                    "strategy": self.strategy,
                    "publish_at": publish_at,
                },
            )

            # For IMMEDIATE strategy, publish now
            if self.strategy == PublicationStrategy.IMMEDIATE:
                return await self._publish_immediate(
                    news_item, publication, start_time
                )

            # For DELAYED/QUEUED, just create the record
            duration = time.time() - start_time

            return PublishNewsResult(
                success=True,
                publication_id=publication.id,
                status=PublicationStatus.PENDING,
                duration_seconds=duration,
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Publication creation failed: {str(e)}"

            logger.error(
                error_msg,
                extra={"news_id": news_item.id, "duration": duration},
                exc_info=True,
            )

            TELEGRAM_PUBLISH_ERRORS.labels(
                error_type="creation_failed"
            ).inc()
            TELEGRAM_PUBLISH_DURATION.observe(duration)

            return PublishNewsResult(
                success=False,
                error=error_msg,
                duration_seconds=duration,
            )

    async def _publish_immediate(
        self, news_item: NewsItem, publication: Publication, start_time: float
    ) -> PublishNewsResult:
        """Publish news item immediately.

        Args:
            news_item: News item to publish
            publication: Publication record
            start_time: Operation start time

        Returns:
            PublishNewsResult with message details
        """
        import time

        retry_count = 0

        while retry_count < self.max_retries:
            try:
                # Format message
                title = (
                    news_item.content.title_ru
                    or news_item.content.title_en
                    or ""
                )
                content = (
                    news_item.content.content_ru
                    or news_item.content.content_en
                    or ""
                )

                message_text = f"<b>{title}</b>\n\n{content}"

                # Add hashtags if available
                if news_item.metadata.hashtags:
                    message_text += "\n\n" + " ".join(
                        f"#{tag}" for tag in news_item.metadata.hashtags
                    )

                # Add source
                message_text += f"\n\n🔗 <i>Source: {news_item.content.source}</i>"

                # Send to Telegram
                message_id = await self.telegram_client.send_message(
                    text=message_text,
                    parse_mode="HTML",
                )

                # Update publication status
                publication.status = PublicationStatus.PUBLISHED
                publication.telegram_message_id = message_id
                await self.publication_repository.save(publication)

                duration = time.time() - start_time
                TELEGRAM_PUBLISH_DURATION.observe(duration)

                logger.info(
                    "News published successfully",
                    extra={
                        "publication_id": publication.id,
                        "message_id": message_id,
                        "duration": duration,
                        "retries": retry_count,
                    },
                )

                return PublishNewsResult(
                    success=True,
                    publication_id=publication.id,
                    message_id=message_id,
                    status=PublicationStatus.PUBLISHED,
                    duration_seconds=duration,
                    retry_count=retry_count,
                )

            except Exception as e:
                retry_count += 1
                error_msg = f"Publication attempt {retry_count} failed: {str(e)}"

                logger.warning(
                    error_msg,
                    extra={
                        "publication_id": publication.id,
                        "retry_count": retry_count,
                        "max_retries": self.max_retries,
                    },
                    exc_info=True,
                )

                if retry_count >= self.max_retries:
                    # Mark as failed
                    publication.status = PublicationStatus.FAILED
                    publication.retry_count = retry_count
                    await self.publication_repository.save(publication)

                    duration = time.time() - start_time
                    TELEGRAM_PUBLISH_ERRORS.labels(
                        error_type="max_retries_exceeded"
                    ).inc()
                    TELEGRAM_PUBLISH_DURATION.observe(duration)

                    final_error = (
                        f"Publication failed after {retry_count} retries: {str(e)}"
                    )

                    logger.error(
                        final_error,
                        extra={
                            "publication_id": publication.id,
                            "duration": duration,
                        },
                    )

                    return PublishNewsResult(
                        success=False,
                        publication_id=publication.id,
                        status=PublicationStatus.FAILED,
                        error=final_error,
                        duration_seconds=duration,
                        retry_count=retry_count,
                    )

                # Wait before retry (exponential backoff)
                wait_time = 2 ** (retry_count - 1)
                logger.info(
                    f"Waiting {wait_time}s before retry",
                    extra={"publication_id": publication.id},
                )
                await asyncio.sleep(wait_time)

        # This should not be reached
        duration = time.time() - start_time
        return PublishNewsResult(
            success=False,
            error="Unexpected error in publish logic",
            duration_seconds=duration,
        )

    async def retry_failed_publication(
        self, publication_id: str
    ) -> PublishNewsResult:
        """Retry failed publication.

        Args:
            publication_id: ID of publication to retry

        Returns:
            PublishNewsResult with retry result
        """
        try:
            # Retrieve publication
            publication = await self.publication_repository.get_by_id(
                publication_id
            )

            if not publication:
                error_msg = f"Publication {publication_id} not found"
                logger.error(error_msg)
                return PublishNewsResult(success=False, error=error_msg)

            # Check if retryable
            if publication.status != PublicationStatus.FAILED:
                error_msg = (
                    f"Publication is in {publication.status} status, "
                    f"cannot retry"
                )
                logger.warning(error_msg)
                return PublishNewsResult(success=False, error=error_msg)

            if publication.retry_count >= self.max_retries:
                error_msg = "Max retries exceeded"
                logger.warning(error_msg)
                return PublishNewsResult(success=False, error=error_msg)

            # Retrieve news item
            # (would need news_repository for this)
            logger.info(
                "Retrying publication",
                extra={"publication_id": publication_id},
            )

            # For now, just mark as retrying
            publication.status = PublicationStatus.RETRYING
            publication.retry_count += 1
            await self.publication_repository.save(publication)

            return PublishNewsResult(
                success=True,
                publication_id=publication_id,
                status=PublicationStatus.RETRYING,
            )

        except Exception as e:
            error_msg = f"Retry failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return PublishNewsResult(success=False, error=error_msg)


# Import asyncio for sleep
import asyncio
