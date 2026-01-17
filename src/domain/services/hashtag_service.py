"""Hashtag generation service."""

import re
from logging import getLogger
from typing import Optional

logger = getLogger(__name__)


class HashtagService:
    """Service for automatic hashtag generation from news content."""

    # Game-related keywords that become hashtags
    GAME_KEYWORDS = {
        "rpg": "#RPG",
        "fps": "#FPS",
        "strategy": "#Strategy",
        "adventure": "#Adventure",
        "shooter": "#Shooter",
        "mmo": "#MMO",
        "rts": "#RTS",
        "simulation": "#Simulation",
        "sports": "#Sports",
        "racing": "#Racing",
    }

    # Platform hashtags
    PLATFORM_KEYWORDS = {
        "pc": "#PC",
        "ps5": "#PS5",
        "ps4": "#PS4",
        "xbox series x": "#XboxSeriesX",
        "xbox series s": "#XboxSeriesS",
        "xbox one": "#XboxOne",
        "switch": "#NintendoSwitch",
        "mobile": "#Mobile",
        "ios": "#iOS",
        "android": "#Android",
    }

    # Event/Action keywords
    ACTION_KEYWORDS = {
        "анонс": "#Announcement",
        "релиз": "#Release",
        "трейлер": "#Trailer",
        "патч": "#Patch",
        "обновление": "#Update",
        "скидка": "#Sale",
        "announcement": "#Announcement",
        "release": "#Release",
        "trailer": "#Trailer",
        "patch": "#Patch",
        "update": "#Update",
        "sale": "#Sale",
        "beta": "#Beta",
        "dlc": "#DLC",
    }

    def __init__(self, max_hashtags: int = 10) -> None:
        """Initialize hashtag service.

        Args:
            max_hashtags: Maximum number of hashtags to generate
        """
        self.max_hashtags = max_hashtags

    def generate_hashtags(
        self,
        title: str,
        content: str,
        game_name: Optional[str] = None,
    ) -> list[str]:
        """Generate hashtags from content.

        Args:
            title: News title
            content: News content
            game_name: Optional main game title

        Returns:
            List of relevant hashtags
        """
        hashtags: set[str] = set()
        combined_text = f"{title} {content}".lower()

        # Add game name as hashtag if provided
        if game_name:
            hashtags.add(f"#{game_name.replace(' ', '')[:20]}")

        # Extract genre/platform hashtags
        hashtags.update(self._extract_keyword_hashtags(combined_text))

        # Limit to maximum
        hashtags_list = sorted(list(hashtags))[: self.max_hashtags]

        logger.debug(f"Generated hashtags: {hashtags_list}")
        return hashtags_list

    def _extract_keyword_hashtags(self, text: str) -> set[str]:
        """Extract keyword-based hashtags.

        Args:
            text: Text to search

        Returns:
            Set of relevant hashtags
        """
        hashtags: set[str] = set()

        # Game genres
        for keyword, hashtag in self.GAME_KEYWORDS.items():
            if re.search(rf"\b{keyword}\b", text):
                hashtags.add(hashtag)

        # Platforms
        for keyword, hashtag in self.PLATFORM_KEYWORDS.items():
            if keyword in text:
                hashtags.add(hashtag)

        # Actions
        for keyword, hashtag in self.ACTION_KEYWORDS.items():
            if keyword in text:
                hashtags.add(hashtag)

        return hashtags

    def extract_game_names(self, title: str) -> list[str]:
        """Extract potential game names from title.

        Args:
            title: News title

        Returns:
            List of potential game names
        """
        # Simple extraction: Title Case words at the beginning
        game_names: list[str] = []
        words = title.split()

        for word in words[:3]:  # First 3 words only
            if word[0].isupper() and len(word) > 3:
                # Remove punctuation
                clean_word = re.sub(r"[^\w\s]", "", word)
                if clean_word:
                    game_names.append(clean_word)

        return game_names
