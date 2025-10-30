"""
Unit tests for the Settings Dialog.

This module tests the settings dialog functionality including directory
selection, LLM provider configuration, API key management, and tax settings.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-28
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog, QDialogButtonBox
from PySide6.QtCore import Qt, QDate

from agentic_bookkeeper.gui.settings_dialog import SettingsDialog
from agentic_bookkeeper.utils.config import Config


@pytest.fixture
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = Mock(spec=Config)
    config.get_watch_directory.return_value = Path("./data/watch")
    config.get_processed_directory.return_value = Path("./data/processed")
    config.get_current_provider.return_value = "openai"
    config.get_api_key.return_value = "test_key_123"
    config.get.side_effect = lambda key, default=None: {
        "tax_jurisdiction": "CRA",
        "fiscal_year_start": "01-01",
        "watch_directory": "./data/watch",
        "processed_directory": "./data/processed",
    }.get(key, default)
    config.set = Mock()
    config.set_api_key = Mock()
    config.validate = Mock()
    return config


@pytest.fixture
def settings_dialog(qapp, mock_config):
    """Create a settings dialog instance for testing."""
    dialog = SettingsDialog(mock_config)
    yield dialog
    dialog.close()
    dialog.deleteLater()


class TestSettingsDialogInitialization:
    """Test settings dialog initialization."""

    def test_dialog_creation(self, settings_dialog):
        """Test that dialog is created successfully."""
        assert settings_dialog is not None
        assert settings_dialog.windowTitle() == "Settings"

    def test_dialog_minimum_size(self, settings_dialog):
        """Test that dialog has appropriate minimum size."""
        assert settings_dialog.minimumWidth() == 600
        assert settings_dialog.minimumHeight() == 500

    def test_config_initialization(self, qapp):
        """Test dialog creates config if none provided."""
        with patch("agentic_bookkeeper.gui.settings_dialog.Config") as mock_config_class:
            mock_config_instance = Mock()
            mock_config_class.return_value = mock_config_instance

            # Set up required mock methods
            mock_config_instance.get_watch_directory.return_value = Path("./data/watch")
            mock_config_instance.get_processed_directory.return_value = Path("./data/processed")
            mock_config_instance.get_current_provider.return_value = "openai"
            mock_config_instance.get_api_key.return_value = ""
            mock_config_instance.get.side_effect = lambda key, default=None: {
                "tax_jurisdiction": "CRA",
                "fiscal_year_start": "01-01",
            }.get(key, default)

            dialog = SettingsDialog()
            assert dialog.config is not None
            dialog.close()
            dialog.deleteLater()


class TestSettingsDialogWidgets:
    """Test settings dialog widgets."""

    def test_directory_widgets_exist(self, settings_dialog):
        """Test that directory input widgets exist."""
        assert settings_dialog.watch_dir_edit is not None
        assert settings_dialog.archive_dir_edit is not None

    def test_llm_provider_widgets_exist(self, settings_dialog):
        """Test that LLM provider widgets exist."""
        assert settings_dialog.provider_combo is not None
        assert settings_dialog.api_key_edit is not None
        assert settings_dialog.show_api_key_btn is not None

    def test_tax_widgets_exist(self, settings_dialog):
        """Test that tax settings widgets exist."""
        assert settings_dialog.jurisdiction_combo is not None
        assert settings_dialog.fiscal_year_date is not None

    def test_provider_combo_items(self, settings_dialog):
        """Test that provider combo has correct items."""
        expected_providers = ["openai", "anthropic", "xai", "google"]
        actual_providers = [
            settings_dialog.provider_combo.itemText(i)
            for i in range(settings_dialog.provider_combo.count())
        ]
        assert actual_providers == expected_providers

    def test_jurisdiction_combo_items(self, settings_dialog):
        """Test that jurisdiction combo has correct items."""
        expected_jurisdictions = ["CRA", "IRS"]
        actual_jurisdictions = [
            settings_dialog.jurisdiction_combo.itemText(i)
            for i in range(settings_dialog.jurisdiction_combo.count())
        ]
        assert actual_jurisdictions == expected_jurisdictions


class TestSettingsDialogLoadSettings:
    """Test loading settings into the dialog."""

    def test_load_directories(self, settings_dialog, mock_config):
        """Test that directories are loaded correctly."""
        assert settings_dialog.watch_dir_edit.text() == str(Path("./data/watch"))
        assert settings_dialog.archive_dir_edit.text() == str(Path("./data/processed"))

    def test_load_llm_provider(self, settings_dialog, mock_config):
        """Test that LLM provider is loaded correctly."""
        assert settings_dialog.provider_combo.currentText() == "openai"

    def test_load_tax_jurisdiction(self, settings_dialog, mock_config):
        """Test that tax jurisdiction is loaded correctly."""
        assert settings_dialog.jurisdiction_combo.currentText() == "CRA"

    def test_load_fiscal_year_start(self, settings_dialog, mock_config):
        """Test that fiscal year start is loaded correctly."""
        date = settings_dialog.fiscal_year_date.date()
        assert date.month() == 1
        assert date.day() == 1


class TestSettingsDialogValidation:
    """Test settings validation."""

    def test_validate_empty_watch_directory(self, settings_dialog):
        """Test validation fails with empty watch directory."""
        settings_dialog.watch_dir_edit.clear()
        with patch.object(QMessageBox, "warning", return_value=QMessageBox.Ok):
            assert not settings_dialog._validate_settings()

    def test_validate_empty_archive_directory(self, settings_dialog):
        """Test validation fails with empty archive directory."""
        settings_dialog.archive_dir_edit.clear()
        with patch.object(QMessageBox, "warning", return_value=QMessageBox.Ok):
            assert not settings_dialog._validate_settings()

    def test_validate_same_directories(self, settings_dialog):
        """Test validation fails when directories are the same."""
        settings_dialog.watch_dir_edit.setText("/same/directory")
        settings_dialog.archive_dir_edit.setText("/same/directory")
        with patch.object(QMessageBox, "warning", return_value=QMessageBox.Ok):
            assert not settings_dialog._validate_settings()

    def test_validate_short_api_key(self, settings_dialog):
        """Test validation fails with too short API key."""
        settings_dialog.api_key_edit.setText("short")
        with patch.object(QMessageBox, "warning", return_value=QMessageBox.Ok):
            assert not settings_dialog._validate_settings()

    def test_validate_nonexistent_directory_create_yes(self, settings_dialog, tmp_path):
        """Test validation creates directory when user confirms."""
        new_dir = tmp_path / "new_watch_dir"
        settings_dialog.watch_dir_edit.setText(str(new_dir))
        settings_dialog.archive_dir_edit.setText(str(tmp_path / "archive"))

        with patch.object(QMessageBox, "question", return_value=QMessageBox.Yes):
            with patch.object(QMessageBox, "warning", return_value=QMessageBox.Ok):
                # Will create watch dir but archive dir doesn't exist either
                settings_dialog._validate_settings()
                assert new_dir.exists()

    def test_validate_nonexistent_directory_create_no(self, settings_dialog, tmp_path):
        """Test validation fails when user declines to create directory."""
        new_dir = tmp_path / "nonexistent"
        settings_dialog.watch_dir_edit.setText(str(new_dir))
        settings_dialog.archive_dir_edit.setText(str(tmp_path))

        # Disable test mode to test the "user says No" scenario
        with patch.object(settings_dialog, "_is_test_mode", return_value=False):
            with patch.object(QMessageBox, "question", return_value=QMessageBox.No):
                with patch.object(QMessageBox, "warning", return_value=QMessageBox.Ok):
                    assert not settings_dialog._validate_settings()


class TestSettingsDialogSaveSettings:
    """Test saving settings."""

    def test_save_settings_success(self, settings_dialog, mock_config, tmp_path):
        """Test that settings are saved successfully."""
        watch_dir = tmp_path / "watch"
        archive_dir = tmp_path / "archive"
        watch_dir.mkdir()
        archive_dir.mkdir()

        settings_dialog.watch_dir_edit.setText(str(watch_dir))
        settings_dialog.archive_dir_edit.setText(str(archive_dir))
        settings_dialog.provider_combo.setCurrentText("anthropic")
        settings_dialog.api_key_edit.setText("test_api_key_123456")
        settings_dialog.jurisdiction_combo.setCurrentText("IRS")
        settings_dialog.fiscal_year_date.setDate(QDate(2024, 4, 1))

        with patch.object(QMessageBox, "information"):
            settings_dialog._save_settings()

        # Verify configuration was updated
        mock_config.set.assert_any_call("watch_directory", str(watch_dir))
        mock_config.set.assert_any_call("processed_directory", str(archive_dir))
        mock_config.set.assert_any_call("llm_provider", "anthropic")
        mock_config.set_api_key.assert_called_once_with("anthropic", "test_api_key_123456")
        mock_config.set.assert_any_call("tax_jurisdiction", "IRS")
        mock_config.set.assert_any_call("fiscal_year_start", "04-01")
        mock_config.validate.assert_called_once()

    def test_save_settings_no_api_key_change(self, settings_dialog, mock_config, tmp_path):
        """Test that API key is not changed if field is empty."""
        watch_dir = tmp_path / "watch"
        archive_dir = tmp_path / "archive"
        watch_dir.mkdir()
        archive_dir.mkdir()

        settings_dialog.watch_dir_edit.setText(str(watch_dir))
        settings_dialog.archive_dir_edit.setText(str(archive_dir))
        settings_dialog.api_key_edit.clear()  # Don't change API key

        with patch.object(QMessageBox, "information"):
            settings_dialog._save_settings()

        # Verify API key was not changed
        mock_config.set_api_key.assert_not_called()

    def test_save_settings_validation_fails(self, settings_dialog, mock_config):
        """Test that settings are not saved if validation fails."""
        settings_dialog.watch_dir_edit.clear()

        with patch.object(QMessageBox, "warning", return_value=QMessageBox.Ok):
            settings_dialog._save_settings()

        # Verify configuration was not updated
        mock_config.validate.assert_not_called()

    def test_save_settings_exception_handling(self, settings_dialog, mock_config, tmp_path):
        """Test error handling when save fails."""
        watch_dir = tmp_path / "watch"
        archive_dir = tmp_path / "archive"
        watch_dir.mkdir()
        archive_dir.mkdir()

        settings_dialog.watch_dir_edit.setText(str(watch_dir))
        settings_dialog.archive_dir_edit.setText(str(archive_dir))

        # Make validate raise an exception
        mock_config.validate.side_effect = ValueError("Invalid configuration")

        with patch.object(QMessageBox, "critical"):
            settings_dialog._save_settings()

        # Dialog should still be open (not accepted)
        assert settings_dialog.result() != SettingsDialog.DialogCode.Accepted


class TestSettingsDialogInteractions:
    """Test user interactions with the dialog."""

    def test_browse_directory_selection(self, settings_dialog):
        """Test directory browse button functionality."""
        test_dir = "/test/directory"
        with patch.object(QFileDialog, "getExistingDirectory", return_value=test_dir):
            settings_dialog._browse_directory(settings_dialog.watch_dir_edit)
            assert settings_dialog.watch_dir_edit.text() == test_dir

    def test_browse_directory_cancelled(self, settings_dialog):
        """Test directory browse cancellation."""
        original_text = settings_dialog.watch_dir_edit.text()
        with patch.object(QFileDialog, "getExistingDirectory", return_value=""):
            settings_dialog._browse_directory(settings_dialog.watch_dir_edit)
            assert settings_dialog.watch_dir_edit.text() == original_text

    def test_toggle_api_key_visibility(self, settings_dialog):
        """Test toggling API key visibility."""
        from PySide6.QtWidgets import QLineEdit

        # Initially hidden
        assert settings_dialog.api_key_edit.echoMode() == QLineEdit.Password
        assert settings_dialog.show_api_key_btn.text() == "Show"

        # Click to show
        settings_dialog.show_api_key_btn.setChecked(True)
        settings_dialog._toggle_api_key_visibility()
        assert settings_dialog.api_key_edit.echoMode() == QLineEdit.Normal
        assert settings_dialog.show_api_key_btn.text() == "Hide"

        # Click to hide again
        settings_dialog.show_api_key_btn.setChecked(False)
        settings_dialog._toggle_api_key_visibility()
        assert settings_dialog.api_key_edit.echoMode() == QLineEdit.Password
        assert settings_dialog.show_api_key_btn.text() == "Show"

    def test_provider_changed_with_api_key(self, settings_dialog, mock_config):
        """Test provider change when API key exists."""
        mock_config.get_api_key.return_value = "existing_key"
        settings_dialog._on_provider_changed("anthropic")

        assert "Current key set" in settings_dialog.api_key_edit.placeholderText()

    def test_provider_changed_without_api_key(self, settings_dialog, mock_config):
        """Test provider change when no API key exists."""
        mock_config.get_api_key.return_value = ""
        settings_dialog._on_provider_changed("google")

        assert "Enter API key" in settings_dialog.api_key_edit.placeholderText()

    def test_get_config(self, settings_dialog, mock_config):
        """Test getting configuration from dialog."""
        config = settings_dialog.get_config()
        assert config == mock_config


class TestSettingsDialogButtons:
    """Test dialog button functionality."""

    def test_save_button_exists(self, settings_dialog):
        """Test that save button exists."""
        button_box = settings_dialog.findChild(QDialogButtonBox)
        assert button_box is not None
        save_button = button_box.button(QDialogButtonBox.Save)
        assert save_button is not None

    def test_cancel_button_exists(self, settings_dialog):
        """Test that cancel button exists."""
        button_box = settings_dialog.findChild(QDialogButtonBox)
        assert button_box is not None
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        assert cancel_button is not None
