"""Telegram bot initialization and startup."""

import logging
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from ...core.logger import get_logger

logger = get_logger(__name__)


class TelegramBot:
    """Telegram bot wrapper."""

    def __init__(self, token: str) -> None:
        """Initialize bot.

        Args:
            token: Bot token
        """
        self.token = token
        self.bot = Bot(token=token)
        self.dp = Dispatcher()

    async def setup_commands(self) -> None:
        """Setup bot commands."""
        commands = [
            BotCommand(command="start", description="Start the bot"),
            BotCommand(command="help", description="Show help"),
            BotCommand(command="status", description="Check bot status"),
        ]

        await self.bot.set_my_commands(commands)
        logger.info("Bot commands configured")

    async def start(self) -> None:
        """Start bot polling."""
        try:
            await self.setup_commands()
            logger.info("Telegram bot started")
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise

    async def stop(self) -> None:
        """Stop bot."""
        await self.bot.session.close()
        logger.info("Telegram bot stopped")
