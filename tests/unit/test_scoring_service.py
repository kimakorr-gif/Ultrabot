"""Unit tests for scoring service."""

import pytest
from datetime import datetime, timedelta

from src.domain.entities.news_item import NewsContent, NewsItem, NewsMetadata, ContentLanguage
from src.domain.services.scoring_service import ScoringService


@pytest.fixture
def scoring_service():
    """Create scoring service instance."""
    return ScoringService()


@pytest.fixture
def sample_news_item():
    """Create sample news item for testing."""
    content = NewsContent(
        original_title="Elden Ring Patch 2.0 Released",
        original_content="FromSoftware announces major update",
    )

    metadata = NewsMetadata(
        source_url="http://example.com/news",
        source_name="IGN",
        published_at=datetime.utcnow(),
    )

    return NewsItem(content=content, metadata=metadata)


def test_scoring_high_priority_keywords(scoring_service, sample_news_item):
    """Test scoring with high priority keywords."""
    sample_news_item.content.original_title = "Elden Ring Announcement"
    score = scoring_service.calculate_score(sample_news_item)
    
    assert score > 0
    assert "announcement" in sample_news_item.content.original_title.lower()


def test_scoring_source_weight(scoring_service, sample_news_item):
    """Test source weight bonus."""
    sample_news_item.metadata.source_name = "IGN"
    score_ign = scoring_service.calculate_score(sample_news_item)

    sample_news_item.metadata.source_name = "Unknown"
    score_unknown = scoring_service.calculate_score(sample_news_item)

    assert score_ign > score_unknown


def test_scoring_freshness_bonus(scoring_service, sample_news_item):
    """Test freshness bonus for recent news."""
    # Recent news (< 15 min)
    sample_news_item.metadata.published_at = datetime.utcnow() - timedelta(minutes=5)
    score_fresh = scoring_service.calculate_score(sample_news_item)

    # Old news (> 15 min)
    sample_news_item.metadata.published_at = datetime.utcnow() - timedelta(minutes=30)
    score_old = scoring_service.calculate_score(sample_news_item)

    assert score_fresh > score_old


def test_keyword_updates(scoring_service):
    """Test dynamic keyword updates."""
    scoring_service.update_keywords(
        high={"cyberpunk"},
        medium={"preorder"},
    )

    assert "cyberpunk" in scoring_service.HIGH_PRIORITY_KEYWORDS
    assert "preorder" in scoring_service.MEDIUM_PRIORITY_KEYWORDS
