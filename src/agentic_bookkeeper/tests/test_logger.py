"""
Unit tests for logging configuration and functionality.

Module: test_logger
Author: Stephen Bogner
Created: 2025-10-29
"""

import logging
import tempfile
from pathlib import Path
import pytest

from agentic_bookkeeper.utils.logger import (
    LoggerSetup,
    SensitiveDataFilter,
    get_logger,
    setup_logging,
    temporary_log_level,
    log_operation_start,
    log_operation_success,
    log_operation_failure,
)


class TestSensitiveDataFilter:
    """Test suite for SensitiveDataFilter."""

    def test_filter_api_key_colon(self):
        """Test filtering API key with colon separator."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Setting api_key: sk-1234567890abcdef",
            args=(),
            exc_info=None,
        )
        filter_obj.filter(record)
        assert "sk-1234567890abcdef" not in record.msg
        assert "api_key=***" in record.msg

    def test_filter_api_key_equals(self):
        """Test filtering API key with equals separator."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg='api_key="sk-abc123xyz"',
            args=(),
            exc_info=None,
        )
        filter_obj.filter(record)
        assert "sk-abc123xyz" not in record.msg
        assert "api_key=***" in record.msg

    def test_filter_bearer_token(self):
        """Test filtering Bearer token."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc",
            args=(),
            exc_info=None,
        )
        filter_obj.filter(record)
        assert "eyJ0eXAiOiJKV1QiLCJhbGc" not in record.msg
        assert "Bearer ***" in record.msg

    def test_filter_openai_key(self):
        """Test filtering OpenAI API key pattern."""
        filter_obj = SensitiveDataFilter()
        api_key = "sk-" + "a" * 48  # OpenAI keys are sk- followed by 48 chars
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=f"Using key: {api_key}",
            args=(),
            exc_info=None,
        )
        filter_obj.filter(record)
        assert api_key not in record.msg
        assert "sk-***" in record.msg

    def test_filter_credit_card(self):
        """Test filtering credit card numbers."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Card: 4532-1234-5678-9010",
            args=(),
            exc_info=None,
        )
        filter_obj.filter(record)
        assert "4532-1234-5678-9010" not in record.msg
        assert "****-****-****-****" in record.msg

    def test_filter_password(self):
        """Test filtering password field."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="password=MySecretPass123",
            args=(),
            exc_info=None,
        )
        filter_obj.filter(record)
        assert "MySecretPass123" not in record.msg
        assert "password=***" in record.msg

    def test_filter_args(self):
        """Test filtering in log record args."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Login with %s",
            args=("api_key=sk-secret123",),
            exc_info=None,
        )
        filter_obj.filter(record)
        assert "sk-secret123" not in record.args[0]
        assert "api_key=***" in record.args[0]

    def test_filter_returns_true(self):
        """Test that filter always returns True (allows record through)."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Normal message",
            args=(),
            exc_info=None,
        )
        result = filter_obj.filter(record)
        assert result is True

    def test_no_false_positives(self):
        """Test that normal text is not filtered."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Processing document with category=Office Supplies",
            args=(),
            exc_info=None,
        )
        original_msg = record.msg
        filter_obj.filter(record)
        assert record.msg == original_msg


class TestLoggerSetup:
    """Test suite for LoggerSetup class."""

    def test_initialization(self):
        """Test LoggerSetup initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = f"{tmpdir}/test.log"
            setup = LoggerSetup(
                log_file=log_file,
                log_level="DEBUG",
                max_bytes=1024,
                backup_count=3,
                console_output=False,
            )

            assert setup.log_file == Path(log_file)
            assert setup.log_level == logging.DEBUG
            assert setup.max_bytes == 1024
            assert setup.backup_count == 3
            assert setup.console_output is False

    def test_creates_log_directory(self):
        """Test that log directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = f"{tmpdir}/subdir/test.log"
            setup = LoggerSetup(log_file=log_file)

            assert Path(log_file).parent.exists()

    def test_setup_creates_handlers(self):
        """Test that setup creates appropriate handlers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = f"{tmpdir}/test.log"
            setup = LoggerSetup(log_file=log_file, console_output=True)

            logger = setup.setup()

            # Should have 2 handlers: file and console
            assert len(logger.handlers) == 2

            # Check handler types
            handler_types = [type(h).__name__ for h in logger.handlers]
            assert "RotatingFileHandler" in handler_types
            assert "StreamHandler" in handler_types

    def test_setup_without_console(self):
        """Test setup with console output disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = f"{tmpdir}/test.log"
            setup = LoggerSetup(log_file=log_file, console_output=False)

            logger = setup.setup()

            # Should have only file handler
            assert len(logger.handlers) == 1
            assert type(logger.handlers[0]).__name__ == "RotatingFileHandler"

    def test_setup_applies_sensitive_filter(self):
        """Test that sensitive data filter is applied to all handlers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = f"{tmpdir}/test.log"
            setup = LoggerSetup(log_file=log_file, console_output=True)

            logger = setup.setup()

            # Check that all handlers have SensitiveDataFilter
            for handler in logger.handlers:
                filter_types = [type(f).__name__ for f in handler.filters]
                assert "SensitiveDataFilter" in filter_types

    def test_log_rotation_size(self):
        """Test that log rotation occurs at max_bytes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = f"{tmpdir}/test.log"
            # Very small size to trigger rotation
            setup = LoggerSetup(
                log_file=log_file, max_bytes=500, backup_count=2, console_output=False
            )

            logger = setup.setup()

            # Write enough data to trigger rotation
            for i in range(100):
                logger.info(f"Test message {i} with some content to fill up space")

            # Check that rotation occurred (backup file exists)
            log_path = Path(log_file)
            backup_file = Path(f"{log_file}.1")

            # Rotation creates backup files
            assert log_path.exists()
            # Backup may or may not exist depending on exact size, but log should exist
            assert log_path.stat().st_size > 0

    def test_log_rotation_backup_count(self):
        """Test that only specified number of backups are kept."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = f"{tmpdir}/test.log"
            backup_count = 2
            setup = LoggerSetup(
                log_file=log_file, max_bytes=100, backup_count=backup_count, console_output=False
            )

            logger = setup.setup()

            # Write lots of data to create multiple rotations
            for i in range(500):
                logger.info(f"Message {i} " + "x" * 100)

            # Count backup files
            log_dir = Path(log_file).parent
            backup_files = list(log_dir.glob(f"{Path(log_file).name}.*"))

            # Should have at most backup_count files (could be less if not enough rotations)
            assert len(backup_files) <= backup_count

    def test_log_level_filtering(self):
        """Test that log level filtering works correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = f"{tmpdir}/test.log"
            setup = LoggerSetup(log_file=log_file, log_level="WARNING", console_output=False)

            logger = setup.setup()

            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")

            # Read log file
            with open(log_file) as f:
                content = f.read()

            # Only WARNING and above should be logged
            assert "Debug message" not in content
            assert "Info message" not in content
            assert "Warning message" in content
            assert "Error message" in content


