"""Feed entity - represents RSS feed source."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class FeedSource:
    """Represents an RSS feed source."""

    id: UUID = field(default_factory=uuid4)
    name: str
    url: str
    enabled: bool = True

    # Weighting
    priority_weight: int = field(default=5, metadata={"ge": 0, "le": 100})

    # Settings
    fetch_timeout: int = field(default=15, metadata={"ge": 5, "le": 60})
    max_age_seconds: int = field(default=3600, metadata={"ge": 300, "le": 86400})

    # Tracking
    last_fetch_at: datetime = field(default_factory=datetime.utcnow)
    last_fetch_success: bool = True
    consecutive_failures: int = 0

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def mark_successful_fetch(self) -> None:
        """Update tracking after successful fetch."""
        self.last_fetch_at = datetime.utcnow()
        self.last_fetch_success = True
        self.consecutive_failures = 0

    def mark_failed_fetch(self) -> None:
        """Update tracking after failed fetch."""
        self.last_fetch_success = False
        self.consecutive_failures += 1

    def is_disabled_after_failures(self, threshold: int = 10) -> bool:
        """Check if feed should be disabled due to repeated failures."""
        return self.consecutive_failures >= threshold
