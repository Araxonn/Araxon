#!/usr/bin/env python3
"""
Complete ARAXON Project Setup Script

This script creates the entire project structure including all directories
and Python module files. Run this once after cloning the repository.

Usage:
    python setup_project.py
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()

# Define file structure: path -> content
FILE_STRUCTURE = {
    # Package files
    "araxon/__init__.py": '''"""
ARAXON - A futuristic modular AI operating system.

This package provides the core components and integrations for building
advanced AI applications with voice, vision, memory, and automation capabilities.
"""

__version__ = "0.1.0"
__author__ = "ARAXON Team"
''',
    "araxon/core/__init__.py": '''"""
Core module for ARAXON.

Provides configuration management, logging, and utility functions.
"""

from araxon.core.config import settings
from araxon.core.logger import logger

__all__ = ["settings", "logger"]
''',
    "araxon/core/config.py": '''"""
Configuration management for ARAXON.

Uses pydantic-settings to load configuration from .env file and environment variables.
Provides a global settings object for use throughout the application.
"""

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
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings object for use throughout the application
settings = Settings()
''',
    "araxon/core/logger.py": '''"""
Logging configuration for ARAXON.

Uses loguru for structured logging with both console and file output.
Provides a global logger object for use throughout the application.
"""

import sys
from pathlib import Path
from loguru import logger as _loguru_logger

from araxon.core.config import settings


def _setup_logger():
    """
    Configure loguru with terminal and file sinks.

    - Terminal output: Rich-formatted with colors
    - File output: logs/araxon.log with 10MB rotation
    """
    # Remove default handler
    _loguru_logger.remove()

    # Sink 1: Terminal output with rich formatting
    _loguru_logger.add(
        sys.stderr,
        format="<level>{time:YYYY-MM-DD HH:mm:ss.SSS}</level> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    # Sink 2: File output with rotation at 10MB
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


# Global logger object - initialized on module import
logger = _setup_logger()
''',
    "araxon/core/utils.py": '''"""
Utility functions for ARAXON.

Provides common async operations, text sanitization, and data chunking utilities.
"""

import asyncio
import re
from datetime import datetime
from typing import Callable, Any
from araxon.core.logger import logger


async def async_retry(
    func: Callable, retries: int = 3, delay: float = 1.0, *args, **kwargs
) -> Any:
    """
    Retry an async function multiple times on failure.

    Args:
        func: Async function to retry
        retries: Number of retry attempts
        delay: Delay between retries in seconds
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Result of func execution

    Raises:
        Exception: If all retries fail
    """
    last_exception = None

    for attempt in range(retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < retries - 1:
                logger.warning(
                    f"Attempt {attempt + 1}/{retries} failed: {e}. Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {retries} retry attempts failed")

    raise last_exception


def sanitize_text(text: str) -> str:
    """
    Sanitize text for TTS (Text-To-Speech).

    Removes special characters and extra whitespace that may cause issues with TTS engines.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text safe for TTS
    """
    # Remove special characters but keep basic punctuation
    text = re.sub(r"[^\\w\\s.,!?\\'-]", "", text)
    # Remove extra whitespace
    text = re.sub(r"\\s+", " ", text).strip()
    return text


def get_timestamp() -> str:
    """
    Get current datetime as a clean ISO format string.

    Returns:
        Current datetime in ISO format with millisecond precision
    """
    return datetime.now().isoformat(timespec="milliseconds")


def chunk_text(text: str, size: int = 200) -> list[str]:
    """
    Split long text into chunks suitable for TTS.

    Chunks at sentence boundaries when possible to maintain natural pauses.

    Args:
        text: Text to chunk
        size: Maximum characters per chunk

    Returns:
        List of text chunks
    """
    if len(text) <= size:
        return [text]

    chunks = []
    # Split by sentences first
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

    return chunks
''',
    # Module init files
    "araxon/ai/__init__.py": '''"""
AI module for ARAXON.

Provides AI model integration and inference capabilities.
"""
''',
    "araxon/voice/__init__.py": '''"""
Voice module for ARAXON.

Provides speech recognition and text-to-speech capabilities.
"""
''',
    "araxon/memory/__init__.py": '''"""
Memory module for ARAXON.

Provides persistent memory and knowledge base management.
"""
''',
    "araxon/vision/__init__.py": '''"""
Vision module for ARAXON.

Provides image processing and computer vision capabilities.
"""
''',
    "araxon/automation/__init__.py": '''"""
Automation module for ARAXON.

Provides task automation and workflow orchestration.
"""
''',
    "araxon/agent/__init__.py": '''"""
Agent module for ARAXON.

Provides autonomous agent capabilities and orchestration.
"""
''',
    "araxon/internet/__init__.py": '''"""
Internet module for ARAXON.

Provides web browsing and API integration capabilities.
"""
''',
    "araxon/ui/__init__.py": '''"""
UI module for ARAXON.

Provides user interface components and interactive features.
"""
''',
    # Configuration files
    "config/settings.yaml": '''# ARAXON Configuration File
# This file is reserved for future use with advanced configuration options

app:
  name: ARAXON
  version: 0.1.0
  description: A futuristic modular AI operating system

features:
  # Voice Pipeline
  voice:
    enabled: false
    # STEP 2: voice pipeline configuration will go here

  # Vision Pipeline
  vision:
    enabled: false
    # STEP 3: vision pipeline configuration will go here

  # Memory System
  memory:
    enabled: false
    # STEP 4: memory system configuration will go here

  # Automation Engine
  automation:
    enabled: false
    # STEP 5: automation engine configuration will go here

  # Agent System
  agents:
    enabled: false
    # STEP 6: agent system configuration will go here

  # Internet Integration
  internet:
    enabled: false
    # STEP 7: internet integration configuration will go here

  # UI System
  ui:
    enabled: false
    # STEP 8: UI system configuration will go here
''',
}


def create_directories():
    """Create all necessary directories."""
    directories = [
        "araxon/core",
        "araxon/ai",
        "araxon/voice",
        "araxon/memory",
        "araxon/vision",
        "araxon/automation",
        "araxon/agent",
        "araxon/internet",
        "araxon/ui",
        "config",
        "logs",
        "models",
        "data",
    ]

    for directory in directories:
        dir_path = PROJECT_ROOT / directory
        dir_path.mkdir(parents=True, exist_ok=True)


def create_files():
    """Create all project files."""
    for file_path, content in FILE_STRUCTURE.items():
        full_path = PROJECT_ROOT / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        if full_path.exists():
            print(f"   ⊘ {file_path} (already exists)")
        else:
            full_path.write_text(content, encoding="utf-8")
            print(f"   ✓ {file_path}")


def main():
    """Main setup function."""
    print("\n🚀 ARAXON Project Setup\n")
    print("📁 Creating directories...")
    create_directories()
    print("\n📄 Creating Python modules and configuration files...")
    create_files()
    print("\n✅ Setup complete!")
    print(f"   Project root: {PROJECT_ROOT}\n")
    
    print("Next steps:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Configure .env: cp .env.example .env")
    print("  3. Run ARAXON: python main.py\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
