"""
Unit tests for main application entry point.

Tests first-run detection, initialization, error handling, and application startup.
"""

import logging
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from PySide6.QtWidgets import QApplication, QMessageBox

from agentic_bookkeeper.main import (
    configure_logging,
    is_first_run,
    initialize_application,
    show_error_dialog,
    show_first_run_dialog,
    main,
)
from agentic_bookkeeper.utils.config import Config


class TestConfigureLogging:
    """Test logging configuration."""

    def test_configure_logging_info_level(self, tmp_path):
        """Test logging configuration with INFO level."""
        log_file = tmp_path / "test.log"
        configure_logging(log_level="INFO", log_file=str(log_file))

        logger = logging.getLogger("test_logger")
        assert logger.getEffectiveLevel() <= logging.INFO

    def test_configure_logging_debug_level(self):
        """Test logging configuration with DEBUG level."""
        configure_logging(log_level="DEBUG")

        logger = logging.getLogger("test_logger")
        assert logger.getEffectiveLevel() <= logging.DEBUG

    def test_configure_logging_creates_log_directory(self, tmp_path):
        """Test that log directory is created if it doesn't exist."""
        log_file = tmp_path / "logs" / "test.log"
        configure_logging(log_level="INFO", log_file=str(log_file))

        assert log_file.parent.exists()

    def test_configure_logging_without_file(self):
        """Test logging configuration without log file."""
        configure_logging(log_level="INFO", log_file=None)

        logger = logging.getLogger("test_logger")
        assert logger.getEffectiveLevel() <= logging.INFO


class TestIsFirstRun:
    """Test first-run detection."""

    def test_is_first_run_no_database(self, tmp_path, mock_config):
        """Test first-run detection when database doesn't exist."""
        mock_config.get_database_path.return_value = tmp_path / "bookkeeper.db"
        assert is_first_run(mock_config) is True

    def test_is_first_run_database_exists(self, tmp_path, mock_config):
        """Test first-run detection when database exists."""
        db_path = tmp_path / "bookkeeper.db"
        db_path.touch()
        mock_config.get_database_path.return_value = db_path
        assert is_first_run(mock_config) is False


class TestInitializeApplication:
    """Test application initialization."""

    def test_initialize_application_success(self, tmp_path, mock_config):
        """Test successful application initialization."""
        watch_dir = tmp_path / "watch"
        processed_dir = tmp_path / "processed"
        db_path = tmp_path / "bookkeeper.db"

        mock_config.get_watch_directory.return_value = watch_dir
        mock_config.get_processed_directory.return_value = processed_dir
        mock_config.get_database_path.return_value = db_path

        with patch("agentic_bookkeeper.main.Database") as mock_db_class:
            mock_db = Mock()
            mock_db_class.return_value = mock_db

            result = initialize_application(mock_config)

            assert result is True
            assert watch_dir.exists()
            assert processed_dir.exists()
            mock_db.initialize_schema.assert_called_once()

    def test_initialize_application_failure(self, tmp_path, mock_config):
        """Test application initialization failure."""
        mock_config.get_watch_directory.side_effect = Exception("Test error")

        result = initialize_application(mock_config)

        assert result is False

    def test_initialize_application_creates_directories(self, tmp_path, mock_config):
        """Test that initialization creates necessary directories."""
        watch_dir = tmp_path / "watch"
        processed_dir = tmp_path / "processed"
        db_path = tmp_path / "data" / "bookkeeper.db"

        mock_config.get_watch_directory.return_value = watch_dir
        mock_config.get_processed_directory.return_value = processed_dir
        mock_config.get_database_path.return_value = db_path

        with patch("agentic_bookkeeper.main.Database") as mock_db_class:
            mock_db = Mock()
            mock_db_class.return_value = mock_db

            initialize_application(mock_config)

            assert watch_dir.exists()
            assert processed_dir.exists()


