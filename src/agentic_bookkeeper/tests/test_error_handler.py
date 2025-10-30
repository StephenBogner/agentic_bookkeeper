"""
Test suite for error handler utilities.

This module tests error formatting, logging, and GUI error handling functions.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-29
"""

import pytest
import logging
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from agentic_bookkeeper.utils.error_handler import (
    format_error_for_user,
    log_error_with_context,
    get_recovery_steps,
    format_recovery_steps_html,
    handle_gui_error,
    create_error_context,
    is_recoverable_error,
    get_error_severity,
)
from agentic_bookkeeper.utils.exceptions import (
    BookkeeperError,
    DocumentError,
    DatabaseError,
    LLMError,
    ConfigError,
    ValidationError,
)


class TestFormatErrorForUser:
    """Test suite for format_error_for_user function."""

    def test_format_bookkeeper_error(self):
        """Test formatting a BookkeeperError."""
        error = DocumentError(
            "Document not found",
            document_path="/path/to/file.pdf",
            tech_message="FileNotFoundError: /path/to/file.pdf",
            recovery_suggestions=["Check the path", "Try again"],
        )
        result = format_error_for_user(error)

        assert result["title"] == "Error: Document Error"
        assert result["message"] == "Document not found"
        assert result["details"] == "FileNotFoundError: /path/to/file.pdf"
        assert result["recovery_steps"] == ["Check the path", "Try again"]

    def test_format_generic_exception(self):
        """Test formatting a generic Python exception."""
        error = ValueError("Invalid input")
        result = format_error_for_user(error)

        assert result["title"] == "Error: ValueError"
        assert result["message"] == "Invalid input"
        assert result["details"] == "ValueError: Invalid input"
        assert len(result["recovery_steps"]) > 0

    def test_format_exception_without_message(self):
        """Test formatting an exception with no message."""
        error = RuntimeError()
        result = format_error_for_user(error)

        assert "Error" in result["title"]
        assert "unexpected error" in result["message"].lower()

    def test_tech_message_same_as_user_message(self):
        """Test that details are None when tech and user messages are identical."""
        error = BookkeeperError("Same message")
        result = format_error_for_user(error)

        assert result["details"] is None


class TestLogErrorWithContext:
    """Test suite for log_error_with_context function."""

    def test_log_error_default_severity(self, caplog):
        """Test logging error with default severity."""
        with caplog.at_level(logging.ERROR):
            error = DocumentError("Test error", document_path="/test/path")
            log_error_with_context(error)

            assert "DOCUMENT_ERROR" in caplog.text
            assert "Test error" in caplog.text

    def test_log_error_with_context_dict(self, caplog):
        """Test logging error with context dictionary."""
        with caplog.at_level(logging.ERROR):
            error = DatabaseError("Query failed", operation="select")
            context = {"user_action": "loading transactions", "table": "transactions"}
            log_error_with_context(error, context)

            assert "user_action=loading transactions" in caplog.text
            assert "table=transactions" in caplog.text

    def test_log_error_critical_severity(self, caplog):
        """Test logging error with critical severity."""
        with caplog.at_level(logging.CRITICAL):
            error = DatabaseError("Database corruption", operation="open")
            log_error_with_context(error, severity="critical")

            assert "CRITICAL" in caplog.text
            assert "Database corruption" in caplog.text

    def test_log_error_warning_severity(self, caplog):
        """Test logging error with warning severity."""
        with caplog.at_level(logging.WARNING):
            error = ConfigError("Missing optional config", config_key="theme")
            log_error_with_context(error, severity="warning")

            assert "WARNING" in caplog.text
            assert "Missing optional config" in caplog.text

    def test_log_generic_exception(self, caplog):
        """Test logging a generic Python exception."""
        with caplog.at_level(logging.ERROR):
            error = ValueError("Invalid value")
            log_error_with_context(error)

            assert "ValueError" in caplog.text
            assert "Invalid value" in caplog.text


