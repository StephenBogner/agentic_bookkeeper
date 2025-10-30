"""Main window for the Agentic Bookkeeper GUI application.

Package Name: agentic_bookkeeper
File Name: main_window.py
Author: Stephen Bogner, P.Eng.
LLM: claude-sonnet-4-5-20250929
Ownership: Stephen Bogner - All Rights Reserved.  See LICENSE
Date Created: 2025-10-27
"""

import logging
import os
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QCloseEvent
from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QStatusBar,
    QDialog,
)

from agentic_bookkeeper.gui.dashboard_widget import DashboardWidget
from agentic_bookkeeper.gui.settings_dialog import SettingsDialog
from agentic_bookkeeper.gui.transactions_widget import TransactionsWidget
from agentic_bookkeeper.utils.config import Config


class MainWindow(QMainWindow):
    """
    Main application window for Agentic Bookkeeper.

    Provides the primary user interface with menu bar, tab widget,
    and status bar for the bookkeeping application.
    """

    def __init__(self, config: Optional[Config] = None, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the main window.

        Args:
            config: Configuration manager instance. If None, creates a new one.
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing MainWindow")

        self.config = config or Config()

        self._setup_window()
        self._create_menu_bar()
        self._create_tab_widget()
        self._create_status_bar()

        self.logger.info("MainWindow initialization complete")

    def _setup_window(self) -> None:
        """Configure the main window properties."""
        self.setWindowTitle("Agentic Bookkeeper")
        self.setMinimumSize(QSize(1024, 768))
        self.resize(QSize(1280, 900))

        # Try to set application icon if it exists
        icon_path = (
            Path(__file__).parent.parent.parent.parent / "resources" / "icons" / "app_icon.png"
        )
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            self.logger.info(f"Application icon loaded from {icon_path}")
        else:
            self.logger.warning(f"Application icon not found at {icon_path}")

    def _create_menu_bar(self) -> None:
        """Create the menu bar with File, View, and Help menus."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        # Settings action
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.setStatusTip("Configure application settings")
        settings_action.setToolTip(
            "Open settings dialog to configure API keys, directories, and preferences"
        )
        settings_action.triggered.connect(self._show_settings_dialog)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.setToolTip("Close Agentic Bookkeeper")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menu_bar.addMenu("&View")

        # Dashboard tab action
        dashboard_action = QAction("&Dashboard", self)
        dashboard_action.setShortcut("Ctrl+1")
        dashboard_action.setStatusTip("Switch to Dashboard view")
        dashboard_action.setToolTip("View application dashboard and monitoring controls")
        dashboard_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        view_menu.addAction(dashboard_action)

        # Transactions tab action
        transactions_action = QAction("&Transactions", self)
        transactions_action.setShortcut("Ctrl+2")
        transactions_action.setStatusTip("Switch to Transactions view")
        transactions_action.setToolTip("View and manage transaction records")
        transactions_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        view_menu.addAction(transactions_action)

        # Reports tab action
        reports_action = QAction("&Reports", self)
        reports_action.setShortcut("Ctrl+3")
        reports_action.setStatusTip("Switch to Reports view")
        reports_action.setToolTip("Generate and export financial reports")
        reports_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        view_menu.addAction(reports_action)

        view_menu.addSeparator()

        # Refresh action
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.setStatusTip("Refresh current view")
        refresh_action.setToolTip("Reload data in the current view")
        refresh_action.triggered.connect(self._refresh_current_view)
        view_menu.addAction(refresh_action)

        # Help menu
        help_menu = menu_bar.addMenu("&Help")

        # User Guide action
        user_guide_action = QAction("&User Guide", self)
        user_guide_action.setShortcut("F1")
        user_guide_action.setStatusTip("Open user guide")
        user_guide_action.setToolTip("View comprehensive user guide and documentation")
        user_guide_action.triggered.connect(self._show_user_guide)
        help_menu.addAction(user_guide_action)

        # Keyboard Shortcuts action
        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.setShortcut("Ctrl+/")
        shortcuts_action.setStatusTip("View keyboard shortcuts")
        shortcuts_action.setToolTip("Display list of available keyboard shortcuts")
        shortcuts_action.triggered.connect(self._show_shortcuts_dialog)
        help_menu.addAction(shortcuts_action)

        help_menu.addSeparator()

        # About action
        about_action = QAction("&About Agentic Bookkeeper", self)
        about_action.setStatusTip("About Agentic Bookkeeper")
        about_action.setToolTip("View application information and version")
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

        self.logger.info("Menu bar created")

    def _create_tab_widget(self) -> None:
        """Create the central tab widget for main views."""
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(False)

        # Create dashboard tab with actual widget
        self.dashboard_widget = DashboardWidget()
        self.tab_widget.addTab(self.dashboard_widget, "Dashboard")
        self.tab_widget.setTabToolTip(
            0, "Monitor document processing and view summary statistics (Ctrl+1)"
        )

        # Create transactions tab with actual widget
        self.transactions_widget = TransactionsWidget()
        self.tab_widget.addTab(self.transactions_widget, "Transactions")
        self.tab_widget.setTabToolTip(1, "View and manage all transaction records (Ctrl+2)")

        # Create placeholder tab for reports
        self._add_placeholder_tab("Reports", "Reports view coming soon")
        self.tab_widget.setTabToolTip(2, "Generate and export financial reports (Ctrl+3)")

        self.setCentralWidget(self.tab_widget)
        self.logger.info("Tab widget created with dashboard and placeholder tabs")

    def _add_placeholder_tab(self, title: str, message: str) -> None:
        """
        Add a placeholder tab with a message.

        Args:
            title: Tab title
            message: Message to display in the tab
        """
        widget = QWidget()
        layout = QVBoxLayout()

        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)
        widget.setLayout(layout)

        self.tab_widget.addTab(widget, title)

    def _create_status_bar(self) -> None:
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready", 5000)
        self.logger.info("Status bar created")

    def _show_settings_dialog(self) -> None:
        """Display the Settings dialog."""
        self.logger.info("Opening settings dialog")
        dialog = SettingsDialog(self.config, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update configuration
            self.config = dialog.get_config()
            self.show_status_message("Settings saved successfully")
            self.logger.info("Settings updated successfully")
        else:
            self.logger.info("Settings dialog cancelled")

    def _show_about_dialog(self) -> None:
        """Display the About dialog."""
        about_text = (
            "<h2>Agentic Bookkeeper</h2>"
            "<p>Version 1.0.0</p>"
            "<p>An intelligent bookkeeping automation system that uses "
            "AI to extract transaction data from financial documents.</p>"
            "<p><b>Author:</b> Stephen Bogner, P.Eng.</p>"
            "<p><b>Copyright:</b> 2025 Stephen Bogner - All Rights Reserved</p>"
        )

        QMessageBox.about(self, "About Agentic Bookkeeper", about_text)
        self.logger.info("About dialog displayed")

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle window close event.

        Args:
            event: Close event
        """
        self.logger.info("MainWindow close event triggered")

        # Skip confirmation dialog during automated testing
        if os.environ.get("PYTEST_CURRENT_TEST") or hasattr(self, "_testing_mode"):
            self.logger.info("Test mode detected - auto-accepting close event")
            event.accept()
            return

        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit Agentic Bookkeeper?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.logger.info("User confirmed exit")
            event.accept()
        else:
            self.logger.info("User cancelled exit")
            event.ignore()

    def show_status_message(self, message: str, timeout: int = 5000) -> None:
        """
        Display a message in the status bar.

        Args:
            message: Message to display
            timeout: Time in milliseconds to display the message (0 for permanent)
        """
        self.status_bar.showMessage(message, timeout)
        self.logger.debug(f"Status message: {message}")

    def get_tab_widget(self) -> QTabWidget:
        """
        Get the central tab widget.

        Returns:
            The tab widget
        """
        return self.tab_widget

    def get_dashboard_widget(self) -> DashboardWidget:
        """
        Get the dashboard widget.

        Returns:
            The dashboard widget
        """
        return self.dashboard_widget

    def _refresh_current_view(self) -> None:
        """Refresh the currently active tab/view."""
        current_index = self.tab_widget.currentIndex()
        current_widget = self.tab_widget.currentWidget()

        self.logger.info(f"Refreshing view at tab index {current_index}")

        # Refresh based on the current tab
        if current_index == 0:  # Dashboard
            if hasattr(current_widget, "refresh"):
                current_widget.refresh()
            self.show_status_message("Dashboard refreshed")
        elif current_index == 1:  # Transactions
            if hasattr(current_widget, "load_transactions"):
                current_widget.load_transactions()
            self.show_status_message("Transactions refreshed")
        elif current_index == 2:  # Reports
            self.show_status_message("Reports view refreshed")
        else:
            self.show_status_message("View refreshed")

    def _show_user_guide(self) -> None:
        """Open the user guide documentation."""
        import webbrowser
        from pathlib import Path

        # Try to open local user guide
        docs_path = Path(__file__).parent.parent.parent.parent / "docs" / "USER_GUIDE.md"

        if docs_path.exists():
            # On Windows, open with default markdown viewer or browser
            webbrowser.open(f"file://{docs_path.absolute()}")
            self.show_status_message("User guide opened")
            self.logger.info(f"Opened user guide: {docs_path}")
        else:
            QMessageBox.information(
                self,
                "User Guide",
                "User guide documentation is available in the docs/ directory.\n\n"
                "Please see docs/USER_GUIDE.md for comprehensive documentation.",
            )
            self.logger.warning(f"User guide not found at {docs_path}")

    def _show_shortcuts_dialog(self) -> None:
        """Display the keyboard shortcuts reference."""
        shortcuts_text = """
        <h2>Keyboard Shortcuts</h2>

        <h3>File Menu</h3>
        <table>
        <tr><td><b>Ctrl+,</b></td><td>Open Settings</td></tr>
        <tr><td><b>Ctrl+Q</b></td><td>Exit Application</td></tr>
        </table>

        <h3>View Menu</h3>
        <table>
        <tr><td><b>Ctrl+1</b></td><td>Switch to Dashboard</td></tr>
        <tr><td><b>Ctrl+2</b></td><td>Switch to Transactions</td></tr>
        <tr><td><b>Ctrl+3</b></td><td>Switch to Reports</td></tr>
        <tr><td><b>F5</b></td><td>Refresh Current View</td></tr>
        </table>

        <h3>Transactions View</h3>
        <table>
        <tr><td><b>Ctrl+F</b></td><td>Focus Search Box</td></tr>
        <tr><td><b>Ctrl+N</b></td><td>Add New Transaction</td></tr>
        <tr><td><b>Delete</b></td><td>Delete Selected Transaction</td></tr>
        </table>

        <h3>Reports View</h3>
        <table>
        <tr><td><b>Ctrl+G</b></td><td>Generate Report</td></tr>
        <tr><td><b>Ctrl+E</b></td><td>Export Report</td></tr>
        </table>

        <h3>Dialogs</h3>
        <table>
        <tr><td><b>Ctrl+S</b></td><td>Save/Accept</td></tr>
        <tr><td><b>Esc</b></td><td>Cancel/Close</td></tr>
        </table>

        <h3>Help Menu</h3>
        <table>
        <tr><td><b>F1</b></td><td>User Guide</td></tr>
        <tr><td><b>Ctrl+/</b></td><td>Keyboard Shortcuts</td></tr>
        </table>
        """

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Keyboard Shortcuts")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(shortcuts_text)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
        self.logger.info("Keyboard shortcuts dialog displayed")
