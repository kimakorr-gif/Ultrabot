"""Telegram message handlers."""

import logging

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def handle_start(message: Message) -> None:
    """Handle /start command."""
    await message.answer(
        "👾 Ultrabot - Gaming News Aggregator\n\n"
        "I'm monitoring 50+ gaming news sources and publishing relevant updates.\n\n"
        "Use /help for more commands."
    )


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    """Handle /help command."""
    await message.answer(
        "/start - Show welcome message\n"
        "/status - Check bot status\n"
        "/help - Show this help message"
    )


@router.message(Command("status"))
async def handle_status(message: Message) -> None:
    """Handle /status command."""
    await message.answer("✅ Bot is running normally")
