"""Model routing between Groq cloud and Ollama local inference."""

from __future__ import annotations

import httpx

from araxon.core.config import settings
from araxon.core.logger import logger


class ModelRouter:
    """Select the best LiteLLM backend for the current ARAXON session."""

    def __init__(self) -> None:
        """Initialize the backend cache."""

        self._last_working_backend: str | None = None

    def get_litellm_model_string(self, backend: str) -> str:
        """Convert a backend name into the model string LiteLLM expects."""

        normalized_backend = backend.strip().lower()
        if normalized_backend == "ollama":
            return f"ollama/{settings.OLLAMA_MODEL}"
        return f"groq/{settings.GROQ_MODEL}"

    async def is_ollama_available(self) -> bool:
        """Check whether the local Ollama service is reachable."""

        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(settings.OLLAMA_BASE_URL)
                available = response.status_code < 500
        except Exception as exc:
            logger.info(f"Ollama availability check failed: {exc}")
            return False

        logger.info(f"Ollama availability check returned {available}.")
        return available

    def mark_backend_success(self, backend: str) -> None:
        """Remember the backend that most recently completed a successful call."""

        normalized_backend = backend.strip().lower()
        if normalized_backend in {"groq", "ollama"}:
            self._last_working_backend = normalized_backend

    async def get_model(self) -> str:
        """Return the LiteLLM model string for the selected backend."""

        preferred_backend = settings.PREFERRED_BACKEND.strip().lower()
        selected_backend = "groq"

        if preferred_backend == "ollama":
            selected_backend = "ollama"
        elif preferred_backend == "auto":
            cached_backend = self._last_working_backend
            if cached_backend == "ollama" and await self.is_ollama_available():
                selected_backend = "ollama"
            elif cached_backend == "groq" and settings.GROQ_API_KEY:
                selected_backend = "groq"
            elif await self.is_ollama_available():
                selected_backend = "ollama"
            elif settings.GROQ_API_KEY:
                selected_backend = "groq"
        elif preferred_backend == "groq":
            selected_backend = "groq"

        self._last_working_backend = selected_backend
        logger.info(f"Model router selected backend: {selected_backend}.")
        return self.get_litellm_model_string(selected_backend)