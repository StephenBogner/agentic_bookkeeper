"""Main entry point for the agentic_bookkeeper GUI application.

Package Name: agentic_bookkeeper
File Name: main.py
Author: Stephen Bogner, P.Eng.
LLM: claude-sonnet-4-5-20250929
Ownership: Stephen Bogner - All Rights Reserved.  See LICENSE
Date Created: 2025-10-24
Date Modified: 2025-10-28
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication, QMessageBox

from agentic_bookkeeper.models.database import Database
from agentic_bookkeeper.gui.main_window import MainWindow
from agentic_bookkeeper.utils.config import Config


def configure_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
        force=True,  # Override any existing configuration
    )


def is_first_run(config: Config) -> bool:
    """
    Check if this is the first time the application is being run.

    Args:
        config: Configuration instance

    Returns:
        True if first run, False otherwise
    """
    db_path = config.get_database_path()
    return not db_path.exists()


def initialize_application(config: Config) -> bool:
    """
    Initialize the application on first run.

    Creates necessary directories and initializes the database.

    Args:
        config: Configuration instance

    Returns:
        True if initialization successful, False otherwise
    """
    logger = logging.getLogger(__name__)

    try:
        # Create data directories
        logger.info("Creating data directories...")
        watch_dir = config.get_watch_directory()
        processed_dir = config.get_processed_directory()

        watch_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created watch directory: {watch_dir}")

        processed_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created processed directory: {processed_dir}")

        # Initialize database
        logger.info("Initializing database...")
        db_path = config.get_database_path()
        db = Database(str(db_path))
        db.initialize_schema()
        logger.info(f"Database initialized at: {db_path}")

        logger.info("Application initialization complete")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize application: {e}", exc_info=True)
        return False


def show_error_dialog(title: str, message: str) -> None:
    """
    Show an error dialog to the user.

    Args:
        title: Dialog title
        message: Error message
    """
    # Skip dialog in test mode
    if os.environ.get("PYTEST_CURRENT_TEST"):
        logging.error(f"{title}: {message}")
        return

    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec()


def show_first_run_dialog() -> None:
    """Show a welcome dialog on first run."""
    # Skip dialog in test mode
    if os.environ.get("PYTEST_CURRENT_TEST"):
        logging.info("First run detected (skipping dialog in test mode)")
        return

    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setWindowTitle("Welcome to Agentic Bookkeeper")
    msg_box.setText(
        "Welcome to Agentic Bookkeeper!\n\n"
        "This appears to be your first time running the application.\n\n"
        "The application has been initialized with default settings.\n"
        "You can configure your preferences via File > Settings."
    )
    msg_box.setInformativeText(
        "Please ensure you have:\n"
        "• Set up your watch and archive directories\n"
        "• Configured your LLM provider and API key\n"
        "• Selected your tax jurisdiction"
    )
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec()


def main() -> int:
    """Run the GUI application.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Agentic Bookkeeper")
    app.setOrganizationName("Stephen Bogner")

    try:
        # Load configuration
        config = Config()

        # Configure logging from config
        configure_logging(log_level=config.get_log_level(), log_file=str(config.get_log_file()))

        logger = logging.getLogger(__name__)
        logger.info("=" * 60)
        logger.info("Starting Agentic Bookkeeper application")
        logger.info("=" * 60)

        # Check for first run
        first_run = is_first_run(config)

        if first_run:
            logger.info("First run detected - initializing application")
            if not initialize_application(config):
                show_error_dialog(
                    "Initialization Error",
                    "Failed to initialize the application.\n\n"
                    "Please check the log file for details:\n"
                    f"{config.get_log_file()}",
                )
                return 1

            # Show welcome dialog
            show_first_run_dialog()
        else:
            logger.info("Loading existing application data")

        # Create and show main window
        logger.info("Creating main window")
        main_window = MainWindow(config=config)
        main_window.show()

        logger.info("Application startup complete - entering main event loop")

        # Run application
        exit_code = app.exec()

        logger.info(f"Application exiting with code {exit_code}")
        logger.info("=" * 60)
        return exit_code

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Application failed with error: {e}", exc_info=True)

        # Show error dialog if possible
        try:
            show_error_dialog(
                "Application Error",
                f"An unexpected error occurred:\n\n{str(e)}\n\n"
                "Please check the log file for details.",
            )
        except:
            pass  # GUI may not be available

        return 1


if __name__ == "__main__":
    sys.exit(main())
