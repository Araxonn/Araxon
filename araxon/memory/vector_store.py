"""ChromaDB-backed vector store for ARAXON memory and file retrieval."""

from __future__ import annotations

import asyncio
import time
from datetime import datetime
from pathlib import Path

import chromadb

from araxon.core.config import settings
from araxon.core.logger import logger
from araxon.core.utils import chunk_text

from .embedder import LocalEmbedder


class ARAxonVectorStore:
    """Wrap ChromaDB collections for conversation and file memory."""

    def __init__(self) -> None:
        """Create the persistent ChromaDB client and required collections."""

        self._embedder = LocalEmbedder()
        self._db_path = Path(settings.CHROMA_DB_PATH)
        self._db_path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(self._db_path))
        self._conversations = None
        self._files = None
        self._initialize_collections()

    def _initialize_collections(self) -> None:
        """Create the ChromaDB collections used by ARAXON."""

        try:
            self._conversations = self._client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_CONVERSATIONS,
                metadata={"hnsw:space": "cosine"},
            )
            self._files = self._client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_FILES,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("ARAXON vector store collections are ready.")
        except Exception as exc:
            logger.error(f"Failed to initialize ARAXON vector store collections: {exc}")
            raise

    def _collection_ready(self, collection: object | None, collection_name: str) -> bool:
        """Check whether a collection reference is available."""

        if collection is None:
            logger.error(f"ChromaDB collection is not ready: {collection_name}")
            return False
        return True

    def _build_document_id(self, session_id: str, timestamp: str, text: str, suffix: str = "") -> str:
        """Build a unique document identifier for ChromaDB."""

        base_id = f"{session_id}_{timestamp}_{hash(text)}"
        return f"{base_id}_{suffix}" if suffix else base_id

    def _detect_topic(self, text: str) -> str:
        """Infer a simple topic label from a memory entry."""

        normalized = str(text).lower()
        topic_map = {
            "voice": ["voice", "speak", "listen", "mic", "microphone"],
            "project": ["project", "code", "repo", "file", "folder", "build"],
            "preference": ["prefer", "like", "dark mode", "theme", "always", "never"],
            "identity": ["my name", "i am", "call me", "remember me"],
        }
        for topic, keywords in topic_map.items():
            if any(keyword in normalized for keyword in keywords):
                return topic
        return "general"

    async def add_conversation(
        self,
        user_text: str,
        assistant_text: str,
        metadata: dict = {},
    ) -> None:
        """Store a single user/assistant exchange in the conversation collection."""

        start_time = time.monotonic()
        if not self._collection_ready(self._conversations, settings.CHROMA_COLLECTION_CONVERSATIONS):
            return

        session_id = str(metadata.get("session_id", "default"))
        timestamp = datetime.utcnow().isoformat(timespec="milliseconds")
        document_text = f"User: {user_text}\nARAXON: {assistant_text}"
        document_id = self._build_document_id(session_id, timestamp, document_text)
        payload_metadata = {
            **metadata,
            "timestamp": timestamp,
            "session_id": session_id,
            "topic": metadata.get("topic") or self._detect_topic(document_text),
            "type": metadata.get("type", "conversation"),
        }

        try:
            embedding = await asyncio.to_thread(self._embedder.embed, document_text)
            await asyncio.to_thread(
                self._conversations.add,
                ids=[document_id],
                documents=[document_text],
                embeddings=[embedding],
                metadatas=[payload_metadata],
            )
            elapsed_seconds = time.monotonic() - start_time
            logger.info(f"Stored conversation memory id={document_id} in {elapsed_seconds:.2f}s.")
        except Exception as exc:
            logger.warning(f"Failed to store conversation memory: {exc}")

    async def search_conversations(self, query: str, n_results: int = 5) -> list[dict]:
        """Search stored conversations for semantically relevant memories."""

        start_time = time.monotonic()
        if not self._collection_ready(self._conversations, settings.CHROMA_COLLECTION_CONVERSATIONS):
            return []

        try:
            query_embedding = await asyncio.to_thread(self._embedder.embed, query)
            result = await asyncio.to_thread(
                self._conversations.query,
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )
            documents = (result.get("documents") or [[]])[0]
            metadatas = (result.get("metadatas") or [[]])[0]
            distances = (result.get("distances") or [[]])[0]
            search_results: list[dict] = []
            for document, metadata, distance in zip(documents, metadatas, distances):
                similarity_score = max(0.0, 1.0 - float(distance or 0.0))
                search_results.append(
                    {
                        "text": document,
                        "similarity_score": similarity_score,
                        "timestamp": metadata.get("timestamp", ""),
                        "metadata": metadata,
                    }
                )
            elapsed_seconds = time.monotonic() - start_time
            logger.info(f"Conversation search returned {len(search_results)} result(s) in {elapsed_seconds:.2f}s.")
            return search_results
        except Exception as exc:
            logger.warning(f"Conversation search failed: {exc}")
            return []

    async def add_file(
        self,
        content: str,
        filename: str,
        metadata: dict = {},
    ) -> int:
        """Split file content into chunks and store the chunks in the file collection."""

        start_time = time.monotonic()
        if not self._collection_ready(self._files, settings.CHROMA_COLLECTION_FILES):
            return 0

        chunks = chunk_text(content, size=500)
        timestamp = datetime.utcnow().isoformat(timespec="milliseconds")
        base_metadata = {
            **metadata,
            "filename": filename,
            "file_type": metadata.get("file_type") or Path(filename).suffix.lstrip(".").lower() or "txt",
            "ingested_at": metadata.get("ingested_at", timestamp),
        }

        try:
            ids: list[str] = []
            documents: list[str] = []
            embeddings: list[list[float]] = []
            metadatas: list[dict] = []
            for index, chunk in enumerate(chunks):
                chunk_id = self._build_document_id(filename, timestamp, f"{filename}:{chunk}", str(index))
                ids.append(chunk_id)
                documents.append(chunk)
                embeddings.append(await asyncio.to_thread(self._embedder.embed, chunk))
                metadatas.append({**base_metadata, "chunk_index": index, "chunk_count": len(chunks)})

            if ids:
                await asyncio.to_thread(
                    self._files.add,
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                )
            elapsed_seconds = time.monotonic() - start_time
            logger.info(f"Stored {len(ids)} file chunk(s) for {filename} in {elapsed_seconds:.2f}s.")
            return len(ids)
        except Exception as exc:
            logger.warning(f"Failed to store file content for {filename}: {exc}")
            return 0

    async def search_files(self, query: str, n_results: int = 3) -> list[dict]:
        """Search ingested files for semantically relevant chunks."""

        start_time = time.monotonic()
        if not self._collection_ready(self._files, settings.CHROMA_COLLECTION_FILES):
            return []

        try:
            query_embedding = await asyncio.to_thread(self._embedder.embed, query)
            result = await asyncio.to_thread(
                self._files.query,
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )
            documents = (result.get("documents") or [[]])[0]
            metadatas = (result.get("metadatas") or [[]])[0]
            distances = (result.get("distances") or [[]])[0]
            search_results: list[dict] = []
            for document, metadata, distance in zip(documents, metadatas, distances):
                similarity_score = max(0.0, 1.0 - float(distance or 0.0))
                search_results.append(
                    {
                        "text": document,
                        "similarity_score": similarity_score,
                        "timestamp": metadata.get("ingested_at", metadata.get("timestamp", "")),
                        "metadata": metadata,
                    }
                )
            elapsed_seconds = time.monotonic() - start_time
            logger.info(f"File search returned {len(search_results)} result(s) in {elapsed_seconds:.2f}s.")
            return search_results
        except Exception as exc:
            logger.warning(f"File search failed: {exc}")
            return []

    async def get_collection_stats(self) -> dict:
        """Return basic statistics for the persistent ChromaDB collections."""

        if not self._collection_ready(self._conversations, settings.CHROMA_COLLECTION_CONVERSATIONS):
            conversations_count = 0
        else:
            try:
                conversations_count = await asyncio.to_thread(self._conversations.count)
            except Exception as exc:
                logger.warning(f"Failed to count conversation memories: {exc}")
                conversations_count = 0

        if not self._collection_ready(self._files, settings.CHROMA_COLLECTION_FILES):
            files_count = 0
        else:
            try:
                files_count = await asyncio.to_thread(self._files.count)
            except Exception as exc:
                logger.warning(f"Failed to count file memories: {exc}")
                files_count = 0

        stats = {
            "conversations_count": conversations_count,
            "files_count": files_count,
            "db_path": str(self._db_path),
        }
        logger.info(f"Vector store stats: conversations={conversations_count}, files={files_count}, db_path={self._db_path}")
        return stats

    async def clear_conversations(self) -> None:
        """Delete all stored conversation memories without touching file memories."""

        if not self._collection_ready(self._conversations, settings.CHROMA_COLLECTION_CONVERSATIONS):
            return

        start_time = time.monotonic()
        try:
            payload = await asyncio.to_thread(self._conversations.get, include=[])
            ids = payload.get("ids") or []
            if ids:
                await asyncio.to_thread(self._conversations.delete, ids=ids)
            elapsed_seconds = time.monotonic() - start_time
            logger.info(f"Cleared {len(ids)} conversation memory item(s) in {elapsed_seconds:.2f}s.")
        except Exception as exc:
            logger.warning(f"Failed to clear conversation memories: {exc}")

    async def clear_files(self) -> None:
        """Delete all stored file chunks from the file collection."""

        if not self._collection_ready(self._files, settings.CHROMA_COLLECTION_FILES):
            return

        start_time = time.monotonic()
        try:
            payload = await asyncio.to_thread(self._files.get, include=[])
            ids = payload.get("ids") or []
            if ids:
                await asyncio.to_thread(self._files.delete, ids=ids)
            elapsed_seconds = time.monotonic() - start_time
            logger.info(f"Cleared {len(ids)} file memory item(s) in {elapsed_seconds:.2f}s.")
        except Exception as exc:
            logger.warning(f"Failed to clear file memories: {exc}")