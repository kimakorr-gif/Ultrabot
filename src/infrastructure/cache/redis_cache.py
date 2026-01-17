"""Redis cache implementation."""

import json
from logging import getLogger
from typing import Any, Optional

try:
    from redis.asyncio import Redis
except ImportError:
    Redis = None

from ...application.ports import CachePort
from ...core.exceptions import CacheError

logger = getLogger(__name__)


class RedisCache(CachePort):
    """Redis cache implementation."""

    def __init__(self, redis_url: str) -> None:
        """Initialize Redis cache.

        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379/0)
        """
        self.redis_url = redis_url
        self.redis: Optional[Any] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            if Redis is None:
                raise CacheError("redis package not installed")
            self.redis = await Redis.from_url(self.redis_url)
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise CacheError(f"Redis connection error: {e}") from e

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")

    async def get(self, key: str) -> str | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.redis:
            raise CacheError("Redis not connected")

        try:
            value = await self.redis.get(key)
            if value:
                return value.decode() if isinstance(value, bytes) else value
            return None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        if not self.redis:
            raise CacheError("Redis not connected")

        try:
            await self.redis.setex(key, ttl, value)
        except Exception as e:
            logger.warning(f"Cache set error: {e}")

    async def delete(self, key: str) -> None:
        """Delete value from cache.

        Args:
            key: Cache key
        """
        if not self.redis:
            raise CacheError("Redis not connected")

        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")

    async def clear(self) -> None:
        """Clear all cache."""
        if not self.redis:
            raise CacheError("Redis not connected")

        try:
            await self.redis.flushdb()
            logger.info("Cache cleared")
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")

    async def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Cache statistics
        """
        if not self.redis:
            raise CacheError("Redis not connected")

        try:
            info = await self.redis.info()
            return {
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
            }
        except Exception as e:
            logger.warning(f"Cache stats error: {e}")
            return {}
