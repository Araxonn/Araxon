"""Core AI brain for ARAXON."""

from __future__ import annotations

import asyncio
import time

import litellm

from araxon.core.config import settings
from araxon.core.logger import logger
from araxon.core.utils import async_retry, sanitize_text

from .memory import ConversationMemory
from .personality import get_system_prompt
from .router import ModelRouter
from araxon.memory import LongTermMemory

litellm.set_verbose = False


class ARAXONBrain:
    """Coordinate conversation memory, backend routing, and LiteLLM responses."""

    def __init__(self, long_term_memory: LongTermMemory = None, ui_bridge=None) -> None:
        """Create the brain with a fresh router and short-term memory."""

        self.memory = ConversationMemory()
        self.router = ModelRouter()
        self.long_term_memory = long_term_memory
        self.ui_bridge = ui_bridge

    def _extract_text(self, completion: object) -> str:
        """Pull assistant text out of a LiteLLM completion response."""

        choices = getattr(completion, "choices", None) or []
        if not choices:
            return ""

        first_choice = choices[0]
        message = getattr(first_choice, "message", None)
        if message is not None:
            content = getattr(message, "content", "")
            if isinstance(content, str):
                return content
            if content is None:
                return ""
            return str(content)

        if isinstance(first_choice, dict):
            message_data = first_choice.get("message") or {}
            content = message_data.get("content", "")
            return content if isinstance(content, str) else str(content)

        content = getattr(first_choice, "content", "")
        return content if isinstance(content, str) else str(content)

    def _extract_total_tokens(self, completion: object) -> str:
        """Return a readable token summary from the LiteLLM usage payload."""

        usage = getattr(completion, "usage", None)
        if usage is None:
            return "unknown"

        total_tokens = getattr(usage, "total_tokens", None)
        if total_tokens is not None:
            return str(total_tokens)

        if isinstance(usage, dict):
            total_tokens = usage.get("total_tokens")
            if total_tokens is not None:
                return str(total_tokens)

        return "unknown"

    def _is_rate_limit_error(self, exc: Exception) -> bool:
        """Detect LiteLLM or provider rate limit failures."""

        error_name = exc.__class__.__name__.lower()
        error_text = str(exc).lower()
        return "ratelimit" in error_name or "rate limit" in error_text or "429" in error_text

    async def _completion(self, model: str, messages: list[dict[str, str]]) -> object:
        """Call LiteLLM with the current ARAXON generation settings."""

        completion_kwargs: dict[str, object] = {
            "model": model,
            "messages": messages,
            "temperature": settings.AI_TEMPERATURE,
            "max_tokens": settings.AI_MAX_TOKENS,
        }
        if model.startswith("groq/") and settings.GROQ_API_KEY:
            completion_kwargs["api_key"] = settings.GROQ_API_KEY
        if model.startswith("ollama/"):
            completion_kwargs["api_base"] = settings.OLLAMA_BASE_URL
        return await litellm.acompletion(**completion_kwargs)

    async def _generate_response(self, messages: list[dict[str, str]]) -> tuple[str, str, str]:
        """Generate one assistant response and return the text plus backend metadata."""

        selected_model = await self.router.get_model()
        selected_backend = selected_model.split("/", 1)[0]

        if selected_backend == "groq" and not settings.GROQ_API_KEY:
            if await self.router.is_ollama_available():
                selected_model = self.router.get_litellm_model_string("ollama")
                selected_backend = "ollama"
                logger.info("Groq API key is missing, so ARAXON is falling back to Ollama for this call.")

        start_time = time.monotonic()
        try:
            completion = await self._completion(selected_model, messages)
        except Exception as exc:
            if selected_backend == "groq" and self._is_rate_limit_error(exc) and await self.router.is_ollama_available():
                logger.warning(f"Groq rate limit reached, switching to Ollama: {exc}")
                selected_backend = "ollama"
                selected_model = self.router.get_litellm_model_string("ollama")
                completion = await self._completion(selected_model, messages)
            else:
                raise

        response_text = sanitize_text(self._extract_text(completion))
        if not response_text:
            raise RuntimeError("LiteLLM returned an empty response.")

        elapsed_seconds = time.monotonic() - start_time
        token_count = self._extract_total_tokens(completion)
        self.router.mark_backend_success(selected_backend)
        logger.info(
            f"ARAXON brain used {selected_backend}, tokens={token_count}, response_time={elapsed_seconds:.2f}s."
        )
        return response_text, selected_backend, token_count

    async def think(self, user_input: str) -> str:
        """Return a response for the given user input without raising exceptions."""

        self.memory.add_user(user_input)
        
        if self.ui_bridge:
            await self.ui_bridge.send_state("thinking")
        
        base_messages = self.memory.get_context_messages()
        messages = base_messages
        if self.long_term_memory and settings.RAG_ENABLED:
            if await self.long_term_memory.rag_pipeline.should_use_rag(user_input):
                messages = await self.long_term_memory.rag_pipeline.build_enhanced_messages(user_input, base_messages)
        # STEP 6: wake system will initialize before this loop
        try:
            response_text, _, _ = await async_retry(self._generate_response, retries=3, delay=1.0, messages=messages)
            self.memory.add_assistant(response_text)
            
            # STEP 11: Send ARAXON transcript to UI
            if self.ui_bridge:
                await self.ui_bridge.send_transcript("assistant", response_text)
            
            if self.long_term_memory:
                asyncio.create_task(self.long_term_memory.save_exchange(user_input, response_text))
            return response_text
        except Exception as exc:
            logger.error(f"ARAXON brain failed after retries: {exc}")
            return "I'm having trouble thinking right now. Please try again in a moment."

    async def recall(self, query: str) -> str:
        """Recall long-term memories for the given query when available."""

        if not self.long_term_memory:
            return "I don't have long-term memory enabled."
        return await self.long_term_memory.recall(query)

    async def reset(self) -> None:
        """Clear the current conversation state."""

        self.memory.clear()
        logger.info("ARAXON brain reset completed.")

    async def warmup(self) -> None:
        """Perform a silent reachability check against the selected model backend."""

        try:
            selected_model = await self.router.get_model()
            selected_backend = selected_model.split("/", 1)[0]
            if selected_backend == "groq" and not settings.GROQ_API_KEY and await self.router.is_ollama_available():
                selected_model = self.router.get_litellm_model_string("ollama")
                selected_backend = "ollama"

            messages = [
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": "hello"},
            ]
            await self._completion(selected_model, messages)
            self.router.mark_backend_success(selected_backend)
            logger.info(f"ARAXON warmup succeeded with {selected_backend}.")
        except Exception as exc:
            logger.warning(f"ARAXON warmup failed: {exc}")