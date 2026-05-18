"""Utility functions for ARAXON."""
import asyncio
import re
from datetime import datetime
from typing import Callable, Any
from araxon.core.logger import logger

async def async_retry(func: Callable, retries: int = 3, delay: float = 1.0, *args, **kwargs) -> Any:
    """Retry an async function multiple times on failure."""
    last_exception = None
    for attempt in range(retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < retries - 1:
                logger.warning(f"Attempt {attempt + 1}/{retries} failed: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {retries} retry attempts failed")
    raise last_exception

def sanitize_text(text: str) -> str:
    """Sanitize text for TTS."""
    text = re.sub(r"[^\w\s.,!?\'-]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def get_timestamp() -> str:
    """Get current datetime as ISO format string."""
    return datetime.now().isoformat(timespec="milliseconds")

def chunk_text(text: str, size: int = 200) -> list[str]:
    """Split long text into chunks for TTS."""
    if len(text) <= size:
        return [text]
    chunks = []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks