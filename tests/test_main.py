"""
Package Name: agentic_bookkeeper
File Name: test_main.py
Description: Unit tests for main module
Author: Stephen Bogner, P.Eng.
LLM: claude-sonnet-4-5-20250929
Ownership: Stephen Bogner - All Rights Reserved.  See LICENSE.md
Date Created: 2025-10-24
"""

import pytest
import logging
from pathlib import Path
from agentic_bookkeeper.main import main, configure_logging


class TestConfigureLogging:
    """Test cases for configure_logging function."""

    def test_configure_logging_default(self):
        """Test logging configuration with default settings."""
        configure_logging()
        logger = logging.getLogger(__name__)
        assert logger.isEnabledFor(logging.INFO)

    def test_configure_logging_debug_level(self):
        """Test logging configuration with DEBUG level."""
        configure_logging(log_level="DEBUG")
        logger = logging.getLogger(__name__)
        assert logger.isEnabledFor(logging.DEBUG)

    def test_configure_logging_with_file(self, tmp_path):
        """Test logging configuration with file output."""
        log_file = tmp_path / "test.log"
        configure_logging(log_level="INFO", log_file=str(log_file))

        logger = logging.getLogger(__name__)
        logger.info("Test message")

        assert log_file.exists()
        assert "Test message" in log_file.read_text()


class TestMain:
    """Test cases for main function."""

    def test_main_returns_zero_on_success(self):
        """Test that main function returns 0 on success."""
        result = main()
        assert result == 0

    def test_main_executes_without_errors(self):
        """Test that main function executes without raising exceptions."""
        try:
            result = main()
            assert isinstance(result, int)
        except Exception as e:
            pytest.fail(f"main() raised an unexpected exception: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
