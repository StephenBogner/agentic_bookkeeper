"""
Settings dialog for Agentic Bookkeeper.

This module provides a comprehensive settings dialog for configuring
application preferences including directories, LLM providers, API keys,
and tax settings.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-28
"""

import logging
import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QDateEdit,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from ..utils.config import Config

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """
    Settings dialog for configuring application preferences.

    Provides UI for configuring:
    - Watch and archive directories
    - LLM provider selection
    - API key management (masked input)
    - Tax jurisdiction (CRA/IRS)
    - Fiscal year start date
    """

    def __init__(self, config: Optional[Config] = None, parent=None):
        """
        Initialize the settings dialog.

        Args:
            config: Configuration manager instance. If None, creates a new one.
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = config or Config()
        self._init_ui()
        self._load_settings()
        logger.debug("Settings dialog initialized")

    def _is_test_mode(self) -> bool:
        """Check if running in test mode."""
        return os.environ.get("PYTEST_CURRENT_TEST") is not None or hasattr(self, "_testing_mode")

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        # Title
        title = QLabel("Application Settings")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)

        # Directory Settings Group
        dir_group = self._create_directory_group()
        main_layout.addWidget(dir_group)

        # LLM Provider Settings Group
        llm_group = self._create_llm_group()
        main_layout.addWidget(llm_group)

        # Tax Settings Group
        tax_group = self._create_tax_group()
        main_layout.addWidget(tax_group)

        # Add stretch to push buttons to bottom
        main_layout.addStretch()

        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._save_settings)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def _create_directory_group(self) -> QGroupBox:
        """Create the directory settings group."""
        group = QGroupBox("Directory Settings")
        layout = QFormLayout()

        # Watch directory
        watch_layout = QHBoxLayout()
        self.watch_dir_edit = QLineEdit()
        self.watch_dir_edit.setPlaceholderText("Select directory to watch for new documents")
        self.watch_dir_edit.setToolTip(
            "Directory where the system will monitor for new documents. "
            "Documents placed here will be automatically processed and extracted."
        )
        watch_browse_btn = QPushButton("Browse...")
        watch_browse_btn.setToolTip("Open directory browser to select watch directory.")
        watch_browse_btn.clicked.connect(lambda: self._browse_directory(self.watch_dir_edit))
        watch_layout.addWidget(self.watch_dir_edit, 1)
        watch_layout.addWidget(watch_browse_btn)
        layout.addRow("Watch Directory:", watch_layout)

        # Archive/processed directory
        archive_layout = QHBoxLayout()
        self.archive_dir_edit = QLineEdit()
        self.archive_dir_edit.setPlaceholderText("Select directory for processed documents")
        self.archive_dir_edit.setToolTip(
            "Directory where processed documents will be moved after extraction. "
            "This keeps your watch directory clean and organized."
        )
        archive_browse_btn = QPushButton("Browse...")
        archive_browse_btn.setToolTip("Open directory browser to select archive directory.")
        archive_browse_btn.clicked.connect(lambda: self._browse_directory(self.archive_dir_edit))
        archive_layout.addWidget(self.archive_dir_edit, 1)
        archive_layout.addWidget(archive_browse_btn)
        layout.addRow("Archive Directory:", archive_layout)

        group.setLayout(layout)
        return group

    def _create_llm_group(self) -> QGroupBox:
        """Create the LLM provider settings group."""
        group = QGroupBox("LLM Provider Settings")
        layout = QFormLayout()

        # Provider selection
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["openai", "anthropic", "xai", "google"])
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        self.provider_combo.setToolTip(
            "Select the LLM provider to use for document extraction. "
            "Each provider requires its own API key configured below."
        )
        layout.addRow("LLM Provider:", self.provider_combo)

        # API key input (masked)
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("Enter API key for selected provider")
        self.api_key_edit.setToolTip(
            "API key for the selected LLM provider. Keys are stored encrypted. "
            "Leave blank to keep the existing key unchanged."
        )

        # Show/hide API key button
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(self.api_key_edit, 1)
        self.show_api_key_btn = QPushButton("Show")
        self.show_api_key_btn.setCheckable(True)
        self.show_api_key_btn.setMaximumWidth(60)
        self.show_api_key_btn.setToolTip("Toggle visibility of API key (show/hide).")
        self.show_api_key_btn.clicked.connect(self._toggle_api_key_visibility)
        api_key_layout.addWidget(self.show_api_key_btn)

        layout.addRow("API Key:", api_key_layout)

        # Help text
        help_label = QLabel("Note: API keys are stored encrypted. Leave blank to keep current key.")
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addRow("", help_label)

        group.setLayout(layout)
        return group

    def _create_tax_group(self) -> QGroupBox:
        """Create the tax settings group."""
        group = QGroupBox("Tax Settings")
        layout = QFormLayout()

        # Tax jurisdiction
        self.jurisdiction_combo = QComboBox()
        self.jurisdiction_combo.addItems(["CRA", "IRS"])
        self.jurisdiction_combo.setToolTip(
            "Tax jurisdiction for reporting and category classification. "
            "CRA for Canada, IRS for United States. Affects available transaction categories."
        )
        layout.addRow("Tax Jurisdiction:", self.jurisdiction_combo)

        # Fiscal year start date
        self.fiscal_year_date = QDateEdit()
        self.fiscal_year_date.setCalendarPopup(True)
        self.fiscal_year_date.setDisplayFormat("MM-dd")
        # Set a default date (January 1st)
        self.fiscal_year_date.setDate(QDate(2024, 1, 1))
        self.fiscal_year_date.setToolTip(
            "Fiscal year start date (month and day) for annual reports. "
            "Click to open calendar picker. Common options: 01-01 (calendar year) or 04-01 (UK tax year)."
        )
        layout.addRow("Fiscal Year Start:", self.fiscal_year_date)

        # Help text
        help_label = QLabel("Fiscal year start date is used for annual report calculations.")
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addRow("", help_label)

        group.setLayout(layout)
        return group

    def _browse_directory(self, line_edit: QLineEdit) -> None:
        """
        Open directory browser dialog.

        Args:
            line_edit: Line edit widget to update with selected directory
        """
        current_dir = line_edit.text() or str(Path.home())
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            current_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        if directory:
            line_edit.setText(directory)
            logger.debug(f"Directory selected: {directory}")

    def _toggle_api_key_visibility(self) -> None:
        """Toggle API key visibility (show/hide)."""
        if self.show_api_key_btn.isChecked():
            self.api_key_edit.setEchoMode(QLineEdit.Normal)
            self.show_api_key_btn.setText("Hide")
        else:
            self.api_key_edit.setEchoMode(QLineEdit.Password)
            self.show_api_key_btn.setText("Show")

    def _on_provider_changed(self, provider: str) -> None:
        """
        Handle LLM provider selection change.

        Args:
            provider: Selected provider name
        """
        # Load API key for the selected provider
        api_key = self.config.get_api_key(provider)
        # Show masked version if key exists, otherwise clear
        if api_key:
            self.api_key_edit.setPlaceholderText("••• Current key set (leave blank to keep)")
            self.api_key_edit.clear()
        else:
            self.api_key_edit.setPlaceholderText(f"Enter API key for {provider}")
            self.api_key_edit.clear()

        logger.debug(f"Provider changed to: {provider}")

    def _load_settings(self) -> None:
        """Load current settings from configuration."""
        try:
            # Load directories
            self.watch_dir_edit.setText(str(self.config.get_watch_directory()))
            self.archive_dir_edit.setText(str(self.config.get_processed_directory()))

            # Load LLM provider
            provider = self.config.get_current_provider()
            index = self.provider_combo.findText(provider)
            if index >= 0:
                self.provider_combo.setCurrentIndex(index)

            # Load tax jurisdiction
            jurisdiction = self.config.get("tax_jurisdiction", "CRA")
            index = self.jurisdiction_combo.findText(jurisdiction)
            if index >= 0:
                self.jurisdiction_combo.setCurrentIndex(index)

            # Load fiscal year start
            fiscal_year_str = self.config.get("fiscal_year_start", "01-01")
            try:
                month, day = fiscal_year_str.split("-")
                date = QDate(2024, int(month), int(day))  # Year doesn't matter
                self.fiscal_year_date.setDate(date)
            except Exception as e:
                logger.warning(f"Failed to parse fiscal year date: {e}")
                self.fiscal_year_date.setDate(QDate(2024, 1, 1))

            logger.info("Settings loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            if not self._is_test_mode():
                QMessageBox.warning(self, "Load Error", f"Failed to load settings: {str(e)}")

    def _validate_settings(self) -> bool:
        """
        Validate all settings before saving.

        Returns:
            True if all settings are valid, False otherwise
        """
        errors = []

        # Validate watch directory
        watch_dir = self.watch_dir_edit.text().strip()
        if not watch_dir:
            errors.append("Watch directory is required")
        elif not Path(watch_dir).exists():
            # Ask if user wants to create it (auto-accept in test mode)
            if self._is_test_mode():
                response = QMessageBox.Yes
            else:
                response = QMessageBox.question(
                    self,
                    "Create Directory?",
                    f"Watch directory does not exist:\n{watch_dir}\n\nCreate it now?",
                    QMessageBox.Yes | QMessageBox.No,
                )
            if response == QMessageBox.Yes:
                try:
                    Path(watch_dir).mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"Failed to create watch directory: {str(e)}")
            else:
                errors.append("Watch directory does not exist")

        # Validate archive directory
        archive_dir = self.archive_dir_edit.text().strip()
        if not archive_dir:
            errors.append("Archive directory is required")
        elif not Path(archive_dir).exists():
            # Ask if user wants to create it (auto-accept in test mode)
            if self._is_test_mode():
                response = QMessageBox.Yes
            else:
                response = QMessageBox.question(
                    self,
                    "Create Directory?",
                    f"Archive directory does not exist:\n{archive_dir}\n\nCreate it now?",
                    QMessageBox.Yes | QMessageBox.No,
                )
            if response == QMessageBox.Yes:
                try:
                    Path(archive_dir).mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"Failed to create archive directory: {str(e)}")
            else:
                errors.append("Archive directory does not exist")

        # Check if directories are the same
        if watch_dir and archive_dir and Path(watch_dir) == Path(archive_dir):
            errors.append("Watch and archive directories cannot be the same")

        # Validate API key if entered
        api_key = self.api_key_edit.text().strip()
        if api_key:
            if len(api_key) < 10:
                errors.append("API key seems too short (minimum 10 characters)")

        # Show errors if any
        if errors:
            if not self._is_test_mode():
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Please correct the following errors:\n\n"
                    + "\n".join(f"• {e}" for e in errors),
                )
            return False

        return True

    def _save_settings(self) -> None:
        """Save settings to configuration."""
        if not self._validate_settings():
            return

        try:
            # Save directories
            self.config.set("watch_directory", self.watch_dir_edit.text().strip())
            self.config.set("processed_directory", self.archive_dir_edit.text().strip())

            # Save LLM provider
            provider = self.provider_combo.currentText()
            self.config.set("llm_provider", provider)

            # Save API key if entered
            api_key = self.api_key_edit.text().strip()
            if api_key:
                self.config.set_api_key(provider, api_key)
                logger.info(f"API key updated for provider: {provider}")

            # Save tax jurisdiction
            jurisdiction = self.jurisdiction_combo.currentText()
            self.config.set("tax_jurisdiction", jurisdiction)

            # Save fiscal year start
            date = self.fiscal_year_date.date()
            fiscal_year_str = f"{date.month():02d}-{date.day():02d}"
            self.config.set("fiscal_year_start", fiscal_year_str)

            # Validate configuration
            self.config.validate()

            logger.info("Settings saved successfully")
            if not self._is_test_mode():
                QMessageBox.information(
                    self, "Settings Saved", "Settings have been saved successfully."
                )

            self.accept()

        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            if not self._is_test_mode():
                QMessageBox.critical(self, "Save Error", f"Failed to save settings:\n{str(e)}")

    def get_config(self) -> Config:
        """
        Get the updated configuration.

        Returns:
            Updated configuration manager instance
        """
        return self.config
