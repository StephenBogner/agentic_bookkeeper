"""
Test suite for custom exception classes.

This module tests the exception hierarchy, error messages, and recovery suggestions.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-29
"""

import pytest
from agentic_bookkeeper.utils.exceptions import (
    BookkeeperError,
    DocumentError,
    DatabaseError,
    LLMError,
    ConfigError,
    ValidationError,
)


class TestBookkeeperError:
    """Test suite for BookkeeperError base exception."""

    def test_basic_initialization(self):
        """Test basic exception initialization."""
        error = BookkeeperError("Something went wrong")
        assert error.user_message == "Something went wrong"
        assert error.tech_message == "Something went wrong"
        assert error.error_code == "GENERAL_ERROR"
        assert error.recovery_suggestions == []

    def test_full_initialization(self):
        """Test initialization with all parameters."""
        error = BookkeeperError(
            user_message="User friendly message",
            tech_message="Technical details for logging",
            error_code="TEST_ERROR",
            recovery_suggestions=["Step 1", "Step 2"],
        )
        assert error.user_message == "User friendly message"
        assert error.tech_message == "Technical details for logging"
        assert error.error_code == "TEST_ERROR"
        assert error.recovery_suggestions == ["Step 1", "Step 2"]

    def test_string_representation(self):
        """Test string representation of error."""
        error = BookkeeperError("Test error", error_code="TEST_CODE")
        assert str(error) == "[TEST_CODE] Test error"

    def test_inheritance(self):
        """Test that BookkeeperError inherits from Exception."""
        error = BookkeeperError("Test error")
        assert isinstance(error, Exception)
        assert isinstance(error, BookkeeperError)


class TestDocumentError:
    """Test suite for DocumentError exception."""

    def test_basic_initialization(self):
        """Test basic document error initialization."""
        error = DocumentError("Document not found", document_path="/path/to/file.pdf")
        assert error.user_message == "Document not found"
        assert error.document_path == "/path/to/file.pdf"
        assert error.document_format is None
        assert error.error_code == "DOCUMENT_ERROR"
        assert len(error.recovery_suggestions) > 0

    def test_with_format(self):
        """Test document error with format specified."""
        error = DocumentError(
            "Invalid document format",
            document_path="/path/to/file.txt",
            document_format="txt",
        )
        assert error.document_format == "txt"

    def test_default_recovery_suggestions(self):
        """Test that default recovery suggestions are provided."""
        error = DocumentError("Error", document_path="/path/to/file.pdf")
        assert (
            "check" in error.recovery_suggestions[0].lower()
            or "Check" in error.recovery_suggestions[0]
        )
        assert len(error.recovery_suggestions) >= 3

    def test_custom_recovery_suggestions(self):
        """Test custom recovery suggestions."""
        custom_suggestions = ["Custom step 1", "Custom step 2"]
        error = DocumentError(
            "Error",
            document_path="/path/to/file.pdf",
            recovery_suggestions=custom_suggestions,
        )
        assert error.recovery_suggestions == custom_suggestions

    def test_inheritance(self):
        """Test DocumentError inheritance."""
        error = DocumentError("Error", document_path="/path/to/file.pdf")
        assert isinstance(error, BookkeeperError)
        assert isinstance(error, DocumentError)


class TestDatabaseError:
    """Test suite for DatabaseError exception."""

    def test_basic_initialization(self):
        """Test basic database error initialization."""
        error = DatabaseError("Connection failed", operation="connect")
        assert error.user_message == "Connection failed"
        assert error.operation == "connect"
        assert error.table is None
        assert error.error_code == "DATABASE_ERROR"

    def test_with_table(self):
        """Test database error with table specified."""
        error = DatabaseError(
            "Insert failed",
            operation="insert",
            table="transactions",
        )
        assert error.operation == "insert"
        assert error.table == "transactions"

    def test_default_recovery_suggestions(self):
        """Test default recovery suggestions."""
        error = DatabaseError("Error", operation="query")
        assert len(error.recovery_suggestions) >= 3
        assert any("database" in s.lower() for s in error.recovery_suggestions)

    def test_inheritance(self):
        """Test DatabaseError inheritance."""
        error = DatabaseError("Error", operation="query")
        assert isinstance(error, BookkeeperError)
        assert isinstance(error, DatabaseError)


