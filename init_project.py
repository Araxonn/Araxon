#!/usr/bin/env python3
"""Initialize ARAXON complete project structure with all files."""
import os
from pathlib import Path

root = Path(r"c:\Users\lucky\OneDrive\Desktop\Araxon.worktrees\agents-project-setup-foundation-structure")

# Create all directories
dirs = [
    "araxon/core", "araxon/ai", "araxon/voice", "araxon/memory",
    "araxon/vision", "araxon/automation", "araxon/agent", "araxon/internet",
    "araxon/ui", "config", "logs", "models", "data"
]
for d in dirs:
    (root / d).mkdir(parents=True, exist_ok=True)

# Create files
files = {
    "araxon/__init__.py": '''"""ARAXON - A futuristic modular AI operating system."""
__version__ = "0.1.0"
__author__ = "ARAXON Team"''',
    
    "araxon/core/__init__.py": '''"""Core module for ARAXON."""
from araxon.core.config import settings
from araxon.core.logger import logger
__all__ = ["settings", "logger"]''',
    
    "araxon/core/config.py": '''"""Configuration management for ARAXON."""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""
    APP_NAME: str = "ARAXON"
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = "INFO"
    GROQ_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    WAKE_WORD: str = "araxon"
    CHROMA_DB_PATH: str = "./data/chromadb"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()''',
    
    "araxon/core/logger.py": '''"""Logging configuration for ARAXON."""
import sys
from pathlib import Path
from loguru import logger as _loguru_logger
from araxon.core.config import settings

def _setup_logger():
    """Configure loguru with terminal and file sinks."""
    _loguru_logger.remove()
    _loguru_logger.add(
        sys.stderr,
        format="<level>{time:YYYY-MM-DD HH:mm:ss.SSS}</level> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)
    _loguru_logger.add(
        log_path / "araxon.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name} | {message}",
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        retention="7 days",
    )
    return _loguru_logger

logger = _setup_logger()''',
    
    "araxon/core/utils.py": '''"""Utility functions for ARAXON."""
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
    text = re.sub(r"[^\\w\\s.,!?\\'-]", "", text)
    text = re.sub(r"\\s+", " ", text).strip()
    return text

def get_timestamp() -> str:
    """Get current datetime as ISO format string."""
    return datetime.now().isoformat(timespec="milliseconds")

def chunk_text(text: str, size: int = 200) -> list[str]:
    """Split long text into chunks for TTS."""
    if len(text) <= size:
        return [text]
    chunks = []
    sentences = re.split(r"(?<=[.!?])\\s+", text)
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
    return chunks''',
    
    "araxon/ai/__init__.py": '"""AI module for ARAXON."""',
    "araxon/voice/__init__.py": '"""Voice module for ARAXON."""',
    "araxon/memory/__init__.py": '"""Memory module for ARAXON."""',
    "araxon/vision/__init__.py": '"""Vision module for ARAXON."""',
    "araxon/automation/__init__.py": '"""Automation module for ARAXON."""',
    "araxon/agent/__init__.py": '"""Agent module for ARAXON."""',
    "araxon/internet/__init__.py": '"""Internet module for ARAXON."""',
    "araxon/ui/__init__.py": '"""UI module for ARAXON."""',
    
    "config/settings.yaml": '''app:
  name: ARAXON
  version: 0.1.0
features:
  voice:
    enabled: false
  vision:
    enabled: false
  memory:
    enabled: false
  automation:
    enabled: false
  agents:
    enabled: false
  internet:
    enabled: false
  ui:
    enabled: false''',
}

for fpath, content in files.items():
    full_path = root / fpath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    print(f"✓ {fpath}")

print("\\n✅ ARAXON project structure created successfully!")
