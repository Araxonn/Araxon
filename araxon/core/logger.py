"""Logging configuration for ARAXON."""
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

logger = _setup_logger()