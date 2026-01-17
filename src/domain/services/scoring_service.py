"""News scoring service - calculates relevance score."""

import re
from datetime import datetime
from logging import getLogger
from typing import Optional

from ..entities.news_item import NewsContent, NewsItem, NewsMetadata

logger = getLogger(__name__)


class KeywordWeight:
    """Keyword weight levels."""

    HIGH = 3  # Releases, announcements, trailers
    MEDIUM = 2  # Patches, updates, sales
    LOW = 1  # Mods, early access


class ScoringService:
    """Service for calculating news relevance scores."""

    # Keyword tiers
    HIGH_PRIORITY_KEYWORDS = {
        "анонс", "релиз", "трейлер", "announcement", "release", "trailer",
        "announced", "released", "exclusive", "debut", "premiere",
    }

    MEDIUM_PRIORITY_KEYWORDS = {
        "патч", "обновление", "скидка", "patch", "update", "sale", "discount",
        "upgrade", "bug fix", "hotfix", "expansion", "dlc",
    }

    LOW_PRIORITY_KEYWORDS = {
        "мод", "ранний доступ", "mod", "early access", "beta", "alpha",
        "rumor", "leak", "speculation", "fan-made",
    }

    # Source weights (IGN, Polygon, Kotaku, etc.)
    SOURCE_WEIGHTS = {
        "ign": 10,
        "polygon": 8,
        "kotaku": 7,
        "eurogamer": 9,
        "gamespot": 8,
        "rockpapershotgun": 8,
        "pc gamer": 7,
        "destructoid": 7,
        "gameinformer": 9,
        "cnet": 6,
    }

    def __init__(
        self,
        base_score: int = 0,
        freshness_bonus: int = 5,
        freshness_threshold_minutes: int = 15,
    ) -> None:
        """Initialize scoring service.

        Args:
            base_score: Starting score for all news
            freshness_bonus: Bonus points for news < freshness_threshold
            freshness_threshold_minutes: Time window for freshness bonus
        """
        self.base_score = base_score
        self.freshness_bonus = freshness_bonus
        self.freshness_threshold_minutes = freshness_threshold_minutes

    def calculate_score(self, news_item: NewsItem) -> int:
        """Calculate total relevance score for news item.

        Args:
            news_item: News item to score

        Returns:
            Final score (0-100+)
        """
        score = self.base_score

        # Keyword scoring
        content = news_item.content
        title_content = f"{content.original_title} {content.original_content}"

        score += self._score_keywords(title_content)

        # Source weight bonus
        score += self._score_source(news_item.metadata.source_name)

        # Freshness bonus
        score += self._score_freshness(news_item.metadata.published_at)

        logger.debug(
            f"News scored: {news_item.metadata.source_name} - {content.original_title[:50]} = {score}"
        )

        return max(score, 0)  # Ensure non-negative

    def _score_keywords(self, content: str) -> int:
        """Score based on keyword matching.

        Args:
            content: Text content to search

        Returns:
            Keyword score
        """
        score = 0
        content_lower = content.lower()

        # High priority keywords
        for keyword in self.HIGH_PRIORITY_KEYWORDS:
            if self._keyword_matches(content_lower, keyword):
                score += KeywordWeight.HIGH

        # Medium priority keywords
        for keyword in self.MEDIUM_PRIORITY_KEYWORDS:
            if self._keyword_matches(content_lower, keyword):
                score += KeywordWeight.MEDIUM

        # Low priority keywords
        for keyword in self.LOW_PRIORITY_KEYWORDS:
            if self._keyword_matches(content_lower, keyword):
                score += KeywordWeight.LOW

        return score

    def _score_source(self, source_name: str) -> int:
        """Get source weight bonus.

        Args:
            source_name: Name of news source

        Returns:
            Source weight score
        """
        source_lower = source_name.lower()
        for source, weight in self.SOURCE_WEIGHTS.items():
            if source in source_lower:
                return weight
        return 5  # Default weight

    def _score_freshness(self, published_at: datetime) -> int:
        """Calculate freshness bonus.

        Args:
            published_at: Publication timestamp

        Returns:
            Freshness bonus (0 or freshness_bonus)
        """
        age_minutes = (datetime.utcnow() - published_at).total_seconds() / 60

        if age_minutes < self.freshness_threshold_minutes:
            return self.freshness_bonus

        return 0

    @staticmethod
    def _keyword_matches(text: str, keyword: str) -> bool:
        """Check if keyword matches in text with word boundary.

        Args:
            text: Text to search (lowercase)
            keyword: Keyword to find (lowercase)

        Returns:
            True if keyword matches with word boundaries
        """
        pattern = r"\b" + re.escape(keyword) + r"\b"
        return bool(re.search(pattern, text))

    def update_keywords(
        self,
        high: Optional[set[str]] = None,
        medium: Optional[set[str]] = None,
        low: Optional[set[str]] = None,
    ) -> None:
        """Update keyword lists dynamically.

        Args:
            high: High priority keywords
            medium: Medium priority keywords
            low: Low priority keywords
        """
        if high:
            self.HIGH_PRIORITY_KEYWORDS.update(high)
        if medium:
            self.MEDIUM_PRIORITY_KEYWORDS.update(medium)
        if low:
            self.LOW_PRIORITY_KEYWORDS.update(low)
