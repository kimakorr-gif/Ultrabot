"""Custom exceptions for Ultrabot application."""


class UltrabotException(Exception):
    """Base exception for Ultrabot."""

    pass


class ConfigurationError(UltrabotException):
    """Raised when configuration is invalid."""

    pass


class ExternalAPIError(UltrabotException):
    """Raised when external API call fails."""

    pass


class RSSParsingError(ExternalAPIError):
    """Raised when RSS parsing fails."""

    pass


class TranslationError(ExternalAPIError):
    """Raised when translation service fails."""

    pass


class TelegramPublishError(ExternalAPIError):
    """Raised when Telegram publication fails."""

    pass


class DatabaseError(UltrabotException):
    """Raised when database operation fails."""

    pass


class CacheError(UltrabotException):
    """Raised when cache operation fails."""

    pass


class DuplicateNewsError(UltrabotException):
    """Raised when duplicate news is detected."""

    pass


class ValidationError(UltrabotException):
    """Raised when validation fails."""

    pass


class CircuitBreakerOpenError(UltrabotException):
    """Raised when circuit breaker is open."""

    pass


class RetryError(UltrabotException):
    """Raised when all retries are exhausted."""

    pass
