"""Local embedding engine for ARAXON memory and retrieval."""

from __future__ import annotations

import asyncio
import os
import time
from threading import Lock

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_TORCH", "1")

from sentence_transformers import SentenceTransformer

from araxon.core.config import settings
from araxon.core.logger import logger


class LocalEmbedder:
    """Load and serve a singleton SentenceTransformer embedding model."""

    _instance: LocalEmbedder | None = None
    _instance_lock: Lock = Lock()

    def __new__(cls) -> LocalEmbedder:
        """Return the shared LocalEmbedder instance."""

        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
                    cls._instance._model = None
        return cls._instance

    def __init__(self) -> None:
        """Initialize the shared embedding model on first use."""

        if getattr(self, "_initialized", False):
            return

        start_time = time.monotonic()
        logger.info(f"Loading embedding model {settings.EMBEDDING_MODEL}...")
        self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
        elapsed_seconds = time.monotonic() - start_time
        logger.info(f"Embedding model {settings.EMBEDDING_MODEL} loaded in {elapsed_seconds:.2f}s.")
        self._initialized = True

    def _ensure_model(self) -> SentenceTransformer:
        """Return the loaded SentenceTransformer model."""

        if self._model is None:
            raise RuntimeError("Embedding model failed to initialize.")
        return self._model

    def embed(self, text: str) -> list[float]:
        """Embed a single text string into a vector."""

        model = self._ensure_model()
        vector = model.encode([str(text)], convert_to_numpy=True, normalize_embeddings=False)[0]
        return [float(value) for value in vector.tolist()]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple text strings into vectors."""

        model = self._ensure_model()
        vectors = model.encode([str(text) for text in texts], convert_to_numpy=True, normalize_embeddings=False)
        return [[float(value) for value in vector.tolist()] for vector in vectors]


async def embed_text(text: str) -> list[float]:
    """Embed text in a worker thread using the shared LocalEmbedder instance."""

    return await asyncio.to_thread(LocalEmbedder().embed, text)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed multiple texts in a worker thread using the shared LocalEmbedder instance."""

    return await asyncio.to_thread(LocalEmbedder().embed_batch, texts)