class TestShowErrorDialog:
    """Test error dialog display."""

    def test_show_error_dialog_creation(self, qtbot):
        """Test error dialog is created with correct properties."""
        # Temporarily disable test mode to test dialog creation
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(QMessageBox, "exec") as mock_exec:
                show_error_dialog("Test Error", "This is a test error")
                mock_exec.assert_called_once()

    def test_show_error_dialog_parameters(self, qtbot):
        """Test error dialog has correct title and message."""
        title = "Test Title"
        message = "Test Message"

        # Temporarily disable test mode to test dialog creation
        with patch.dict("os.environ", {}, clear=True):
            with patch("agentic_bookkeeper.main.QMessageBox") as mock_msg_box_class:
                mock_msg_box = Mock()
                mock_msg_box_class.return_value = mock_msg_box
                # Mock the Icon enum
                mock_msg_box_class.Critical = QMessageBox.Icon.Critical

                show_error_dialog(title, message)

                mock_msg_box.setWindowTitle.assert_called_once_with(title)
                mock_msg_box.setText.assert_called_once_with(message)
                mock_msg_box.setIcon.assert_called_once()


class TestShowFirstRunDialog:
    """Test first-run welcome dialog."""

    def test_show_first_run_dialog_creation(self, qtbot):
        """Test first-run dialog is created."""
        # Temporarily disable test mode to test dialog creation
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(QMessageBox, "exec") as mock_exec:
                show_first_run_dialog()
                mock_exec.assert_called_once()

    def test_show_first_run_dialog_content(self, qtbot):
        """Test first-run dialog has welcome content."""
        # Temporarily disable test mode to test dialog creation
        with patch.dict("os.environ", {}, clear=True):
            with patch("agentic_bookkeeper.main.QMessageBox") as mock_msg_box_class:
                mock_msg_box = Mock()
                mock_msg_box_class.return_value = mock_msg_box
                # Mock the Icon enum
                mock_msg_box_class.Information = QMessageBox.Icon.Information

                show_first_run_dialog()

                mock_msg_box.setWindowTitle.assert_called_once_with("Welcome to Agentic Bookkeeper")
                mock_msg_box.setIcon.assert_called_once()


