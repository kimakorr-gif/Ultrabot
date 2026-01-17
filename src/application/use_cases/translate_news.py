"""Translate news use case."""

from dataclasses import dataclass

from src.application.use_cases.base import UseCase
from src.core.exceptions import TranslationError
from src.core.logger import get_logger
from src.core.metrics import TRANSLATION_DURATION
from src.domain.entities.news_item import ContentLanguage, NewsItem
from src.domain.services.translator_service import EntityPreservingTranslator

logger = get_logger(__name__)


@dataclass
class TranslateNewsResult:
    """Result of translation operation."""

    success: bool
    news_item: NewsItem | None = None
    error: str | None = None
    duration_seconds: float = 0.0


class TranslateNewsUseCase(UseCase):
    """Translate news item to target language while preserving proper nouns."""

    def __init__(self, translator: EntityPreservingTranslator) -> None:
        """Initialize use case.

        Args:
            translator: Translation service with entity preservation
        """
        self.translator = translator

    async def execute(self, news_item: NewsItem) -> TranslateNewsResult:
        """Translate news item.

        Args:
            news_item: News item to translate

        Returns:
            TranslateNewsResult with translated content or error

        Raises:
            TranslationError: If translation fails
        """
        import time

        start_time = time.time()

        try:
            # Skip if already in Russian
            if news_item.content.language == ContentLanguage.RUSSIAN:
                logger.info(
                    "News already in Russian, skipping translation",
                    extra={"news_id": news_item.id},
                )
                duration = time.time() - start_time
                TRANSLATION_DURATION.observe(duration)
                return TranslateNewsResult(
                    success=True,
                    news_item=news_item,
                    duration_seconds=duration,
                )

            # Translate title
            translated_title = await self.translator.translate(
                news_item.content.title_en or news_item.content.title_ru
            )

            # Translate content
            translated_content = await self.translator.translate(
                news_item.content.content_en or news_item.content.content_ru
            )

            # Create translated news item
            translated_item = NewsItem(
                id=news_item.id,
                feed_id=news_item.feed_id,
                content=news_item.content,
                metadata=news_item.metadata,
                created_at=news_item.created_at,
            )

            # Update content with translations
            translated_item.content.title_ru = translated_title
            translated_item.content.content_ru = translated_content
            translated_item.content.language = ContentLanguage.RUSSIAN

            duration = time.time() - start_time
            TRANSLATION_DURATION.labels(
                source_lang=news_item.content.language.value,
                target_lang="ru"
            ).observe(duration)

            logger.info(
                "News translated successfully",
                extra={
                    "news_id": news_item.id,
                    "duration": duration,
                    "source_language": news_item.content.language,
                },
            )

            return TranslateNewsResult(
                success=True,
                news_item=translated_item,
                duration_seconds=duration,
            )

            duration = time.time() - start_time
            error_msg = f"Translation failed: {str(e)}"

            logger.error(
                error_msg,
                extra={"news_id": news_item.id, "duration": duration},
                exc_info=True,
            )

            TRANSLATION_DURATION.labels(
                source_lang=news_item.content.language.value,
                target_lang="ru"
            ).observe(duration)

            return TranslateNewsResult(
                success=False,
                error=error_msg,
                duration_seconds=duration,
            )
