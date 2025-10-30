"""
Custom exception classes for Agentic Bookkeeper.

This module defines a hierarchy of exceptions with user-friendly error messages
and recovery suggestions for better error handling throughout the application.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-29
"""

from typing import List, Optional, Any


class BookkeeperError(Exception):
    """
    Base exception class for all Agentic Bookkeeper errors.

    Attributes:
        error_code: Short code identifying the error type
        user_message: User-friendly error message
        tech_message: Technical error details for logging
        recovery_suggestions: List of steps to resolve the error
    """

    def __init__(
        self,
        user_message: str,
        tech_message: Optional[str] = None,
        error_code: str = "GENERAL_ERROR",
        recovery_suggestions: Optional[List[str]] = None,
    ):
        """
        Initialize BookkeeperError.

        Args:
            user_message: User-friendly error description
            tech_message: Technical details for logging
            error_code: Short error identifier
            recovery_suggestions: Steps to fix the error
        """
        super().__init__(user_message)
        self.error_code = error_code
        self.user_message = user_message
        self.tech_message = tech_message or user_message
        self.recovery_suggestions = recovery_suggestions or []

    def __str__(self) -> str:
        """Return string representation of error."""
        return f"[{self.error_code}] {self.user_message}"


class DocumentError(BookkeeperError):
    """
    Exception raised for document processing errors.

    Attributes:
        document_path: Path to the problematic document
        document_format: File format (e.g., 'pdf', 'jpg')
    """

    def __init__(
        self,
        user_message: str,
        document_path: str,
        document_format: Optional[str] = None,
        tech_message: Optional[str] = None,
        recovery_suggestions: Optional[List[str]] = None,
    ):
        """
        Initialize DocumentError.

        Args:
            user_message: User-friendly error description
            document_path: Path to the document
            document_format: File format (e.g., 'pdf', 'jpg')
            tech_message: Technical details for logging
            recovery_suggestions: Steps to fix the error
        """
        super().__init__(
            user_message=user_message,
            tech_message=tech_message,
            error_code="DOCUMENT_ERROR",
            recovery_suggestions=recovery_suggestions
            or [
                "Check that the file exists and is not corrupted",
                "Ensure the file format is supported (PDF, PNG, JPG, JPEG)",
                "Try re-scanning or re-saving the document",
                "Contact support if the problem persists",
            ],
        )
        self.document_path = document_path
        self.document_format = document_format


class DatabaseError(BookkeeperError):
    """
    Exception raised for database operation errors.

    Attributes:
        operation: Database operation that failed (e.g., 'insert', 'update')
        table: Database table involved
    """

    def __init__(
        self,
        user_message: str,
        operation: str,
        table: Optional[str] = None,
        tech_message: Optional[str] = None,
        recovery_suggestions: Optional[List[str]] = None,
    ):
        """
        Initialize DatabaseError.

        Args:
            user_message: User-friendly error description
            operation: Database operation that failed
            table: Database table involved
            tech_message: Technical details for logging
            recovery_suggestions: Steps to fix the error
        """
        super().__init__(
            user_message=user_message,
            tech_message=tech_message,
            error_code="DATABASE_ERROR",
            recovery_suggestions=recovery_suggestions
            or [
                "Check if the database file is accessible",
                "Ensure the application has write permissions",
                "Try restarting the application",
                "Restore from backup if data is corrupted",
            ],
        )
        self.operation = operation
        self.table = table


class LLMError(BookkeeperError):
    """
    Exception raised for LLM provider errors.

    Attributes:
        provider: Name of the LLM provider (e.g., 'OpenAI', 'Anthropic')
        api_error: Original API error message
    """

    def __init__(
        self,
        user_message: str,
        provider: str,
        api_error: Optional[str] = None,
        tech_message: Optional[str] = None,
        recovery_suggestions: Optional[List[str]] = None,
    ):
        """
        Initialize LLMError.

        Args:
            user_message: User-friendly error description
            provider: LLM provider name
            api_error: Original API error message
            tech_message: Technical details for logging
            recovery_suggestions: Steps to fix the error
        """
        super().__init__(
            user_message=user_message,
            tech_message=tech_message or api_error,
            error_code="LLM_ERROR",
            recovery_suggestions=recovery_suggestions
            or [
                f"Check your {provider} API key in Settings",
                "Verify your internet connection is working",
                "Check if you have sufficient API credits",
                f"Try switching to a different LLM provider in Settings",
            ],
        )
        self.provider = provider
        self.api_error = api_error


class ConfigError(BookkeeperError):
    """
    Exception raised for configuration errors.

    Attributes:
        config_key: Configuration key that caused the error
        config_value: The problematic configuration value
    """

    def __init__(
        self,
        user_message: str,
        config_key: str,
        config_value: Any = None,
        tech_message: Optional[str] = None,
        recovery_suggestions: Optional[List[str]] = None,
    ):
        """
        Initialize ConfigError.

        Args:
            user_message: User-friendly error description
            config_key: Configuration key
            config_value: The problematic value
            tech_message: Technical details for logging
            recovery_suggestions: Steps to fix the error
        """
        super().__init__(
            user_message=user_message,
            tech_message=tech_message,
            error_code="CONFIG_ERROR",
            recovery_suggestions=recovery_suggestions
            or [
                "Open Settings and review your configuration",
                f"Check the value for '{config_key}'",
                "Refer to the User Guide for valid configuration options",
                "Reset to default settings if needed",
            ],
        )
        self.config_key = config_key
        self.config_value = config_value


class ValidationError(BookkeeperError):
    """
    Exception raised for data validation errors.

    Attributes:
        field: Name of the field that failed validation
        value: The invalid value
        constraint: Validation constraint that was violated
    """

    def __init__(
        self,
        user_message: str,
        field: str,
        value: Any = None,
        constraint: Optional[str] = None,
        tech_message: Optional[str] = None,
        recovery_suggestions: Optional[List[str]] = None,
    ):
        """
        Initialize ValidationError.

        Args:
            user_message: User-friendly error description
            field: Field name that failed validation
            value: The invalid value
            constraint: Validation constraint violated
            tech_message: Technical details for logging
            recovery_suggestions: Steps to fix the error
        """
        super().__init__(
            user_message=user_message,
            tech_message=tech_message,
            error_code="VALIDATION_ERROR",
            recovery_suggestions=recovery_suggestions
            or [
                f"Check the value entered for '{field}'",
                (
                    f"Ensure it meets the requirement: {constraint}"
                    if constraint
                    else "Ensure it meets the requirements"
                ),
                "Refer to field help text for valid values",
                "Contact support if you believe this is an error",
            ],
        )
        self.field = field
        self.value = value
        self.constraint = constraint
