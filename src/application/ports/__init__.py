"""Ports - interfaces for external services."""

from typing import Protocol, runtime_checkable

from ...domain.value_objects.base import LanguagePair


@runtime_checkable
class RSSParserPort(Protocol):
    """Port for RSS parsing."""

    async def fetch_feed(self, url: str) -> dict:
        """Fetch and parse RSS feed.

        Args:
            url: Feed URL

        Returns:
            Parsed feed data
        """
        ...


@runtime_checkable
class TranslatorPort(Protocol):
    """Port for text translation."""

    async def translate(self, text: str, language_pair: LanguagePair) -> str:
        """Translate text.

        Args:
            text: Text to translate
            language_pair: Source and target language

        Returns:
            Translated text
        """
        ...


@runtime_checkable
class CachePort(Protocol):
    """Port for caching."""

    async def get(self, key: str) -> str | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        ...

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        ...

    async def delete(self, key: str) -> None:
        """Delete value from cache.

        Args:
            key: Cache key
        """
        ...


@runtime_checkable
class TelegramPort(Protocol):
    """Port for Telegram operations."""

    async def send_message(self, chat_id: int, text: str, html: bool = False) -> int:
        """Send message to Telegram chat.

        Args:
            chat_id: Chat ID
            text: Message text
            html: Whether text is HTML formatted

        Returns:
            Message ID
        """
        ...

    async def send_photo(self, chat_id: int, photo_url: str, caption: str = "") -> int:
        """Send photo to Telegram chat.

        Args:
            chat_id: Chat ID
            photo_url: Photo URL
            caption: Photo caption

        Returns:
            Message ID
        """
        ...
