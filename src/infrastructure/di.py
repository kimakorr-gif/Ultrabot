"""Infrastructure layer dependency injection providers."""

from typing import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from src.core.settings import Settings
from src.domain.services.hashtag_service import HashtagService
from src.domain.services.scoring_service import ScoringService
from src.domain.services.translator_service import EntityPreservingTranslator
from src.infrastructure.cache.memory_cache import MemoryCache
from src.infrastructure.cache.redis_cache import RedisCache
from src.infrastructure.database.repositories import (
    PostgresFeedRepository,
    PostgresNewsRepository,
    PostgresPublicationRepository,
)
from src.infrastructure.external.rss_parser import FeedParserAdapter
from src.infrastructure.external.telegram_client import TelegramClientAdapter
from src.infrastructure.external.yandex_translator import YandexTranslatorAdapter


class DatabaseProvider(Provider):
    """Database and repository providers."""

    scope = Scope.APP

    @provide
    async def database_engine(self, settings: Settings) -> AsyncEngine:
        """Create async SQLAlchemy engine."""
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.SQL_ECHO,
            pool_pre_ping=True,
            poolclass=NullPool if settings.ENVIRONMENT == "test" else None,
            connect_args={
                "timeout": settings.DB_TIMEOUT,
                "command_timeout": settings.DB_TIMEOUT,
                "server_settings": {
                    "jit": "off",  # Disable JIT for consistency
                },
            },
        )
        return engine

    @provide
    async def session_factory(
        self, engine: AsyncEngine
    ) -> AsyncGenerator[AsyncSession, None]:
        """Create async session factory."""
        async with engine.begin() as conn:
            # Create tables if not exists
            # from src.infrastructure.database.models import Base
            # await conn.run_sync(Base.metadata.create_all)
            pass

        async_session = AsyncSession(
            bind=engine,
            expire_on_commit=False,
        )

        yield async_session

        await async_session.close()
        await engine.dispose()

    @provide(scope=Scope.REQUEST)
    async def session(
        self, engine: AsyncEngine
    ) -> AsyncGenerator[AsyncSession, None]:
        """Provide request-scoped database session."""
        async with AsyncSession(bind=engine, expire_on_commit=False) as session:
            yield session

    @provide
    def news_repository(self, session: AsyncSession) -> PostgresNewsRepository:
        """Provide news repository."""
        return PostgresNewsRepository(session)

    @provide
    def feed_repository(self, session: AsyncSession) -> PostgresFeedRepository:
        """Provide feed repository."""
        return PostgresFeedRepository(session)

    @provide
    def publication_repository(
        self, session: AsyncSession
    ) -> PostgresPublicationRepository:
        """Provide publication repository."""
        return PostgresPublicationRepository(session)


class CacheProvider(Provider):
    """Cache providers."""

    scope = Scope.APP

    @provide
    async def redis_cache(self, settings: Settings) -> RedisCache:
        """Provide Redis cache."""
        cache = RedisCache(
            url=settings.REDIS_URL,
            default_ttl=settings.REDIS_DEFAULT_TTL,
            key_prefix=settings.REDIS_KEY_PREFIX,
        )
        await cache.connect()
        return cache

    @provide
    async def memory_cache(self, settings: Settings) -> MemoryCache:
        """Provide in-memory LRU cache."""
        return MemoryCache(
            max_size=settings.MEMORY_CACHE_MAX_SIZE,
            default_ttl=settings.MEMORY_CACHE_DEFAULT_TTL,
        )


class ExternalServicesProvider(Provider):
    """External service adapters."""

    scope = Scope.APP

    @provide
    def feed_parser(self) -> FeedParserAdapter:
        """Provide RSS feed parser adapter."""
        return FeedParserAdapter()

    @provide
    def telegram_client(self, settings: Settings) -> TelegramClientAdapter:
        """Provide Telegram client adapter."""
        return TelegramClientAdapter(
            token=settings.TELEGRAM_TOKEN,
            channel_id=settings.TELEGRAM_CHANNEL_ID,
        )

    @provide
    def yandex_translator(self, settings: Settings) -> YandexTranslatorAdapter:
        """Provide Yandex translator adapter."""
        return YandexTranslatorAdapter(
            api_key=settings.YANDEX_API_KEY,
            folder_id=settings.YANDEX_FOLDER_ID,
            source_language=settings.YANDEX_SOURCE_LANGUAGE,
            target_language=settings.YANDEX_TARGET_LANGUAGE,
        )


class DomainServicesProvider(Provider):
    """Domain service providers."""

    scope = Scope.APP

    @provide
    def scoring_service(self) -> ScoringService:
        """Provide scoring service."""
        return ScoringService()

    @provide
    def translator_service(
        self, translator: YandexTranslatorAdapter
    ) -> EntityPreservingTranslator:
        """Provide translator service."""
        return EntityPreservingTranslator(translator_port=translator)

    @provide
    def hashtag_service(self) -> HashtagService:
        """Provide hashtag service."""
        return HashtagService()


class InfrastructureContainer:
    """Main infrastructure DI container combining all providers."""

    def __init__(self):
        """Initialize all providers."""
        self.database_provider = DatabaseProvider()
        self.cache_provider = CacheProvider()
        self.external_services_provider = ExternalServicesProvider()
        self.domain_services_provider = DomainServicesProvider()

    def get_providers(self) -> list[Provider]:
        """Get all providers for dishka."""
        return [
            self.database_provider,
            self.cache_provider,
            self.external_services_provider,
            self.domain_services_provider,
        ]
