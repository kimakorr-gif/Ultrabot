"""In-memory cache implementation."""

from datetime import datetime, timedelta
from logging import getLogger
from typing import Any, Optional
from collections import OrderedDict

from ...application.ports import CachePort
from ...core.exceptions import CacheError

logger = getLogger(__name__)


class CacheEntry:
    """Cache entry with TTL."""

    def __init__(self, value: str, ttl: int = 3600) -> None:
        """Initialize cache entry.

        Args:
            value: Entry value
            ttl: Time to live in seconds
        """
        self.value = value
        self.expires_at = datetime.utcnow() + timedelta(seconds=ttl)

    def is_expired(self) -> bool:
        """Check if entry is expired.

        Returns:
            True if expired
        """
        return datetime.utcnow() > self.expires_at


class MemoryCache(CachePort):
    """In-memory cache with LRU eviction and TTL."""

    def __init__(self, max_size: int = 1000) -> None:
        """Initialize memory cache.

        Args:
            max_size: Maximum number of items
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.hits = 0
        self.misses = 0

    async def get(self, key: str) -> str | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if key not in self.cache:
            self.misses += 1
            return None

        entry = self.cache[key]

        if entry.is_expired():
            del self.cache[key]
            self.misses += 1
            return None

        # Move to end (LRU)
        self.cache.move_to_end(key)
        self.hits += 1
        return entry.value

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        # Remove old entry if exists
        if key in self.cache:
            del self.cache[key]

        # Add new entry
        self.cache[key] = CacheEntry(value, ttl)

        # LRU eviction if needed
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)
            logger.debug("LRU eviction: removed oldest entry")

    async def delete(self, key: str) -> None:
        """Delete value from cache.

        Args:
            key: Cache key
        """
        if key in self.cache:
            del self.cache[key]

    async def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Memory cache cleared")

    def get_hit_ratio(self) -> float:
        """Get cache hit ratio.

        Returns:
            Hit ratio (0-1)
        """
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Cache statistics
        """
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": self.get_hit_ratio(),
        }