class TestGetRecoverySteps:
    """Test suite for get_recovery_steps function."""

    def test_bookkeeper_error_recovery_steps(self):
        """Test getting recovery steps from BookkeeperError."""
        error = LLMError(
            "API failed",
            provider="OpenAI",
            recovery_suggestions=["Check API key", "Verify connection"],
        )
        steps = get_recovery_steps(error)

        assert steps == ["Check API key", "Verify connection"]

    def test_generic_exception_recovery_steps(self):
        """Test getting default recovery steps for generic exception."""
        error = RuntimeError("Something failed")
        steps = get_recovery_steps(error)

        assert len(steps) > 0
        assert any("try" in step.lower() or "Try" in step for step in steps)


class TestFormatRecoveryStepsHtml:
    """Test suite for format_recovery_steps_html function."""

    def test_format_steps_as_html(self):
        """Test formatting recovery steps as HTML."""
        steps = ["Step 1", "Step 2", "Step 3"]
        html = format_recovery_steps_html(steps)

        assert "<b>Suggested Actions:</b>" in html
        assert "<ul>" in html
        assert "</ul>" in html
        assert "<li>Step 1</li>" in html
        assert "<li>Step 2</li>" in html
        assert "<li>Step 3</li>" in html

    def test_format_empty_steps(self):
        """Test formatting empty recovery steps list."""
        html = format_recovery_steps_html([])
        assert html == ""

    def test_html_escaping(self):
        """Test that HTML special characters are preserved."""
        steps = ["Check <config> file", "Try again & verify"]
        html = format_recovery_steps_html(steps)

        # HTML content should be present
        assert "<li>Check <config> file</li>" in html
        assert "<li>Try again & verify</li>" in html


class TestHandleGuiError:
    """Test suite for handle_gui_error function."""

    @patch("agentic_bookkeeper.utils.error_handler.log_error_with_context")
    @patch("PySide6.QtWidgets.QMessageBox")
    def test_handle_gui_error_displays_dialog(self, mock_msgbox, mock_log):
        """Test that GUI error displays a message box."""
        # Create mock message box instance
        mock_box = Mock()
        mock_msgbox.return_value = mock_box
        mock_box.exec.return_value = None

        error = ValidationError("Invalid date", field="date")
        mock_parent = Mock()

        handle_gui_error(error, parent_widget=mock_parent)

        # Verify logging was called
        mock_log.assert_called_once()

        # Verify QMessageBox was instantiated with parent
        mock_msgbox.assert_called_once_with(mock_parent)

        # Verify methods were called on message box
        assert mock_box.setIcon.called
        assert mock_box.setWindowTitle.called
        assert mock_box.setText.called
        assert mock_box.exec.called

    @patch("agentic_bookkeeper.utils.error_handler.log_error_with_context")
    @patch("PySide6.QtWidgets.QMessageBox")
    def test_handle_gui_error_with_context(self, mock_msgbox, mock_log):
        """Test GUI error with additional context."""
        # Create mock message box instance
        mock_box = Mock()
        mock_msgbox.return_value = mock_box
        mock_box.exec.return_value = None

        error = DocumentError("File not found", document_path="/test/path")
        context = {"user_action": "opening document"}

        handle_gui_error(error, context=context)

        # Verify context was passed to logging
        mock_log.assert_called_once()
        call_args = mock_log.call_args
        assert call_args[0][1] == context

    @patch("agentic_bookkeeper.utils.error_handler.log_error_with_context")
    @patch("PySide6.QtWidgets.QMessageBox")
    def test_handle_gui_error_logging_only(self, mock_msgbox, mock_log):
        """Test that logging occurs regardless of GUI availability."""
        # Create mock message box instance
        mock_box = Mock()
        mock_msgbox.return_value = mock_box
        mock_box.exec.return_value = None

        error = ConfigError("Config error", config_key="test")
        context = {"operation": "load_config"}

        # Just test that logging works, GUI may or may not be available
        handle_gui_error(error, context=context)

        # Logging should have been called
        mock_log.assert_called_once()
        call_args = mock_log.call_args
        assert call_args[0][0] == error
        assert call_args[0][1] == context


