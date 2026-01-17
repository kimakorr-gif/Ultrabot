"""Value objects for domain model."""

from dataclasses import dataclass
from typing import Any

from pydantic import HttpUrl, validator


@dataclass(frozen=True)
class URL:
    """Value object for URL validation."""

    value: str

    def __post_init__(self) -> None:
        """Validate URL."""
        try:
            HttpUrl(self.value)
        except Exception as e:
            raise ValueError(f"Invalid URL: {self.value}") from e

    def __str__(self) -> str:
        """Return string representation."""
        return self.value


@dataclass(frozen=True)
class DedupHash:
    """Value object for deduplication hash."""

    algorithm: str  # md5, sha256
    value: str

    def __post_init__(self) -> None:
        """Validate hash."""
        if not self.value:
            raise ValueError("Hash value cannot be empty")
        if self.algorithm not in ("md5", "sha256"):
            raise ValueError(f"Unknown hash algorithm: {self.algorithm}")

    def __str__(self) -> str:
        """Return string representation."""
        return self.value

    def __eq__(self, other: Any) -> bool:
        """Compare by value only."""
        if isinstance(other, DedupHash):
            return self.value == other.value
        return self.value == other


@dataclass(frozen=True)
class Score:
    """Value object for news relevance score."""

    value: int
    max_value: int = 100

    def __post_init__(self) -> None:
        """Validate score."""
        if not 0 <= self.value <= self.max_value:
            raise ValueError(f"Score must be between 0 and {self.max_value}")

    def meets_threshold(self, threshold: int) -> bool:
        """Check if score meets minimum threshold."""
        return self.value >= threshold

    def __int__(self) -> int:
        """Return integer value."""
        return self.value


@dataclass(frozen=True)
class LanguagePair:
    """Value object for language pair."""

    source: str  # Language code: en, ru, etc.
    target: str

    def __post_init__(self) -> None:
        """Validate languages."""
        if not (len(self.source) == 2 and self.source.isalpha()):
            raise ValueError(f"Invalid source language code: {self.source}")
        if not (len(self.target) == 2 and self.target.isalpha()):
            raise ValueError(f"Invalid target language code: {self.target}")

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.source}→{self.target}"
