"""Short-term conversational memory for ARAXON."""

from __future__ import annotations

from araxon.core.config import settings
from araxon.core.logger import logger

from .personality import get_system_prompt


class ConversationMemory:
    """Maintain a short in-memory history of user and assistant messages."""

    def __init__(self) -> None:
        """Initialize an empty conversation history buffer."""

        self._history: list[dict[str, str]] = []

    def _append(self, role: str, text: str) -> None:
        """Add a message to history and trim old messages if needed."""

        message = {"role": role, "content": str(text).strip()}
        self._history.append(message)
        self._trim_history()

    def _trim_history(self) -> None:
        """Remove the oldest messages when the memory buffer grows too large."""

        max_messages = max(0, int(settings.MAX_MEMORY_TURNS))
        if max_messages == 0 or len(self._history) <= max_messages:
            return

        removed = 0
        while len(self._history) > max_messages:
            remove_count = 2 if len(self._history) - 2 >= max_messages else 1
            del self._history[:remove_count]
            removed += remove_count

        logger.info(
            f"Conversation memory trimmed by {removed} message(s) to keep {max_messages} message(s)."
        )

    def add_user(self, text: str) -> None:
        """Add a user message to the conversation history."""

        self._append("user", text)

    def add_assistant(self, text: str) -> None:
        """Add an assistant message to the conversation history."""

        self._append("assistant", text)

    def get_history(self) -> list[dict[str, str]]:
        """Return a copy of the current conversation history."""

        return [message.copy() for message in self._history]

    def get_context_messages(self) -> list[dict[str, str]]:
        """Return the system prompt followed by the latest context messages."""

        return [{"role": "system", "content": get_system_prompt()}] + self._history[-settings.MAX_MEMORY_TURNS :]

    def clear(self) -> None:
        """Clear all stored conversation history."""

        self._history.clear()
        logger.info("Conversation memory cleared.")

    def summarize(self) -> str:
        """Summarize the current short-term memory in one spoken line."""

        if not self._history:
            return "0 turns, last topic: none"

        last_user_message = "none"
        for message in reversed(self._history):
            if message.get("role") == "user":
                last_user_message = message.get("content", "none") or "none"
                break

        turn_count = (len(self._history) + 1) // 2
        return f"{turn_count} turns, last topic: {last_user_message}"