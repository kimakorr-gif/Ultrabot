"""Unit tests for use cases."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.application.use_cases.deduplicate_news import DeduplicateNewsUseCase
from src.application.use_cases.publish_news import PublishNewsUseCase, PublicationStrategy
from src.application.use_cases.score_news import ScoreNewsUseCase
from src.application.use_cases.translate_news import TranslateNewsUseCase
from src.domain.entities.news_item import ContentLanguage, NewsContent, NewsItem
from src.domain.repositories import NewsRepository, PublicationRepository
from src.domain.services.scoring_service import ScoringService
from src.domain.services.translator_service import EntityPreservingTranslator
from src.infrastructure.external.telegram_client import TelegramClientAdapter
from src.infrastructure.external.yandex_translator import YandexTranslatorAdapter


class TestTranslateNewsUseCase:
    """Tests for TranslateNewsUseCase."""

    @pytest.mark.asyncio
    async def test_skip_russian_content(self):
        """Test that Russian content is not translated."""
        mock_translator = AsyncMock(spec=YandexTranslatorAdapter)
        translator_service = EntityPreservingTranslator(
            translator_port=mock_translator
        )
        uc = TranslateNewsUseCase(translator=translator_service)

        news = NewsItem(
            feed_id="feed_1",
            content=NewsContent(
                title_ru="Русский заголовок",
                content_ru="Русский контент",
                language=ContentLanguage.RUSSIAN,
                source="Source",
            ),
        )

        result = await uc.execute(news)

        assert result.success
        assert mock_translator.translate.call_count == 0

    @pytest.mark.asyncio
    async def test_translate_english_content(self):
        """Test translation of English content."""
        mock_translator = AsyncMock(spec=YandexTranslatorAdapter)
        mock_translator.translate.return_value = "Переведённый текст"

        translator_service = EntityPreservingTranslator(
            translator_port=mock_translator
        )
        uc = TranslateNewsUseCase(translator=translator_service)

        news = NewsItem(
            feed_id="feed_1",
            content=NewsContent(
                title_en="English Title",
                content_en="English content",
                language=ContentLanguage.ENGLISH,
                source="Source",
            ),
        )

        result = await uc.execute(news)

        assert result.success
        assert result.news_item is not None
        assert result.news_item.content.language == ContentLanguage.RUSSIAN

    @pytest.mark.asyncio
    async def test_translation_error_handling(self):
        """Test handling of translation errors."""
        mock_translator = AsyncMock(spec=YandexTranslatorAdapter)
        mock_translator.translate.side_effect = Exception("API Error")

        translator_service = EntityPreservingTranslator(
            translator_port=mock_translator
        )
        uc = TranslateNewsUseCase(translator=translator_service)

        news = NewsItem(
            feed_id="feed_1",
            content=NewsContent(
                title_en="Title",
                content_en="Content",
                language=ContentLanguage.ENGLISH,
                source="Source",
            ),
        )

        result = await uc.execute(news)

        assert not result.success
        assert result.error is not None


class TestScoreNewsUseCase:
    """Tests for ScoreNewsUseCase."""

    @pytest.mark.asyncio
    async def test_score_with_high_quality_source(self):
        """Test scoring with high-value source."""
        scoring_service = ScoringService()
        uc = ScoreNewsUseCase(scoring_service=scoring_service, threshold=8)

        news = NewsItem(
            feed_id="feed_1",
            content=NewsContent(
                title_ru="Игра выпущена",
                content_ru="Новая игра выпущена с отличными рецензиями",
                language=ContentLanguage.RUSSIAN,
                source="IGN",  # High-weight source
            ),
        )

        result = await uc.execute(news)

        assert result.success
        assert result.score > 0

    @pytest.mark.asyncio
    async def test_score_with_gaming_keywords(self):
        """Test scoring boost from gaming keywords."""
        scoring_service = ScoringService()
        uc = ScoreNewsUseCase(scoring_service=scoring_service, threshold=5)

        news = NewsItem(
            feed_id="feed_1",
            content=NewsContent(
                title_ru="RPG выпуск",
                content_ru="Новая ролевая игра (RPG) на PlayStation 5",
                language=ContentLanguage.RUSSIAN,
                source="Generic",
            ),
        )

        result = await uc.execute(news)

        assert result.success
        assert result.score > 0

    @pytest.mark.asyncio
    async def test_score_below_threshold(self):
        """Test news that scores below threshold."""
        scoring_service = ScoringService()
        uc = ScoreNewsUseCase(scoring_service=scoring_service, threshold=15)

        news = NewsItem(
            feed_id="feed_1",
            content=NewsContent(
                title_ru="Обычная новость",
                content_ru="Просто случайная новость без контекста",
                language=ContentLanguage.RUSSIAN,
                source="Unknown",
            ),
        )

        result = await uc.execute(news)

        assert result.success
        assert not result.meets_threshold


class TestDeduplicateNewsUseCase:
    """Tests for DeduplicateNewsUseCase."""

    @pytest.mark.asyncio
    async def test_detect_duplicate(self):
        """Test duplicate detection."""
        mock_repo = AsyncMock(spec=NewsRepository)

        existing_news = NewsItem(
            feed_id="feed_1",
            content=NewsContent(
                title_en="Original",
                content_en="Original content",
                language=ContentLanguage.ENGLISH,
                source="Source",
            ),
        )
        existing_news.id = "existing_id"

        mock_repo.get_by_dedup_hash.return_value = existing_news

        uc = DeduplicateNewsUseCase(news_repository=mock_repo)

        news = NewsItem(
            feed_id="feed_2",
            content=NewsContent(
                title_en="Copy",
                content_en="Original content",  # Same content
                language=ContentLanguage.ENGLISH,
                source="Source",
            ),
        )

        result = await uc.execute(news)

        assert result.success
        assert result.is_duplicate
        assert result.existing_news_id == "existing_id"

    @pytest.mark.asyncio
    async def test_detect_unique_news(self):
        """Test unique news detection."""
        mock_repo = AsyncMock(spec=NewsRepository)
        mock_repo.get_by_dedup_hash.return_value = None

        uc = DeduplicateNewsUseCase(news_repository=mock_repo)

        news = NewsItem(
            feed_id="feed_1",
            content=NewsContent(
                title_en="Unique",
                content_en="Unique content",
                language=ContentLanguage.ENGLISH,
                source="Source",
            ),
        )

        result = await uc.execute(news)

        assert result.success
        assert not result.is_duplicate

    @pytest.mark.asyncio
    async def test_cleanup_old_news(self):
        """Test cleanup of old news."""
        mock_repo = AsyncMock(spec=NewsRepository)
        mock_repo.cleanup_old.return_value = 15

        uc = DeduplicateNewsUseCase(news_repository=mock_repo)

        result = await uc.cleanup_old_news(days=30)

        assert result["success"]
        assert result["deleted_count"] == 15


class TestPublishNewsUseCase:
    """Tests for PublishNewsUseCase."""

    @pytest.mark.asyncio
    async def test_publish_immediate_success(self):
        """Test successful immediate publication."""
        mock_telegram = AsyncMock(spec=TelegramClientAdapter)
        mock_publication_repo = AsyncMock(spec=PublicationRepository)

        mock_telegram.send_message.return_value = 12345
        mock_publication_repo.save.return_value = None

        uc = PublishNewsUseCase(
            telegram_client=mock_telegram,
            publication_repository=mock_publication_repo,
            strategy=PublicationStrategy.IMMEDIATE,
        )

        news = NewsItem(
            feed_id="feed_1",
            content=NewsContent(
                title_ru="Игра выпущена",
                content_ru="Новая игра выпущена сегодня",
                language=ContentLanguage.RUSSIAN,
                source="IGN",
            ),
        )

        result = await uc.execute(news)

        assert result.success
        assert result.publication_id is not None

    @pytest.mark.asyncio
    async def test_publish_delayed_strategy(self):
        """Test delayed publication strategy."""
        mock_telegram = AsyncMock(spec=TelegramClientAdapter)
        mock_publication_repo = AsyncMock(spec=PublicationRepository)

        mock_publication_repo.save.return_value = None

        uc = PublishNewsUseCase(
            telegram_client=mock_telegram,
            publication_repository=mock_publication_repo,
            strategy=PublicationStrategy.DELAYED,
            delay_seconds=600,
        )

        news = NewsItem(
            feed_id="feed_1",
            content=NewsContent(
                title_ru="Тест",
                content_ru="Контент",
                language=ContentLanguage.RUSSIAN,
                source="Source",
            ),
        )

        result = await uc.execute(news)

        assert result.success
        # Telegram should not be called immediately
        mock_telegram.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_with_hashtags(self):
        """Test publication includes hashtags."""
        mock_telegram = AsyncMock(spec=TelegramClientAdapter)
        mock_publication_repo = AsyncMock(spec=PublicationRepository)

        mock_telegram.send_message.return_value = 12345
        mock_publication_repo.save.return_value = None

        uc = PublishNewsUseCase(
            telegram_client=mock_telegram,
            publication_repository=mock_publication_repo,
            strategy=PublicationStrategy.IMMEDIATE,
        )

        news = NewsItem(
            feed_id="feed_1",
            content=NewsContent(
                title_ru="Игра",
                content_ru="Контент",
                language=ContentLanguage.RUSSIAN,
                source="IGN",
            ),
        )
        news.metadata.hashtags = ["#RPG", "#PS5"]

        result = await uc.execute(news)

        assert result.success
        # Verify hashtags were included in message
        call_args = mock_telegram.send_message.call_args
        if call_args:
            message_text = call_args[1].get("text", "")
            assert "#RPG" in message_text or "#PS5" in message_text
