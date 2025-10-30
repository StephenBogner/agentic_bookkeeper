"""
Centralized error handling and formatting utilities.

This module provides functions for formatting errors for users, logging errors
with context, and displaying error dialogs in the GUI.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-29
"""

import logging
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime

from .exceptions import BookkeeperError


logger = logging.getLogger(__name__)


def format_error_for_user(error: Exception) -> Dict[str, Any]:
    """
    Format an exception for user display.

    Args:
        error: Exception to format

    Returns:
        Dictionary with formatted error information:
        - title: Error dialog title
        - message: User-friendly error message
        - details: Technical details (optional)
        - recovery_steps: List of suggested actions
    """
    if isinstance(error, BookkeeperError):
        return {
            "title": f"Error: {error.error_code.replace('_', ' ').title()}",
            "message": error.user_message,
            "details": error.tech_message if error.tech_message != error.user_message else None,
            "recovery_steps": error.recovery_suggestions,
        }
    else:
        # Generic error formatting
        error_type = type(error).__name__
        return {
            "title": f"Error: {error_type}",
            "message": str(error) or "An unexpected error occurred",
            "details": f"{error_type}: {str(error)}",
            "recovery_steps": [
                "Try the operation again",
                "Restart the application if the problem persists",
                "Check the log file for more details",
                "Contact support if you need assistance",
            ],
        }


def log_error_with_context(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    severity: str = "error",
) -> None:
    """
    Log an error with contextual information.

    Args:
        error: Exception to log
        context: Additional context information (user action, system state, etc.)
        severity: Log severity level ('error', 'warning', 'critical')
    """
    # Build context string
    context = context or {}
    context_str = ", ".join(f"{k}={v}" for k, v in context.items())

    # Get error details
    if isinstance(error, BookkeeperError):
        error_msg = f"[{error.error_code}] {error.tech_message}"
    else:
        error_msg = f"[{type(error).__name__}] {str(error)}"

    # Get stack trace
    stack_trace = traceback.format_exc()

    # Log with appropriate severity
    log_message = f"{error_msg}"
    if context_str:
        log_message += f" | Context: {context_str}"

    if severity == "critical":
        logger.critical(log_message)
        logger.critical(f"Stack trace:\n{stack_trace}")
    elif severity == "warning":
        logger.warning(log_message)
    else:
        logger.error(log_message)
        logger.debug(f"Stack trace:\n{stack_trace}")


def get_recovery_steps(error: Exception) -> List[str]:
    """
    Get recovery steps for an exception.

    Args:
        error: Exception to get recovery steps for

    Returns:
        List of suggested recovery steps
    """
    if isinstance(error, BookkeeperError):
        return error.recovery_suggestions
    else:
        return [
            "Try the operation again",
            "Restart the application if the problem persists",
            "Check the log file for more details",
            "Contact support if you need assistance",
        ]


def format_recovery_steps_html(steps: List[str]) -> str:
    """
    Format recovery steps as HTML for display.

    Args:
        steps: List of recovery steps

    Returns:
        HTML formatted string
    """
    if not steps:
        return ""

    html = "<b>Suggested Actions:</b><ul>"
    for step in steps:
        html += f"<li>{step}</li>"
    html += "</ul>"
    return html


def handle_gui_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    parent_widget: Optional[Any] = None,
) -> None:
    """
    Handle an error in the GUI by logging and displaying a dialog.

    Args:
        error: Exception to handle
        context: Additional context information
        parent_widget: Parent QWidget for the error dialog (optional)
    """
    # Log the error with context
    log_error_with_context(error, context)

    # Format for user display
    error_info = format_error_for_user(error)

    # Import here to avoid circular dependency
    try:
        from PySide6.QtWidgets import QMessageBox

        # Build detailed message with recovery steps
        message = error_info["message"]
        if error_info["recovery_steps"]:
            message += "\n\n" + format_recovery_steps_html(error_info["recovery_steps"])

        # Show error dialog
        msg_box = QMessageBox(parent_widget)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(error_info["title"])
        msg_box.setText(error_info["message"])

        # Add recovery steps as informative text
        if error_info["recovery_steps"]:
            recovery_text = "\n".join(f"• {step}" for step in error_info["recovery_steps"])
            msg_box.setInformativeText(f"\nSuggested Actions:\n{recovery_text}")

        # Add technical details if available
        if error_info["details"]:
            msg_box.setDetailedText(error_info["details"])

        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    except ImportError:
        # If PySide6 is not available, just log
        logger.error(f"Cannot display GUI error dialog: {error_info['message']}")


def create_error_context(
    operation: str,
    user_action: Optional[str] = None,
    file_path: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a standardized error context dictionary.

    Args:
        operation: Name of the operation being performed
        user_action: User action that triggered the error
        file_path: File path involved (if applicable)
        **kwargs: Additional context key-value pairs

    Returns:
        Dictionary with error context
    """
    context = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
    }

    if user_action:
        context["user_action"] = user_action
    if file_path:
        context["file_path"] = file_path

    # Add any additional context
    context.update(kwargs)

    return context


def is_recoverable_error(error: Exception) -> bool:
    """
    Determine if an error is recoverable.

    Args:
        error: Exception to check

    Returns:
        True if the error is recoverable, False otherwise
    """
    # Database errors are usually recoverable (retry, reconnect)
    if "database" in str(error).lower() or "sqlite" in str(error).lower():
        return True

    # Network/API errors are recoverable (retry, check connection)
    if any(
        keyword in str(error).lower()
        for keyword in ["network", "connection", "timeout", "api", "rate limit"]
    ):
        return True

    # File not found can be recoverable (user can provide correct path)
    if "not found" in str(error).lower() or "no such file" in str(error).lower():
        return True

    # BookkeeperErrors are generally recoverable
    if isinstance(error, BookkeeperError):
        return True

    # Most other errors are not recoverable
    return False


def get_error_severity(error: Exception) -> str:
    """
    Determine the severity level of an error.

    Args:
        error: Exception to assess

    Returns:
        Severity level: 'critical', 'error', or 'warning'
    """
    # Critical errors that prevent app from functioning
    critical_keywords = ["database corruption", "disk full", "out of memory"]
    if any(keyword in str(error).lower() for keyword in critical_keywords):
        return "critical"

    # Recoverable errors are warnings
    if is_recoverable_error(error):
        return "warning"

    # Everything else is an error
    return "error"
