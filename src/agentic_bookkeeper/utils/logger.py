"""
Logging configuration for Agentic Bookkeeper.

This module sets up structured logging with file and console handlers,
log rotation, and sensitive data filtering.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import re


class SensitiveDataFilter(logging.Filter):
    """
    Filter to remove sensitive data from log messages.

    Filters out:
    - API keys
    - Tokens
    - Passwords
    - Credit card numbers
    """

    # Patterns for sensitive data
    PATTERNS = [
        (re.compile(r'(api[_-]?key|token|password|secret)["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', re.IGNORECASE), r'\1=***'),
        (re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE), 'Bearer ***'),
        (re.compile(r'sk-[A-Za-z0-9]{48}'), 'sk-***'),  # OpenAI API key pattern
        (re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'), '****-****-****-****'),  # Credit card
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record to remove sensitive data.

        Args:
            record: Log record to filter

        Returns:
            True (record is always allowed, just modified)
        """
        record.msg = self._sanitize(str(record.msg))
        if record.args:
            record.args = tuple(self._sanitize(str(arg)) for arg in record.args)
        return True

    def _sanitize(self, text: str) -> str:
        """
        Remove sensitive data from text.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        for pattern, replacement in self.PATTERNS:
            text = pattern.sub(replacement, text)
        return text


class LoggerSetup:
    """
    Configure application logging.

    Sets up:
    - Console handler with color support (if available)
    - File handler with rotation
    - Sensitive data filtering
    - Structured log formatting
    """

    def __init__(
        self,
        log_file: str = "./logs/agentic_bookkeeper.log",
        log_level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True
    ):
        """
        Initialize logger configuration.

        Args:
            log_file: Path to log file
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Maximum log file size before rotation
            backup_count: Number of backup files to keep
            console_output: Whether to output to console
        """
        self.log_file = Path(log_file)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.console_output = console_output

        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def setup(self) -> logging.Logger:
        """
        Set up logging configuration.

        Returns:
            Root logger
        """
        # Get root logger
        logger = logging.getLogger()
        logger.setLevel(self.log_level)

        # Remove existing handlers
        logger.handlers.clear()

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            filename=str(self.log_file),
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(detailed_formatter)
        file_handler.addFilter(SensitiveDataFilter())
        logger.addHandler(file_handler)

        # Console handler
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(simple_formatter)
            console_handler.addFilter(SensitiveDataFilter())
            logger.addHandler(console_handler)

        # Log initialization
        logger.info("="*60)
        logger.info("Agentic Bookkeeper - Logging Initialized")
        logger.info(f"Log Level: {logging.getLevelName(self.log_level)}")
        logger.info(f"Log File: {self.log_file}")
        logger.info("="*60)

        return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def setup_logging(
    log_file: Optional[str] = None,
    log_level: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Convenience function to set up logging.

    Args:
        log_file: Path to log file (defaults to config value)
        log_level: Logging level (defaults to config value)
        console_output: Whether to output to console

    Returns:
        Root logger
    """
    # Import here to avoid circular dependency
    from ..utils.config import Config

    # Load config if not provided
    config = Config()
    if log_file is None:
        log_file = str(config.get_log_file())
    if log_level is None:
        log_level = config.get_log_level()

    # Set up logger
    logger_setup = LoggerSetup(
        log_file=log_file,
        log_level=log_level,
        console_output=console_output
    )

    return logger_setup.setup()


# Context manager for temporary log level changes
class temporary_log_level:
    """
    Context manager to temporarily change log level.

    Example:
        with temporary_log_level(logging.DEBUG):
            # Debug logging enabled
            logger.debug("Detailed debug info")
        # Back to original level
    """

    def __init__(self, level: int):
        """
        Initialize context manager.

        Args:
            level: Temporary logging level
        """
        self.level = level
        self.original_level = None

    def __enter__(self):
        """Set temporary log level."""
        logger = logging.getLogger()
        self.original_level = logger.level
        logger.setLevel(self.level)
        for handler in logger.handlers:
            handler.setLevel(self.level)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original log level."""
        logger = logging.getLogger()
        logger.setLevel(self.original_level)
        for handler in logger.handlers:
            handler.setLevel(self.original_level)
        return False
