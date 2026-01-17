"""Unit tests for hashtag service."""

import pytest

from src.domain.services.hashtag_service import HashtagService


@pytest.fixture
def hashtag_service():
    """Create hashtag service instance."""
    return HashtagService(max_hashtags=10)


def test_generate_hashtags_from_content(hashtag_service):
    """Test hashtag generation."""
    title = "RPG Game Released on PS5"
    content = "A new action RPG for PlayStation 5"

    hashtags = hashtag_service.generate_hashtags(title, content)

    assert len(hashtags) > 0
    assert any("RPG" in tag for tag in hashtags)
    assert any("PS5" in tag for tag in hashtags)


def test_generate_hashtags_max_limit(hashtag_service):
    """Test hashtag max limit."""
    title = "Game announcement for multiple platforms"
    content = "rpg fps strategy adventure mmo rts simulation ps5 xbox pc android ios"

    hashtags = hashtag_service.generate_hashtags(title, content)

    assert len(hashtags) <= hashtag_service.max_hashtags


def test_extract_game_names(hashtag_service):
    """Test game name extraction."""
    title = "The Legend of Zelda Tears of Kingdom Released"

    game_names = hashtag_service.extract_game_names(title)

    assert len(game_names) > 0
    assert any("Legend" in name or "Zelda" in name for name in game_names)


def test_empty_content_hashtags(hashtag_service):
    """Test hashtag generation with empty content."""
    hashtags = hashtag_service.generate_hashtags("", "")

    assert isinstance(hashtags, list)
