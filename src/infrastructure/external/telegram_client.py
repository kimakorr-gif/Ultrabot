"""Telegram bot client adapter."""

from logging import getLogger
from typing import Optional

from aiogram import Bot
from aiogram.types import InputFile, InputMediaPhoto

from ...core.exceptions import TelegramPublishError

logger = getLogger(__name__)


class TelegramClientAdapter:
    """Telegram bot client implementation."""

    def __init__(self, token: str) -> None:
        """Initialize Telegram client.

        Args:
            token: Telegram bot token
        """
        self.bot = Bot(token=token)

    async def send_message(
        self,
        chat_id: int,
        text: str,
        html: bool = False,
    ) -> int:
        """Send text message to Telegram chat.

        Args:
            chat_id: Chat ID (negative for groups/channels)
            text: Message text
            html: Whether text is HTML formatted

        Returns:
            Message ID

        Raises:
            TelegramPublishError: If sending fails
        """
        try:
            from aiogram.types import ParseMode

            parse_mode = ParseMode.HTML if html else None

            message = await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_web_page_preview=False,
            )

            logger.info(f"Message sent: {message.message_id}")
            return message.message_id

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise TelegramPublishError(f"Failed to send Telegram message: {e}") from e

    async def send_photo(
        self,
        chat_id: int,
        photo_url: str,
        caption: str = "",
    ) -> int:
        """Send photo to Telegram chat.

        Args:
            chat_id: Chat ID
            photo_url: Photo URL or path
            caption: Photo caption

        Returns:
            Message ID

        Raises:
            TelegramPublishError: If sending fails
        """
        try:
            message = await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo_url,
                caption=caption,
            )

            logger.info(f"Photo sent: {message.message_id}")
            return message.message_id

        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
            raise TelegramPublishError(f"Failed to send Telegram photo: {e}") from e

    async def close(self) -> None:
        """Close bot session."""
        await self.bot.session.close()
