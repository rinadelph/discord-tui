"""Constants for Discordo."""

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

DISCORDO_NAME = "discordo"


def _init_cache_dir() -> Path:
    """Initialize and return the cache directory path."""
    try:
        cache_dir = Path(os.path.expanduser("~/.cache")) / DISCORDO_NAME
    except Exception as err:
        logger.warning(f"failed to get user cache dir; falling back to temp dir: {err}")
        cache_dir = Path(os.path.expanduser("~")) / ".cache" / DISCORDO_NAME
    
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
    except Exception as err:
        logger.error(f"failed to create cache dir at {cache_dir}: {err}")
    
    return cache_dir


_CACHE_DIR = _init_cache_dir()


def cache_dir() -> Path:
    """Return the cache directory path."""
    return _CACHE_DIR
