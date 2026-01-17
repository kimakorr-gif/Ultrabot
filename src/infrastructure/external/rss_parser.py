"""RSS Parser adapter using feedparser."""

import asyncio
from logging import getLogger
from typing import Any

import aiohttp
import feedparser
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ...application.ports import RSSParserPort
from ...core.exceptions import RSSParsingError
from ...core.metrics import RSS_FETCH_DURATION, RSS_FETCH_ERRORS

logger = getLogger(__name__)


class FeedParserAdapter(RSSParserPort):
    """RSS parser implementation with retry logic."""

    def __init__(
        self,
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        timeout: int = 15,
        max_retries: int = 3,
    ) -> None:
        """Initialize RSS parser.

        Args:
            user_agent: Custom user agent for requests
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts on failure
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max_retries

    async def fetch_feed(self, url: str) -> dict[str, Any]:
        """Fetch and parse RSS feed with retry logic.

        Args:
            url: Feed URL

        Returns:
            Parsed feed data

        Raises:
            RSSParsingError: If parsing fails after retries
        """
        import time

        feed_name = url.split("/")[-1] if "/" in url else url

        try:
            start_time = time.time()

            # Retry logic with exponential backoff
            async for attempt in AsyncRetrying(
                retry=retry_if_exception_type(RSSParsingError),
                stop=stop_after_attempt(self.max_retries),
                wait=wait_exponential(multiplier=1, min=1, max=10),
                reraise=True,
            ):
                with attempt:
                    return await self._fetch_feed_impl(url, feed_name, start_time)

        except RSSParsingError as e:
            RSS_FETCH_ERRORS.labels(
                feed_name=feed_name,
                error_type="parsing_error",
            ).inc()
            raise
        except Exception as e:
            logger.error(f"Error parsing feed {url}: {e}")
            RSS_FETCH_ERRORS.labels(
                feed_name=feed_name,
                error_type="unexpected_error",
            ).inc()
            raise RSSParsingError(f"Failed to parse feed {url}: {e}") from e

    async def _fetch_feed_impl(
        self, url: str, feed_name: str, start_time: float
    ) -> dict[str, Any]:
        """Internal implementation of feed fetching.

        Args:
            url: Feed URL
            feed_name: Feed name for metrics
            start_time: Operation start time

        Returns:
            Parsed feed data

        Raises:
            RSSParsingError: If parsing fails
        """
        import time

        try:
            # Fetch feed using aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    headers={"User-Agent": self.user_agent},
                ) as response:
                    if response.status != 200:
                        raise RSSParsingError(
                            f"HTTP {response.status} from {url}"
                        )

                    content = await response.read()

            # Parse feed
            feed = feedparser.parse(content)

            if feed.bozo:
                logger.warning(
                    f"Malformed feed from {url}: {feed.bozo_exception}"
                )

            # Extract entries
            entries = []
            for entry in feed.entries:
                parsed_entry = {
                    "title": entry.get("title", ""),
                    "summary": entry.get(
                        "summary", entry.get("description", "")
                    ),
                    "link": entry.get("link", ""),
                    "published": entry.get(
                        "published", entry.get("updated", None)
                    ),
                    "media": self._extract_media(entry),
                }
                entries.append(parsed_entry)

            duration = time.time() - start_time
            RSS_FETCH_DURATION.labels(feed_name=feed_name).observe(duration)

            return {
                "title": feed.feed.get("title", ""),
                "link": feed.feed.get("link", ""),
                "entries": entries,
            }

        except aiohttp.ClientError as e:
            raise RSSParsingError(f"Network error fetching {url}: {e}") from e
        except RSSParsingError:
            raise
        except Exception as e:
            logger.error(f"Error parsing feed {url}: {e}")
            raise RSSParsingError(
                f"Failed to parse feed {url}: {e}"
            ) from e

    @staticmethod
    def _extract_media(entry: dict[str, Any]) -> dict[str, list[str]]:
        """Extract media URLs from entry.

        Args:
            entry: RSS entry

        Returns:
            Dictionary with 'images' and 'videos' lists
        """
        media = {"images": [], "videos": []}

        # Extract images
        if "media_content" in entry:
            for media_item in entry.get("media_content", []):
                if "image" in media_item.get("type", ""):
                    media["images"].append(media_item.get("url", ""))

        # Extract videos
        if "media_thumbnail" in entry:
            for thumb in entry.get("media_thumbnail", []):
                media["images"].append(thumb.get("url", ""))

        # Check enclosures
        for enclosure in entry.get("enclosures", []):
            url = enclosure.get("href", "")
            enc_type = enclosure.get("type", "")

            if "image" in enc_type:
                media["images"].append(url)
            elif "video" in enc_type:
                media["videos"].append(url)

        return media