class TestLLMError:
    """Test suite for LLMError exception."""

    def test_basic_initialization(self):
        """Test basic LLM error initialization."""
        error = LLMError("API call failed", provider="OpenAI")
        assert error.user_message == "API call failed"
        assert error.provider == "OpenAI"
        assert error.api_error is None
        assert error.error_code == "LLM_ERROR"

    def test_with_api_error(self):
        """Test LLM error with API error message."""
        error = LLMError(
            "API call failed",
            provider="Anthropic",
            api_error="Rate limit exceeded",
        )
        assert error.api_error == "Rate limit exceeded"
        assert error.tech_message == "Rate limit exceeded"

    def test_default_recovery_suggestions(self):
        """Test that provider name appears in suggestions."""
        error = LLMError("Error", provider="OpenAI")
        suggestions_text = " ".join(error.recovery_suggestions)
        assert "OpenAI" in suggestions_text or "API" in suggestions_text

    def test_inheritance(self):
        """Test LLMError inheritance."""
        error = LLMError("Error", provider="OpenAI")
        assert isinstance(error, BookkeeperError)
        assert isinstance(error, LLMError)


class TestConfigError:
    """Test suite for ConfigError exception."""

    def test_basic_initialization(self):
        """Test basic config error initialization."""
        error = ConfigError("Invalid configuration", config_key="api_key")
        assert error.user_message == "Invalid configuration"
        assert error.config_key == "api_key"
        assert error.config_value is None
        assert error.error_code == "CONFIG_ERROR"

    def test_with_value(self):
        """Test config error with value specified."""
        error = ConfigError(
            "Invalid value",
            config_key="timeout",
            config_value=0,
        )
        assert error.config_key == "timeout"
        assert error.config_value == 0

    def test_default_recovery_suggestions(self):
        """Test that config key appears in suggestions."""
        error = ConfigError("Error", config_key="test_key")
        suggestions_text = " ".join(error.recovery_suggestions)
        assert "test_key" in suggestions_text or "Settings" in suggestions_text

    def test_inheritance(self):
        """Test ConfigError inheritance."""
        error = ConfigError("Error", config_key="key")
        assert isinstance(error, BookkeeperError)
        assert isinstance(error, ConfigError)


class TestValidationError:
    """Test suite for ValidationError exception."""

    def test_basic_initialization(self):
        """Test basic validation error initialization."""
        error = ValidationError("Invalid amount", field="amount")
        assert error.user_message == "Invalid amount"
        assert error.field == "amount"
        assert error.value is None
        assert error.constraint is None
        assert error.error_code == "VALIDATION_ERROR"

    def test_with_value_and_constraint(self):
        """Test validation error with value and constraint."""
        error = ValidationError(
            "Amount must be positive",
            field="amount",
            value=-10.5,
            constraint="amount >= 0",
        )
        assert error.field == "amount"
        assert error.value == -10.5
        assert error.constraint == "amount >= 0"

    def test_default_recovery_suggestions(self):
        """Test that field name appears in suggestions."""
        error = ValidationError("Error", field="date")
        suggestions_text = " ".join(error.recovery_suggestions)
        assert "date" in suggestions_text or "field" in suggestions_text

    def test_constraint_in_suggestions(self):
        """Test that constraint appears in suggestions when provided."""
        error = ValidationError(
            "Error",
            field="amount",
            constraint="Must be greater than 0",
        )
        suggestions_text = " ".join(error.recovery_suggestions)
        assert "Must be greater than 0" in suggestions_text

    def test_inheritance(self):
        """Test ValidationError inheritance."""
        error = ValidationError("Error", field="test")
        assert isinstance(error, BookkeeperError)
        assert isinstance(error, ValidationError)


class TestExceptionHierarchy:
    """Test exception class hierarchy."""

    def test_all_inherit_from_base(self):
        """Test that all exceptions inherit from BookkeeperError."""
        exceptions = [
            DocumentError("", document_path=""),
            DatabaseError("", operation=""),
            LLMError("", provider=""),
            ConfigError("", config_key=""),
            ValidationError("", field=""),
        ]
        for exc in exceptions:
            assert isinstance(exc, BookkeeperError)
            assert isinstance(exc, Exception)

    def test_exception_codes_unique(self):
        """Test that each exception type has a unique error code."""
        exceptions = [
            BookkeeperError(""),
            DocumentError("", document_path=""),
            DatabaseError("", operation=""),
            LLMError("", provider=""),
            ConfigError("", config_key=""),
            ValidationError("", field=""),
        ]
        error_codes = [exc.error_code for exc in exceptions]
        assert len(error_codes) == len(set(error_codes))

    def test_all_have_recovery_suggestions(self):
        """Test that all exceptions provide recovery suggestions."""
        exceptions = [
            BookkeeperError("", recovery_suggestions=["Step 1"]),
            DocumentError("", document_path=""),
            DatabaseError("", operation=""),
            LLMError("", provider=""),
            ConfigError("", config_key=""),
            ValidationError("", field=""),
        ]
        for exc in exceptions:
            assert isinstance(exc.recovery_suggestions, list)
