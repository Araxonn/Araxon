"""File ingestion pipeline for ARAXON project documents and knowledge sources."""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader

from araxon.core.config import settings
from araxon.core.logger import logger

from .vector_store import ARAxonVectorStore


class FileIngester:
    """Load supported local files and index them in the vector store."""

    SUPPORTED_EXTENSIONS = {".txt", ".md", ".py", ".pdf", ".json"}

    def __init__(self, vector_store: ARAxonVectorStore) -> None:
        """Store the vector store reference used for file ingestion."""

        self.vector_store = vector_store

    async def _read_text_file(self, path: Path) -> str:
        """Read a text-like file safely with UTF-8 fallback handling."""

        return await asyncio.to_thread(path.read_text, encoding="utf-8", errors="ignore")

    async def _read_pdf_file(self, path: Path) -> str:
        """Read and combine text from a PDF file using LangChain's PyPDFLoader."""

        documents = await asyncio.to_thread(PyPDFLoader(str(path)).load)
        return "\n\n".join(document.page_content for document in documents)

    async def _read_file_content(self, path: Path) -> str:
        """Dispatch file reading based on file extension."""

        if path.suffix.lower() == ".pdf":
            return await self._read_pdf_file(path)
        if path.suffix.lower() == ".json":
            raw_text = await self._read_text_file(path)
            try:
                parsed = json.loads(raw_text)
                return json.dumps(parsed, indent=2, ensure_ascii=False)
            except Exception:
                return raw_text
        return await self._read_text_file(path)

    async def ingest_file(self, path: str) -> int:
        """Ingest a single supported file and return the number of stored chunks."""

        file_path = Path(path)
        if not file_path.exists() or file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            logger.warning(f"Skipping unsupported or missing file: {file_path}")
            return 0

        start_time = time.monotonic()
        try:
            content = await self._read_file_content(file_path)
            chunks_count = await self.vector_store.add_file(
                content=content,
                filename=file_path.name,
                metadata={"source_path": str(file_path), "file_type": file_path.suffix.lstrip(".").lower()},
            )
            elapsed_seconds = time.monotonic() - start_time
            logger.info(f"Ingested file {file_path.name} with {chunks_count} chunk(s) in {elapsed_seconds:.2f}s.")
            return chunks_count
        except Exception as exc:
            logger.warning(f"Failed to ingest file {file_path}: {exc}")
            return 0

    async def ingest_folder(self, folder_path: str | None = None) -> dict:
        """Ingest every supported file in a folder, skipping duplicates by filename."""

        folder = Path(folder_path or settings.INGESTION_FOLDER)
        folder.mkdir(parents=True, exist_ok=True)

        existing_files = set(await self.list_ingested_files())
        results: dict[str, int] = {}

        for file_path in sorted(folder.rglob("*")):
            if not file_path.is_file() or file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue
            if file_path.name in existing_files:
                logger.info(f"Skipping already ingested file: {file_path.name}")
                continue

            chunks_count = await self.ingest_file(str(file_path))
            results[file_path.name] = chunks_count
            existing_files.add(file_path.name)

        logger.info(f"Folder ingestion complete with {len(results)} file(s) processed.")
        return results

    async def list_ingested_files(self) -> list[str]:
        """Return the filenames of all files already stored in the vector store."""

        try:
            payload = await asyncio.to_thread(self.vector_store._files.get, include=["metadatas"])
            metadatas = payload.get("metadatas") or []
            filenames = sorted({metadata.get("filename", "") for metadata in metadatas if metadata.get("filename")})
            return filenames
        except Exception as exc:
            logger.warning(f"Failed to list ingested files: {exc}")
            return []