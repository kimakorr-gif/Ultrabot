"""Dependency Injection container using Dishka."""

from typing import AsyncIterator

from dishka import Provider, Scope, provide

from .logger import get_logger, setup_logging
from .settings import Settings


class SettingsProvider(Provider):
    """Provider for application settings."""

    scope = Scope.APP

    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        """Load and return application settings."""
        settings = Settings()  # type: ignore
        setup_logging(settings)
        return settings


class LoggerProvider(Provider):
    """Provider for logging."""

    scope = Scope.APP

    @provide(scope=Scope.APP)
    def logger_setup(self, settings: Settings) -> None:
        """Setup logging infrastructure."""
        setup_logging(settings)
        return None


# Additional providers will be implemented in infrastructure layer
# This is the foundation for DI container setup