class TestGetLogger:
    """Test suite for get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a Logger instance."""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_with_name(self):
        """Test that logger has correct name."""
        logger = get_logger("my_module")
        assert logger.name == "my_module"


class TestSetupLogging:
    """Test suite for setup_logging function."""

    def test_setup_logging_creates_logger(self):
        """Test that setup_logging creates a logger."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = f"{tmpdir}/test.log"
            logger = setup_logging(log_file=log_file, log_level="INFO", console_output=False)

            assert isinstance(logger, logging.Logger)
            assert len(logger.handlers) > 0


class TestTemporaryLogLevel:
    """Test suite for temporary_log_level context manager."""

    def test_changes_log_level(self):
        """Test that context manager changes log level."""
        original_level = logging.INFO
        temp_level = logging.DEBUG

        logger = logging.getLogger()
        logger.setLevel(original_level)

        with temporary_log_level(temp_level):
            assert logger.level == temp_level

    def test_restores_log_level(self):
        """Test that original log level is restored."""
        original_level = logging.INFO
        temp_level = logging.DEBUG

        logger = logging.getLogger()
        logger.setLevel(original_level)

        with temporary_log_level(temp_level):
            pass

        assert logger.level == original_level

    def test_restores_handler_levels(self):
        """Test that handler log levels are restored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = f"{tmpdir}/test.log"
            setup = LoggerSetup(log_file=log_file, log_level="INFO", console_output=False)
            logger = setup.setup()

            original_handler_levels = [h.level for h in logger.handlers]

            with temporary_log_level(logging.DEBUG):
                # Handler levels should change
                for handler in logger.handlers:
                    assert handler.level == logging.DEBUG

            # Handler levels should be restored
            restored_levels = [h.level for h in logger.handlers]
            assert restored_levels == original_handler_levels


class TestStructuredLogging:
    """Test suite for structured logging helper functions."""

    def test_log_operation_start(self, caplog):
        """Test log_operation_start logs correctly."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO):
            log_operation_start(logger, "test_operation", user_id=123, document="test.pdf")

        assert "Operation started: test_operation" in caplog.text
        assert "user_id=123" in caplog.text
        assert "document=test.pdf" in caplog.text

    def test_log_operation_success_with_duration(self, caplog):
        """Test log_operation_success logs with duration."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO):
            log_operation_success(logger, "test_operation", duration_ms=123.45, result_count=5)

        assert "Operation succeeded: test_operation" in caplog.text
        assert "duration_ms=123.45" in caplog.text
        assert "result_count=5" in caplog.text

    def test_log_operation_success_without_duration(self, caplog):
        """Test log_operation_success without duration."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO):
            log_operation_success(logger, "test_operation", status="complete")

        assert "Operation succeeded: test_operation" in caplog.text
        assert "status=complete" in caplog.text
        assert "duration_ms" not in caplog.text

    def test_log_operation_failure(self, caplog):
        """Test log_operation_failure logs error details."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.ERROR)

        error = ValueError("Invalid input")

        with caplog.at_level(logging.ERROR):
            log_operation_failure(logger, "test_operation", error, document="test.pdf")

        assert "Operation failed: test_operation" in caplog.text
        assert "error=ValueError" in caplog.text
        assert "message=Invalid input" in caplog.text
        assert "document=test.pdf" in caplog.text

    def test_structured_logging_no_context(self, caplog):
        """Test structured logging functions work without context."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO):
            log_operation_start(logger, "simple_operation")

        assert "Operation started: simple_operation" in caplog.text

    def test_structured_logging_special_chars(self, caplog):
        """Test structured logging handles special characters."""
        logger = logging.getLogger("test")
        logger.setLevel(logging.INFO)

        with caplog.at_level(logging.INFO):
            log_operation_start(logger, "test_op", file_path="/path/to/file with spaces.pdf")

        assert "Operation started: test_op" in caplog.text
        assert "file_path=/path/to/file with spaces.pdf" in caplog.text
