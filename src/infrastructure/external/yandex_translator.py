"""Yandex Translate API adapter."""

import asyncio
from logging import getLogger
from typing import Optional

import aiohttp
from pybreaker import CircuitBreaker
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ...application.ports import TranslatorPort
from ...core.exceptions import TranslationError
from ...core.metrics import CIRCUIT_BREAKER_ERRORS, CIRCUIT_BREAKER_STATE
from ...domain.value_objects.base import LanguagePair

logger = getLogger(__name__)


class YandexTranslatorAdapter(TranslatorPort):
    """Yandex.Translate API implementation with circuit breaker."""

    BASE_URL = "https://translate.api.cloud.yandex.net/translate/v2/translate"

    def __init__(
        self,
        api_key: str,
        folder_id: Optional[str] = None,
        source_language: str = "en",
        target_language: str = "ru",
        timeout: int = 30,
        circuit_breaker_failure_threshold: int = 5,
        circuit_breaker_recovery_timeout: int = 60,
    ) -> None:
        """Initialize Yandex translator.

        Args:
            api_key: Yandex API key
            folder_id: Yandex Cloud folder ID (optional)
            source_language: Source language code (default: en)
            target_language: Target language code (default: ru)
            timeout: Request timeout in seconds
            circuit_breaker_failure_threshold: Number of failures to open circuit
            circuit_breaker_recovery_timeout: Timeout before attempting recovery
        """
        self.api_key = api_key
        self.folder_id = folder_id or ""
        self.source_language = source_language
        self.target_language = target_language
        self.timeout = timeout

        # Circuit breaker
        self.circuit_breaker = CircuitBreaker(
            fail_max=circuit_breaker_failure_threshold,
            reset_timeout=circuit_breaker_recovery_timeout,
            name="yandex_translator",
        )

    async def translate(self, text: str, language_pair: LanguagePair | None = None) -> str:
        """Translate text using Yandex API with retry and circuit breaker.

        Args:
            text: Text to translate
            language_pair: Source and target language (optional, uses default)

        Returns:
            Translated text

        Raises:
            TranslationError: If translation fails
        """
        if not text:
            return ""

        # Use default language pair if not provided
        if not language_pair:
            language_pair = LanguagePair(
                source=self.source_language,
                target=self.target_language,
            )

        # Check circuit breaker state
        if self.circuit_breaker.opened:
            CIRCUIT_BREAKER_STATE.labels(service="yandex_translator").set(1)
            error_msg = "Circuit breaker is open, translation service unavailable"
            logger.error(error_msg)
            raise TranslationError(error_msg)

        CIRCUIT_BREAKER_STATE.labels(service="yandex_translator").set(0)

        # Retry logic
        try:
            async for attempt in AsyncRetrying(
                retry=retry_if_exception_type(TranslationError),
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=1, max=10),
                reraise=True,
            ):
                with attempt:
                    return await self._translate_with_circuit_breaker(
                        text, language_pair
                    )
        except Exception as e:
            CIRCUIT_BREAKER_ERRORS.labels(
                service="yandex_translator"
            ).inc()
            raise

    async def _translate_with_circuit_breaker(
        self, text: str, language_pair: LanguagePair
    ) -> str:
        """Translate text with circuit breaker protection.

        Args:
            text: Text to translate
            language_pair: Source and target language

        Returns:
            Translated text

        Raises:
            TranslationError: If translation fails
        """
        try:
            return await self.circuit_breaker.call(
                self._translate_impl, text, language_pair
            )
        except Exception as e:
            if "CircuitBreakerListener" in str(type(e)):
                CIRCUIT_BREAKER_STATE.labels(service="yandex_translator").set(1)
                raise TranslationError(
                    f"Circuit breaker open after error: {e}"
                ) from e
            raise

    async def _translate_impl(
        self, text: str, language_pair: LanguagePair
    ) -> str:
        """Internal translation implementation.

        Args:
            text: Text to translate
            language_pair: Source and target language

        Returns:
            Translated text

        Raises:
            TranslationError: If translation fails
        """
        try:
            payload = {
                "sourceLanguageCode": language_pair.source,
                "targetLanguageCode": language_pair.target,
                "texts": [text],
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Api-Key {self.api_key}",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.BASE_URL,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise TranslationError(
                            f"API error: {response.status} - {error_text}"
                        )

                    result = await response.json()
                    translations = result.get("translations", [])

                    if not translations:
                        raise TranslationError("No translation in response")

                    return translations[0].get("text", "")

        except aiohttp.ClientError as e:
            raise TranslationError(f"Network error during translation: {e}") from e
        except TranslationError:
            raise
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise TranslationError(f"Translation service error: {e}") from e

    async def translate_text(
        self, text: str, language_pair: LanguagePair | None = None
    ) -> str:
        """Translate text (port interface).

        Args:
            text: Text to translate
            language_pair: Source and target language (optional)

        Returns:
            Translated text
        """
        return await self.translate(text, language_pair)
