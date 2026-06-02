"""Retrieval-augmented generation pipeline for ARAXON memory context injection."""

from __future__ import annotations

from typing import Iterable

from araxon.core.config import settings
from araxon.core.logger import logger

from .vector_store import ARAxonVectorStore


class RAGPipeline:
    """Retrieve relevant memory and file context for ARAXONBrain prompts."""

    def __init__(self, vector_store: ARAxonVectorStore) -> None:
        """Store the vector store reference used for retrieval."""

        self.vector_store = vector_store

    def _format_section(self, heading: str, items: Iterable[dict]) -> tuple[str, int]:
        """Format a retrieval result section into a readable bullet list."""

        lines = [heading]
        count = 0
        for item in items:
            text = str(item.get("text", "")).strip()
            if not text:
                continue
            lines.append(f"- {text}")
            count += 1
        return "\n".join(lines), count

    async def retrieve(self, query: str) -> str:
        """Retrieve and format relevant memories and files for a query."""

        if not settings.RAG_ENABLED:
            return ""

        conversation_results = await self.vector_store.search_conversations(query, n_results=settings.RAG_MAX_RESULTS)
        file_results = await self.vector_store.search_files(query, n_results=2)

        filtered_conversations = [
            result for result in conversation_results if result.get("similarity_score", 0.0) >= settings.RAG_SIMILARITY_THRESHOLD
        ]
        filtered_files = [
            result for result in file_results if result.get("similarity_score", 0.0) >= settings.RAG_SIMILARITY_THRESHOLD
        ]

        if not filtered_conversations and not filtered_files:
            return ""

        sections: list[str] = []
        memory_section, memory_count = self._format_section("Relevant memory:", filtered_conversations)
        if memory_count:
            sections.append(memory_section)

        file_section, file_count = self._format_section("Relevant files:", filtered_files)
        if file_count:
            sections.append(file_section)

        context = "\n\n".join(sections).strip()
        logger.info(
            f"RAG retrieved {memory_count} memory result(s) and {file_count} file result(s) for context injection."
        )
        return context

    async def build_enhanced_messages(
        self,
        user_input: str,
        base_messages: list[dict],
    ) -> list[dict]:
        """Inject retrieved context into the system message when relevant context exists."""

        if not settings.RAG_ENABLED:
            return base_messages

        context = await self.retrieve(user_input)
        if not context:
            return base_messages

        enhanced_messages = [message.copy() for message in base_messages]
        if settings.RAG_INJECT_INTO_SYSTEM and enhanced_messages:
            system_message = enhanced_messages[0]
            if system_message.get("role") == "system":
                system_message["content"] = f"{system_message.get('content', '')}\n\n{context}".strip()
            else:
                enhanced_messages.insert(0, {"role": "system", "content": context})
        else:
            enhanced_messages.insert(0, {"role": "system", "content": context})

        logger.info("RAG context injected into the system prompt.")
        return enhanced_messages

    async def should_use_rag(self, user_input: str) -> bool:
        """Decide whether a user input benefits from retrieval augmentation."""

        normalized = str(user_input).strip().lower()
        if not normalized:
            return False

        simple_commands = (
            "open chrome",
            "what time is it",
            "time is it",
            "open browser",
            "shutdown",
            "quit",
            "exit",
        )
        if any(command == normalized for command in simple_commands):
            return False

        question_words = ("what", "why", "how", "when", "where", "who", "which", "remember", "recall")
        memory_phrases = ("last time", "my project", "earlier", "before", "you said", "don't forget", "remember that")

        return normalized.endswith("?") or any(word in normalized for word in question_words) or any(
            phrase in normalized for phrase in memory_phrases
        )