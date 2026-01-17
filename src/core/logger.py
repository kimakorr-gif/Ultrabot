"""Structured logging configuration."""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .settings import Settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra context
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id
        if hasattr(record, "context"):
            log_data["context"] = record.context

        return json.dumps(log_data, default=str)


class TextFormatter(logging.Formatter):
    """Text formatter for human-readable logging."""

    FORMAT = (
        "%(asctime)s - %(name)s - %(levelname)s "
        "[%(filename)s:%(lineno)d] - %(message)s"
    )

    def __init__(self) -> None:
        super().__init__(fmt=self.FORMAT, datefmt="%Y-%m-%d %H:%M:%S")


def setup_logging(settings: Settings) -> None:
    """Setup logging for the application."""
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Choose formatter
    if settings.log_format == "json":
        formatter = JSONFormatter(settings)
    else:
        formatter = TextFormatter()

    # Console handler (always enabled)
    if settings.log_to_stdout:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler (optional)
    if settings.log_to_file:
        Path(settings.log_file_path).parent.mkdir(parents=True, exist_ok=True)

        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(
            filename=settings.log_file_path,
            maxBytes=settings.log_file_max_bytes,
            backupCount=settings.log_file_backup_count,
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get logger with specific name."""
    return logging.getLogger(name)


class LogContext:
    """Context manager for adding correlation IDs to logs."""

    def __init__(self, correlation_id: str) -> None:
        self.correlation_id = correlation_id
        self.token: Optional[Any] = None

    def __enter__(self) -> "LogContext":
        # Store correlation ID in context
        return self

    def __exit__(self, *args: Any) -> None:
        # Clean up
        pass
