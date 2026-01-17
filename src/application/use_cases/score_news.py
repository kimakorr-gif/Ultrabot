"""Score news use case."""

from dataclasses import dataclass

from src.application.use_cases.base import UseCase
from src.core.logger import get_logger
from src.core.metrics import NEWS_PROCESSED_TOTAL
from src.domain.entities.news_item import NewsItem
from src.domain.services.scoring_service import ScoringService

logger = get_logger(__name__)


@dataclass
class ScoreNewsResult:
    """Result of scoring operation."""

    success: bool
    news_item: NewsItem | None = None
    score: int = 0
    meets_threshold: bool = False
    error: str | None = None


class ScoreNewsUseCase(UseCase):
    """Score news item based on keywords, source, and freshness."""

    def __init__(self, scoring_service: ScoringService, threshold: int = 8) -> None:
        """Initialize use case.

        Args:
            scoring_service: Service for calculating scores
            threshold: Minimum score to pass (default: 8)
        """
        self.scoring_service = scoring_service
        self.threshold = threshold

    async def execute(self, news_item: NewsItem) -> ScoreNewsResult:
        """Score news item.

        Args:
            news_item: News item to score

        Returns:
            ScoreNewsResult with score and threshold check

        Raises:
            Exception: If scoring fails
        """
        try:
            # Get text to score (prefer Russian)
            text_to_score = (
                news_item.content.content_ru
                or news_item.content.content_en
                or ""
            )
            title_to_score = (
                news_item.content.title_ru or news_item.content.title_en or ""
            )

            # Score keywords
            keyword_score = self.scoring_service.score_keywords(
                title_to_score, text_to_score
            )

            # Score source
            source_score = self.scoring_service.score_source(news_item.content.source)

            # Score freshness
            freshness_bonus = self.scoring_service.calculate_freshness_bonus(
                news_item.created_at
            )

            # Calculate total score
            total_score = min(
                100, keyword_score + source_score + freshness_bonus
            )  # Cap at 100

            # Update news item with score
            news_item.metadata.score = total_score

            # Determine if meets threshold
            meets_threshold = total_score >= self.threshold

            # Record metric
            NEWS_PROCESSED_TOTAL.labels(
                source=news_item.content.source,
                status="approved" if meets_threshold else "rejected",
            ).inc()

            logger.info(
                "News scored successfully",
                extra={
                    "news_id": news_item.id,
                    "keyword_score": keyword_score,
                    "source_score": source_score,
                    "freshness_bonus": freshness_bonus,
                    "total_score": total_score,
                    "meets_threshold": meets_threshold,
                },
            )

            return ScoreNewsResult(
                success=True,
                news_item=news_item,
                score=total_score,
                meets_threshold=meets_threshold,
            )

        except Exception as e:
            error_msg = f"Scoring failed: {str(e)}"

            logger.error(
                error_msg,
                extra={"news_id": news_item.id},
                exc_info=True,
            )

            NEWS_PROCESSED_TOTAL.labels(
                source=news_item.content.source,
                status="error",
            ).inc()

            return ScoreNewsResult(
                success=False,
                error=error_msg,
            )
