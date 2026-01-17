"""Translator service - handles text translation with entity preservation."""

import hashlib
import re
from abc import ABC, abstractmethod
from logging import getLogger
from typing import Optional

from ..entities.news_item import ContentLanguage, NewsContent
from ..value_objects.base import LanguagePair

logger = getLogger(__name__)


class NamedEntityPattern:
    """Patterns for extracting named entities (proper nouns)."""

    # Game titles (common patterns)
    GAME_PATTERNS = [
        r"\b([A-Z][a-z]+(?: [A-Z][a-z]+)*(?::\s*[A-Z][a-z]+)*)\b",  # Title Case with colons
        r"\b([A-Z\d]+(?:\s+[A-Z\d]+)*)\b",  # ALL CAPS
    ]

    # Company/Studio names
    COMPANY_PATTERNS = [
        r"\b([A-Z][a-z]+\s+(?:Games|Studios|Entertainment|Software|Digital))\b",
        r"\b(Rockstar|Ubisoft|Activision|Blizzard|Square Enix|FromSoftware|Naughty Dog|Insomniac)\b",
    ]

    # Proper nouns (names)
    PROPER_NOUN_PATTERN = r"\b([A-Z][a-z]+)\b"


class TranslationPort(ABC):
    """Abstract port for translation service."""

    @abstractmethod
    async def translate_text(self, text: str, language_pair: LanguagePair) -> str:
        """Translate text.

        Args:
            text: Text to translate
            language_pair: Source and target language

        Returns:
            Translated text
        """
        pass


class EntityPreservingTranslator:
    """Translator that preserves proper nouns during translation."""

    ENTITY_PLACEHOLDER_TEMPLATE = "__ENTITY_{idx}__"

    def __init__(self, translator: TranslationPort) -> None:
        """Initialize entity-preserving translator.

        Args:
            translator: Underlying translation service
        """
        self.translator = translator

    async def translate_content(
        self,
        content: NewsContent,
        target_lang: str,
    ) -> NewsContent:
        """Translate news content while preserving entities.

        Args:
            content: News content to translate
            target_lang: Target language code (e.g., 'ru')

        Returns:
            NewsContent with translated text
        """
        if content.translated_language == ContentLanguage(target_lang):
            logger.debug("Content already translated to target language")
            return content

        # Extract entities
        title_entities = self._extract_entities(content.original_title)
        content_entities = self._extract_entities(content.original_content)

        # Replace entities with placeholders
        title_with_placeholders = self._replace_with_placeholders(
            content.original_title,
            title_entities,
        )
        content_with_placeholders = self._replace_with_placeholders(
            content.original_content,
            content_entities,
        )

        # Translate
        language_pair = LanguagePair(
            source=content.original_language.value,
            target=target_lang,
        )

        try:
            translated_title = await self.translator.translate_text(
                title_with_placeholders,
                language_pair,
            )
            translated_content_text = await self.translator.translate_text(
                content_with_placeholders,
                language_pair,
            )
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise

        # Restore entities
        translated_title = self._restore_entities(translated_title, title_entities)
        translated_content_text = self._restore_entities(
            translated_content_text,
            content_entities,
        )

        # Update content
        content.translated_title = translated_title
        content.translated_content = translated_content_text
        content.translated_language = ContentLanguage(target_lang)

        return content

    def _extract_entities(self, text: str) -> dict[str, str]:
        """Extract named entities from text.

        Args:
            text: Text to extract entities from

        Returns:
            Dictionary mapping entity index to entity text
        """
        entities: dict[str, str] = {}
        entity_count = 0

        # Extract proper nouns (capitalized words)
        for match in re.finditer(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text):
            entity_key = f"entity_{entity_count}"
            entities[entity_key] = match.group(0)
            entity_count += 1

        return entities

    def _replace_with_placeholders(
        self,
        text: str,
        entities: dict[str, str],
    ) -> str:
        """Replace entities with placeholders.

        Args:
            text: Original text
            entities: Dictionary of entities to replace

        Returns:
            Text with entities replaced by placeholders
        """
        result = text
        for entity_key, entity_text in entities.items():
            placeholder = self.ENTITY_PLACEHOLDER_TEMPLATE.format(idx=entity_key)
            result = result.replace(entity_text, placeholder, 1)
        return result

    def _restore_entities(
        self,
        text: str,
        entities: dict[str, str],
    ) -> str:
        """Restore entities from placeholders.

        Args:
            text: Text with placeholders
            entities: Dictionary of entities to restore

        Returns:
            Text with entities restored
        """
        result = text
        for entity_key, entity_text in entities.items():
            placeholder = self.ENTITY_PLACEHOLDER_TEMPLATE.format(idx=entity_key)
            result = result.replace(placeholder, entity_text)
        return result

    def get_entity_cache_key(
        self,
        text: str,
        language_pair: LanguagePair,
    ) -> str:
        """Generate cache key for translated content.

        Args:
            text: Original text
            language_pair: Language pair

        Returns:
            Cache key
        """
        text_hash = hashlib.md5(text.encode()).hexdigest()[:16]
        return f"translation:{language_pair}:{text_hash}"
