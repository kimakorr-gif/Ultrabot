"""Test fixtures and utilities."""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_rss_parser():
    """Mock RSS parser."""
    parser = AsyncMock()
    parser.fetch_feed = AsyncMock(
        return_value={
            "title": "Test Feed",
            "entries": [
                {
                    "title": "Test News",
                    "summary": "Test summary",
                    "link": "http://example.com/news",
                    "published": "2024-01-17T10:00:00Z",
                }
            ],
        }
    )
    return parser


@pytest.fixture
def mock_translator():
    """Mock translator."""
    translator = AsyncMock()
    translator.translate = AsyncMock(return_value="Переведённый текст")
    return translator


@pytest.fixture
def mock_cache():
    """Mock cache."""
    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock()
    cache.delete = AsyncMock()
    return cache


@pytest.fixture
def mock_telegram_client():
    """Mock Telegram client."""
    client = AsyncMock()
    client.send_message = AsyncMock(return_value=12345)
    client.send_photo = AsyncMock(return_value=12346)
    return client
