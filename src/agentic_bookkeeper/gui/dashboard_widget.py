"""Dashboard widget for the Agentic Bookkeeper GUI application.

Package Name: agentic_bookkeeper
File Name: dashboard_widget.py
Author: Stephen Bogner, P.Eng.
LLM: claude-sonnet-4-5-20250929
Ownership: Stephen Bogner - All Rights Reserved.  See LICENSE
Date Created: 2025-10-27
"""

import logging
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QMessageBox,
)
from PySide6.QtGui import QColor

from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.core.document_monitor import DocumentMonitor
from agentic_bookkeeper.core.document_processor import DocumentProcessor
from agentic_bookkeeper.models.database import Database
from agentic_bookkeeper.utils.config import Config
from agentic_bookkeeper.llm.openai_provider import OpenAIProvider
from agentic_bookkeeper.llm.anthropic_provider import AnthropicProvider
from agentic_bookkeeper.llm.xai_provider import XAIProvider
from agentic_bookkeeper.llm.google_provider import GoogleProvider


class DashboardWidget(QWidget):
    """
    Dashboard widget displaying system status, recent transactions, and statistics.

    Provides real-time monitoring of document processing, transaction statistics,
    and quick actions for starting/stopping the document monitor.
    """

    # Signals
    status_changed = Signal(str)  # Emitted when monitoring status changes
    refresh_requested = Signal()  # Emitted when refresh is requested

    def __init__(
        self,
        database: Optional[Database] = None,
        transaction_manager: Optional[TransactionManager] = None,
        document_monitor: Optional[DocumentMonitor] = None,
        config: Optional[Config] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Initialize the dashboard widget.

        Args:
            database: Database instance for querying data
            transaction_manager: Transaction manager for operations
            document_monitor: Document monitor for watching directories
            config: Configuration instance
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing DashboardWidget")

        # Backend services
        self.database = database
        self.transaction_manager = transaction_manager
        self.document_monitor = document_monitor
        self.config = config if config else Config()

        # Monitoring state
        self._is_monitoring = False

        # Auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._auto_refresh)
        self.refresh_timer.setInterval(5000)  # Refresh every 5 seconds

        self._setup_ui()
        self._connect_signals()
        self._load_initial_data()

        self.logger.info("DashboardWidget initialization complete")

    def _setup_ui(self) -> None:
        """Set up the user interface layout."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Top section: Status and controls
        main_layout.addWidget(self._create_status_section())

        # Middle section: Statistics panel
        main_layout.addWidget(self._create_statistics_section())

        # Bottom section: Recent transactions table
        main_layout.addWidget(self._create_transactions_section())

        # Bottom controls
        main_layout.addWidget(self._create_control_buttons())

        self.setLayout(main_layout)
        self.logger.info("Dashboard UI layout created")

    def _create_status_section(self) -> QGroupBox:
        """
        Create the monitoring status section.

        Returns:
            QGroupBox containing status indicator
        """
        group_box = QGroupBox("Monitoring Status")
        layout = QHBoxLayout()

        # Status indicator
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(20, 20)
        self.status_indicator.setStyleSheet(
            "background-color: #E74C3C; border-radius: 10px;"
        )  # Red = stopped

        # Status text
        self.status_label = QLabel("Monitoring: Stopped")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        # Start/Stop button
        self.toggle_monitoring_button = QPushButton("Start Monitoring")
        self.toggle_monitoring_button.setFixedWidth(150)
        self.toggle_monitoring_button.setToolTip(
            "Start or stop automatic document monitoring. When enabled, the system will "
            "automatically process new documents placed in the watch directory."
        )
        self.toggle_monitoring_button.clicked.connect(self._toggle_monitoring)

        layout.addWidget(self.status_indicator)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.toggle_monitoring_button)

        group_box.setLayout(layout)
        return group_box

    def _create_statistics_section(self) -> QGroupBox:
        """
        Create the statistics panel section.

        Returns:
            QGroupBox containing statistics
        """
        group_box = QGroupBox("Quick Statistics")
        layout = QHBoxLayout()

        # Total income
        income_frame = self._create_stat_frame("Total Income", "$0.00", "#27AE60")
        income_frame.setToolTip(
            "Total income from all income transactions in the database. "
            "This includes all revenue, sales, and other income sources."
        )
        self.income_label = income_frame.findChild(QLabel, "value_label")

        # Total expenses
        expense_frame = self._create_stat_frame("Total Expenses", "$0.00", "#E74C3C")
        expense_frame.setToolTip(
            "Total expenses from all expense transactions in the database. "
            "This includes all business costs, purchases, and expenditures."
        )
        self.expense_label = expense_frame.findChild(QLabel, "value_label")

        # Net income
        net_frame = self._create_stat_frame("Net Income", "$0.00", "#3498DB")
        net_frame.setToolTip(
            "Net income calculated as total income minus total expenses. "
            "A positive value indicates profit, while a negative value indicates loss."
        )
        self.net_label = net_frame.findChild(QLabel, "value_label")

        # Transaction count
        count_frame = self._create_stat_frame("Transactions", "0", "#9B59B6")
        count_frame.setToolTip(
            "Total number of transactions recorded in the database. "
            "This includes both income and expense transactions."
        )
        self.count_label = count_frame.findChild(QLabel, "value_label")

        layout.addWidget(income_frame)
        layout.addWidget(expense_frame)
        layout.addWidget(net_frame)
        layout.addWidget(count_frame)

        group_box.setLayout(layout)
        return group_box

    def _create_stat_frame(self, title: str, value: str, color: str) -> QFrame:
        """
        Create a statistics display frame.

        Args:
            title: Statistic title
            value: Initial value
            color: Color code for the frame

        Returns:
            QFrame containing the statistic
        """
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(f"QFrame {{ border: 2px solid {color}; border-radius: 5px; }}")

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #7F8C8D;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        frame.setLayout(layout)
        return frame

    def _create_transactions_section(self) -> QGroupBox:
        """
        Create the recent transactions table section.

        Returns:
            QGroupBox containing transactions table
        """
        group_box = QGroupBox("Recent Transactions (Last 10)")
        layout = QVBoxLayout()

        # Create table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(5)
        self.transactions_table.setHorizontalHeaderLabels(
            ["Date", "Type", "Category", "Description", "Amount"]
        )

        # Configure table
        self.transactions_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.transactions_table.setAlternatingRowColors(True)

        # Set column widths
        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.transactions_table)
        group_box.setLayout(layout)
        return group_box

    def _create_control_buttons(self) -> QWidget:
        """
        Create the control buttons section.

        Returns:
            QWidget containing control buttons
        """
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Refresh button
        self.refresh_button = QPushButton("Refresh Now")
        self.refresh_button.setFixedWidth(120)
        self.refresh_button.setToolTip(
            "Manually refresh dashboard data to display the latest statistics "
            "and recent transactions from the database."
        )
        self.refresh_button.clicked.connect(self._on_refresh_clicked)

        # Auto-refresh toggle
        self.auto_refresh_button = QPushButton("Enable Auto-Refresh")
        self.auto_refresh_button.setFixedWidth(150)
        self.auto_refresh_button.setCheckable(True)
        self.auto_refresh_button.setToolTip(
            "Enable or disable automatic refresh of dashboard data every 5 seconds. "
            "Useful for monitoring changes in real-time when processing documents."
        )
        self.auto_refresh_button.clicked.connect(self._toggle_auto_refresh)

        layout.addStretch()
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.auto_refresh_button)

        widget.setLayout(layout)
        return widget

    def _connect_signals(self) -> None:
        """Connect internal signals and slots."""
        self.status_changed.connect(self._update_status_display)
        self.refresh_requested.connect(self._load_data)

    def _load_initial_data(self) -> None:
        """Load initial data on startup."""
        self._load_data()

    def _load_data(self) -> None:
        """Load all dashboard data from backend services."""
        self.logger.debug("Loading dashboard data")
        self._load_statistics()
        self._load_recent_transactions()

    def _load_statistics(self) -> None:
        """Load and display statistics."""
        if not self.transaction_manager:
            self.logger.warning("Transaction manager not available")
            return

        try:
            stats = self.transaction_manager.get_transaction_statistics()

            # Update income
            total_income = stats.get("income", {}).get("total", 0.0)
            self.income_label.setText(f"${total_income:,.2f}")

            # Update expenses
            total_expenses = stats.get("expense", {}).get("total", 0.0)
            self.expense_label.setText(f"${total_expenses:,.2f}")

            # Update net income
            net_income = stats.get("net", 0.0)
            self.net_label.setText(f"${net_income:,.2f}")

            # Update transaction count (sum of income and expense counts)
            income_count = stats.get("income", {}).get("count", 0)
            expense_count = stats.get("expense", {}).get("count", 0)
            transaction_count = income_count + expense_count
            self.count_label.setText(str(transaction_count))

            self.logger.debug(f"Statistics loaded: {stats}")

        except Exception as e:
            self.logger.error(f"Error loading statistics: {e}", exc_info=True)

    def _load_recent_transactions(self) -> None:
        """Load and display recent transactions."""
        if not self.transaction_manager:
            self.logger.warning("Transaction manager not available")
            return

        try:
            # Get last 10 transactions
            transactions = self.transaction_manager.query_transactions(
                limit=10, order_by="date DESC"
            )

            # Clear existing rows
            self.transactions_table.setRowCount(0)

            # Add transactions to table
            for i, transaction in enumerate(transactions):
                self.transactions_table.insertRow(i)

                # Date
                date_item = QTableWidgetItem(transaction.date)
                self.transactions_table.setItem(i, 0, date_item)

                # Type
                type_item = QTableWidgetItem(transaction.type.capitalize())
                if transaction.type == "income":
                    type_item.setForeground(QColor("#27AE60"))
                else:
                    type_item.setForeground(QColor("#E74C3C"))
                self.transactions_table.setItem(i, 1, type_item)

                # Category
                category_item = QTableWidgetItem(transaction.category or "")
                self.transactions_table.setItem(i, 2, category_item)

                # Description
                description = transaction.description or transaction.vendor_customer or ""
                desc_item = QTableWidgetItem(description[:50])
                self.transactions_table.setItem(i, 3, desc_item)

                # Amount
                amount_item = QTableWidgetItem(f"${transaction.amount:,.2f}")
                amount_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )
                self.transactions_table.setItem(i, 4, amount_item)

            self.logger.debug(f"Loaded {len(transactions)} recent transactions")

        except Exception as e:
            self.logger.error(f"Error loading transactions: {e}", exc_info=True)

    def _toggle_monitoring(self) -> None:
        """Toggle document monitoring on/off."""
        if self._is_monitoring:
            self._stop_monitoring()
        else:
            self._start_monitoring()

    def _start_monitoring(self) -> None:
        """Start document monitoring."""
        # Initialize DocumentMonitor on demand if not already created
        if not self.document_monitor:
            self.logger.info("DocumentMonitor not initialized - attempting on-demand initialization")

            # Validate configuration
            validation_error = self._validate_monitoring_configuration()
            if validation_error:
                self.logger.warning(f"Cannot start monitoring: {validation_error}")
                self._show_configuration_error(validation_error)
                return

            # Initialize DocumentMonitor
            try:
                self.document_monitor = self._initialize_document_monitor()
                self.logger.info("DocumentMonitor initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize DocumentMonitor: {e}", exc_info=True)
                QMessageBox.critical(
                    self,
                    "Initialization Error",
                    f"Failed to initialize document monitoring:\n\n{str(e)}\n\n"
                    "Please check the log file for details."
                )
                return

        try:
            self.document_monitor.start()
            self._is_monitoring = True
            self.status_changed.emit("running")
            self.logger.info("Document monitoring started")

            # Process any existing files in the watch directory
            self.logger.info("Processing existing files in watch directory...")
            processed_files = self.document_monitor.process_existing_files()
            if processed_files:
                self.logger.info(f"Processed {len(processed_files)} existing file(s)")
            else:
                self.logger.info("No existing files to process")

        except Exception as e:
            self.logger.error(f"Error starting monitoring: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Monitoring Error",
                f"Failed to start document monitoring:\n\n{str(e)}"
            )

    def _stop_monitoring(self) -> None:
        """Stop document monitoring."""
        if not self.document_monitor:
            self.logger.warning("Document monitor not available")
            return

        try:
            self.document_monitor.stop()
            self._is_monitoring = False
            self.status_changed.emit("stopped")
            self.logger.info("Document monitoring stopped")
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {e}", exc_info=True)

    def _update_status_display(self, status: str) -> None:
        """
        Update the status display based on monitoring state.

        Args:
            status: Status string ('running' or 'stopped')
        """
        if status == "running":
            self.status_indicator.setStyleSheet(
                "background-color: #27AE60; border-radius: 10px;"
            )  # Green = running
            self.status_label.setText("Monitoring: Running")
            self.toggle_monitoring_button.setText("Stop Monitoring")
        else:
            self.status_indicator.setStyleSheet(
                "background-color: #E74C3C; border-radius: 10px;"
            )  # Red = stopped
            self.status_label.setText("Monitoring: Stopped")
            self.toggle_monitoring_button.setText("Start Monitoring")

    def _on_refresh_clicked(self) -> None:
        """Handle refresh button click."""
        self.logger.info("Manual refresh triggered")
        self.refresh_requested.emit()

    def _toggle_auto_refresh(self, checked: bool) -> None:
        """
        Toggle auto-refresh on/off.

        Args:
            checked: True if auto-refresh should be enabled
        """
        if checked:
            self.refresh_timer.start()
            self.auto_refresh_button.setText("Disable Auto-Refresh")
            self.logger.info("Auto-refresh enabled")
        else:
            self.refresh_timer.stop()
            self.auto_refresh_button.setText("Enable Auto-Refresh")
            self.logger.info("Auto-refresh disabled")

    def _auto_refresh(self) -> None:
        """Perform auto-refresh of dashboard data."""
        self.logger.debug("Auto-refresh triggered")
        self._load_data()

    def get_monitoring_status(self) -> bool:
        """
        Get current monitoring status.

        Returns:
            True if monitoring is active, False otherwise
        """
        return self._is_monitoring

    def _validate_monitoring_configuration(self) -> Optional[str]:
        """
        Validate that required configuration is present for monitoring.

        Returns:
            Error message if validation fails, None if configuration is valid
        """
        # Check if watch directory is configured
        watch_dir = self.config.get_watch_directory()
        if not watch_dir or not str(watch_dir).strip():
            return "Watch directory not configured"

        # Check if processed directory is configured
        processed_dir = self.config.get_processed_directory()
        if not processed_dir or not str(processed_dir).strip():
            return "Processed directory not configured"

        # Check if LLM provider is configured
        llm_provider = self.config.get("llm_provider")
        if not llm_provider:
            return "LLM provider not configured"

        # Check if API key is configured for the provider
        api_key = self.config.get_api_key(llm_provider)
        if not api_key:
            return f"API key not configured for {llm_provider}"

        return None  # Configuration is valid

    def _show_configuration_error(self, error_message: str) -> None:
        """
        Show user-friendly configuration error dialog.

        Args:
            error_message: Error message describing the missing configuration
        """
        QMessageBox.warning(
            self,
            "Configuration Required",
            f"{error_message}\n\n"
            "To enable document monitoring, please configure the following:\n\n"
            "1. Watch Directory - where new documents will be placed\n"
            "2. Processed Directory - where processed documents will be moved\n"
            "3. LLM Provider - select your AI provider (OpenAI, Anthropic, etc.)\n"
            "4. API Key - enter your API key for the selected provider\n\n"
            "Go to File → Settings to configure these options.",
        )

    def _initialize_document_monitor(self) -> DocumentMonitor:
        """
        Initialize DocumentMonitor with current configuration.

        Returns:
            Initialized DocumentMonitor instance

        Raises:
            Exception: If initialization fails
        """
        # Get directories from config
        watch_dir = str(self.config.get_watch_directory())
        processed_dir = str(self.config.get_processed_directory())

        # Create LLM provider
        llm_provider_name = self.config.get("llm_provider")
        api_key = self.config.get_api_key(llm_provider_name)

        # Create provider based on name
        if llm_provider_name == "openai":
            llm_provider = OpenAIProvider(api_key)
        elif llm_provider_name == "anthropic":
            llm_provider = AnthropicProvider(api_key)
        elif llm_provider_name == "xai":
            llm_provider = XAIProvider(api_key)
        elif llm_provider_name == "google":
            llm_provider = GoogleProvider(api_key)
        else:
            raise ValueError(f"Unknown LLM provider: {llm_provider_name}")

        # Get tax categories
        tax_categories = self.config.get_categories()

        # Create document processor
        document_processor = DocumentProcessor(llm_provider, tax_categories)

        # Create callback function that processes documents and saves to database
        def process_document_callback(document_path: str) -> None:
            """Process document and save transaction to database."""
            try:
                self.logger.info(f"Processing document: {document_path}")

                # Process document
                transaction = document_processor.process_document(document_path)

                if transaction and self.transaction_manager:
                    # Save transaction to database
                    self.transaction_manager.create_transaction(transaction)
                    self.logger.info(f"Transaction saved: {transaction.id}")

                    # Refresh dashboard
                    self.refresh_requested.emit()

            except Exception as e:
                self.logger.error(f"Error processing document {document_path}: {e}", exc_info=True)

        # Create and return DocumentMonitor
        return DocumentMonitor(
            watch_directory=watch_dir,
            processed_directory=processed_dir,
            on_document_callback=process_document_callback,
        )

    def set_backend_services(
        self,
        database: Optional[Database] = None,
        transaction_manager: Optional[TransactionManager] = None,
        document_monitor: Optional[DocumentMonitor] = None,
    ) -> None:
        """
        Set or update backend services.

        Args:
            database: Database instance
            transaction_manager: Transaction manager instance
            document_monitor: Document monitor instance
        """
        if database is not None:
            self.database = database
            self.logger.info("Database service updated")

        if transaction_manager is not None:
            self.transaction_manager = transaction_manager
            self.logger.info("Transaction manager service updated")

        if document_monitor is not None:
            self.document_monitor = document_monitor
            self.logger.info("Document monitor service updated")

        # Reload data with new services
        self._load_data()