class TestMain:
    """Test main application entry point."""

    def test_main_first_run_success(self, qtbot, tmp_path, monkeypatch):
        """Test main function on first run with successful initialization."""
        # Mock sys.argv to prevent Qt from processing test runner arguments
        monkeypatch.setattr(sys, "argv", ["test"])

        with patch("agentic_bookkeeper.main.QApplication") as mock_app_class, patch(
            "agentic_bookkeeper.main.Config"
        ) as mock_config_class, patch(
            "agentic_bookkeeper.main.is_first_run"
        ) as mock_first_run, patch(
            "agentic_bookkeeper.main.initialize_application"
        ) as mock_init, patch(
            "agentic_bookkeeper.main.show_first_run_dialog"
        ) as mock_dialog, patch(
            "agentic_bookkeeper.main.MainWindow"
        ) as mock_window_class:

            mock_config = Mock()
            mock_config.get_log_level.return_value = "INFO"
            mock_config.get_log_file.return_value = tmp_path / "test.log"
            mock_config_class.return_value = mock_config

            mock_first_run.return_value = True
            mock_init.return_value = True

            mock_app = Mock()
            mock_app.exec.return_value = 0
            mock_app_class.return_value = mock_app

            mock_window = Mock()
            mock_window_class.return_value = mock_window

            exit_code = main()

            assert exit_code == 0
            mock_init.assert_called_once_with(mock_config)
            mock_dialog.assert_called_once()
            mock_window.show.assert_called_once()

    def test_main_existing_installation(self, qtbot, tmp_path, monkeypatch):
        """Test main function with existing installation."""
        monkeypatch.setattr(sys, "argv", ["test"])

        with patch("agentic_bookkeeper.main.QApplication") as mock_app_class, patch(
            "agentic_bookkeeper.main.Config"
        ) as mock_config_class, patch(
            "agentic_bookkeeper.main.is_first_run"
        ) as mock_first_run, patch(
            "agentic_bookkeeper.main.initialize_application"
        ) as mock_init, patch(
            "agentic_bookkeeper.main.MainWindow"
        ) as mock_window_class:

            mock_config = Mock()
            mock_config.get_log_level.return_value = "INFO"
            mock_config.get_log_file.return_value = tmp_path / "test.log"
            mock_config_class.return_value = mock_config

            mock_first_run.return_value = False

            mock_app = Mock()
            mock_app.exec.return_value = 0
            mock_app_class.return_value = mock_app

            mock_window = Mock()
            mock_window_class.return_value = mock_window

            exit_code = main()

            assert exit_code == 0
            mock_init.assert_not_called()
            mock_window.show.assert_called_once()

    def test_main_initialization_failure(self, qtbot, tmp_path, monkeypatch):
        """Test main function when initialization fails."""
        monkeypatch.setattr(sys, "argv", ["test"])

        with patch("agentic_bookkeeper.main.QApplication") as mock_app_class, patch(
            "agentic_bookkeeper.main.Config"
        ) as mock_config_class, patch(
            "agentic_bookkeeper.main.is_first_run"
        ) as mock_first_run, patch(
            "agentic_bookkeeper.main.initialize_application"
        ) as mock_init, patch(
            "agentic_bookkeeper.main.show_error_dialog"
        ) as mock_error:

            mock_config = Mock()
            mock_config.get_log_level.return_value = "INFO"
            mock_config.get_log_file.return_value = tmp_path / "test.log"
            mock_config_class.return_value = mock_config

            mock_app = Mock()
            mock_app_class.return_value = mock_app

            mock_first_run.return_value = True
            mock_init.return_value = False

            exit_code = main()

            assert exit_code == 1
            mock_error.assert_called_once()

    def test_main_exception_handling(self, qtbot, monkeypatch):
        """Test main function exception handling."""
        monkeypatch.setattr(sys, "argv", ["test"])

        with patch("agentic_bookkeeper.main.QApplication") as mock_app_class, patch(
            "agentic_bookkeeper.main.Config"
        ) as mock_config_class, patch("agentic_bookkeeper.main.show_error_dialog") as mock_error:

            mock_app = Mock()
            mock_app_class.return_value = mock_app

            mock_config_class.side_effect = Exception("Test configuration error")

            exit_code = main()

            assert exit_code == 1

    def test_main_configures_logging(self, qtbot, tmp_path, monkeypatch):
        """Test that main function configures logging."""
        monkeypatch.setattr(sys, "argv", ["test"])

        with patch("agentic_bookkeeper.main.QApplication") as mock_app_class, patch(
            "agentic_bookkeeper.main.Config"
        ) as mock_config_class, patch(
            "agentic_bookkeeper.main.configure_logging"
        ) as mock_logging, patch(
            "agentic_bookkeeper.main.is_first_run"
        ) as mock_first_run, patch(
            "agentic_bookkeeper.main.MainWindow"
        ) as mock_window_class:

            mock_config = Mock()
            mock_config.get_log_level.return_value = "DEBUG"
            log_file = tmp_path / "test.log"
            mock_config.get_log_file.return_value = log_file
            mock_config_class.return_value = mock_config

            mock_app = Mock()
            mock_app.exec.return_value = 0
            mock_app_class.return_value = mock_app

            mock_first_run.return_value = False

            main()

            mock_logging.assert_called_once_with(log_level="DEBUG", log_file=str(log_file))


# Pytest fixtures
@pytest.fixture
def mock_config():
    """Create a mock Config instance."""
    config = Mock(spec=Config)
    config.get_watch_directory.return_value = Path("./watch")
    config.get_processed_directory.return_value = Path("./processed")
    config.get_database_path.return_value = Path("./bookkeeper.db")
    config.get_log_level.return_value = "INFO"
    config.get_log_file.return_value = Path("./logs/test.log")
    return config
