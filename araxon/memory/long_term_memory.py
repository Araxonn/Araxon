"""High-level persistent memory manager for ARAXON."""

from __future__ import annotations

from araxon.core.logger import logger

from .rag_pipeline import RAGPipeline
from .vector_store import ARAxonVectorStore


class LongTermMemory:
    """Coordinate persistent conversation memory, facts, and retrieval."""

    def __init__(self, vector_store: ARAxonVectorStore | None = None) -> None:
        """Create the long-term memory manager and its retrieval pipeline."""

        self.vector_store = vector_store or ARAxonVectorStore()
        self.rag_pipeline = RAGPipeline(self.vector_store)

    async def save_exchange(self, user_text: str, assistant_text: str) -> None:
        """Persist one completed conversation exchange in the background."""

        try:
            await self.vector_store.add_conversation(user_text=user_text, assistant_text=assistant_text)
        except Exception as exc:
            logger.warning(f"Failed to save long-term exchange: {exc}")

    async def recall(self, query: str) -> str:
        """Return relevant memories and files for a query."""

        return await self.rag_pipeline.retrieve(query)

    async def remember_fact(self, fact: str) -> None:
        """Store a standalone fact or note as a conversation memory entry."""

        try:
            await self.vector_store.add_conversation(
                user_text=fact,
                assistant_text="Remembered fact.",
                metadata={"type": "fact", "topic": "fact"},
            )
            logger.info("Stored a remembered fact in long-term memory.")
        except Exception as exc:
            logger.warning(f"Failed to store remembered fact: {exc}")

    async def get_stats(self) -> str:
        """Return a human-readable summary of stored memories and files."""

        stats = await self.vector_store.get_collection_stats()
        return f"I have {stats['conversations_count']} memories and {stats['files_count']} ingested files stored."

    async def clear_all(self, confirmed: bool = False) -> None:
        """Clear all memory data only after explicit confirmation."""

        if not confirmed:
            logger.info("Long-term memory clear_all request ignored because confirmation was not provided.")
            return

        try:
            await self.vector_store.clear_conversations()
            await self.vector_store.clear_files()
            logger.info("Long-term memory cleared.")
        except Exception as exc:
            logger.warning(f"Failed to clear long-term memory: {exc}")