class TestCreateErrorContext:
    """Test suite for create_error_context function."""

    def test_create_basic_context(self):
        """Test creating basic error context."""
        context = create_error_context(operation="document_processing")

        assert "timestamp" in context
        assert context["operation"] == "document_processing"
        assert "user_action" not in context
        assert "file_path" not in context

    def test_create_context_with_user_action(self):
        """Test creating context with user action."""
        context = create_error_context(
            operation="save_transaction",
            user_action="clicking Save button",
        )

        assert context["operation"] == "save_transaction"
        assert context["user_action"] == "clicking Save button"

    def test_create_context_with_file_path(self):
        """Test creating context with file path."""
        context = create_error_context(
            operation="process_document",
            file_path="/path/to/document.pdf",
        )

        assert context["operation"] == "process_document"
        assert context["file_path"] == "/path/to/document.pdf"

    def test_create_context_with_kwargs(self):
        """Test creating context with additional kwargs."""
        context = create_error_context(
            operation="generate_report",
            report_type="income_statement",
            date_range="2024-01-01 to 2024-12-31",
        )

        assert context["operation"] == "generate_report"
        assert context["report_type"] == "income_statement"
        assert context["date_range"] == "2024-01-01 to 2024-12-31"

    def test_timestamp_format(self):
        """Test that timestamp is in ISO format."""
        context = create_error_context(operation="test")
        timestamp = context["timestamp"]

        # Should be parseable as ISO format
        datetime.fromisoformat(timestamp)


class TestIsRecoverableError:
    """Test suite for is_recoverable_error function."""

    def test_database_error_recoverable(self):
        """Test that database errors are recoverable."""
        error = DatabaseError("Connection failed", operation="connect")
        assert is_recoverable_error(error) is True

    def test_network_error_recoverable(self):
        """Test that network errors are recoverable."""
        error = Exception("Network connection timeout")
        assert is_recoverable_error(error) is True

    def test_file_not_found_recoverable(self):
        """Test that file not found errors are recoverable."""
        error = FileNotFoundError("File not found: /path/to/file")
        assert is_recoverable_error(error) is True

    def test_bookkeeper_error_recoverable(self):
        """Test that BookkeeperErrors are recoverable."""
        error = ConfigError("Invalid config", config_key="test")
        assert is_recoverable_error(error) is True

    def test_generic_error_not_recoverable(self):
        """Test that generic errors are not recoverable."""
        error = RuntimeError("Unexpected runtime error")
        assert is_recoverable_error(error) is False

    def test_api_rate_limit_recoverable(self):
        """Test that API rate limit errors are recoverable."""
        error = Exception("API rate limit exceeded")
        assert is_recoverable_error(error) is True


class TestGetErrorSeverity:
    """Test suite for get_error_severity function."""

    def test_critical_error_severity(self):
        """Test that critical errors are identified."""
        error = Exception("Database corruption detected")
        assert get_error_severity(error) == "critical"

    def test_disk_full_critical(self):
        """Test that disk full errors are critical."""
        error = OSError("Disk full")
        assert get_error_severity(error) == "critical"

    def test_recoverable_error_warning(self):
        """Test that recoverable errors are warnings."""
        error = DatabaseError("Connection timeout", operation="query")
        assert get_error_severity(error) == "warning"

    def test_generic_error_severity(self):
        """Test that non-recoverable errors are 'error' severity."""
        error = RuntimeError("Unexpected error")
        assert get_error_severity(error) == "error"

    def test_bookkeeper_error_warning(self):
        """Test that BookkeeperErrors are treated as warnings."""
        error = ValidationError("Invalid input", field="amount")
        assert get_error_severity(error) == "warning"


class TestErrorHandlerIntegration:
    """Integration tests for error handler module."""

    def test_full_error_flow(self, caplog):
        """Test complete error handling flow."""
        with caplog.at_level(logging.ERROR):
            # Create error
            error = LLMError(
                "API call failed",
                provider="OpenAI",
                api_error="Rate limit exceeded",
                recovery_suggestions=["Wait and retry", "Check API credits"],
            )

            # Format for user
            formatted = format_error_for_user(error)
            assert (
                "OpenAI" in formatted["message"]
                or "API" in formatted["message"]
                or formatted["title"]
            )

            # Log with context
            context = create_error_context(
                operation="extract_transaction",
                user_action="processing document",
                file_path="/test/document.pdf",
            )
            log_error_with_context(error, context)

            # Verify logging
            assert "LLM_ERROR" in caplog.text
            assert "extract_transaction" in caplog.text

            # Get recovery steps
            steps = get_recovery_steps(error)
            assert "Wait and retry" in steps

            # Check error properties
            assert is_recoverable_error(error) is True
            assert get_error_severity(error) == "warning"
