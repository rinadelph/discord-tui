"""Logging configuration for Discordo."""

import logging
import logging.handlers
from pathlib import Path

from discordo.internal.consts import cache_dir

LOG_FILE_NAME = "logs.txt"


def default_path() -> Path:
    """Return the default log file path."""
    return cache_dir() / LOG_FILE_NAME


def setup_logger(path: str, level: int = logging.INFO) -> None:
    """
    Setup the default logger with both file and console handlers.
    
    Args:
        path: Path to the log file
        level: Logging level (e.g., logging.DEBUG, logging.INFO)
    """
    log_path = Path(path)
    
    # Create parent directories if they don't exist
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Create file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
