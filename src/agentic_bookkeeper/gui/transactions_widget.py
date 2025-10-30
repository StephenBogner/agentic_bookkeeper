"""Transactions widget for viewing and managing transactions.

Package Name: agentic_bookkeeper
File Name: transactions_widget.py
Author: Stephen Bogner, P.Eng.
LLM: claude-sonnet-4-5-20250929
Ownership: Stephen Bogner - All Rights Reserved.  See LICENSE
Date Created: 2025-10-28
"""

import logging
import os
from datetime import datetime, date, timedelta
from typing import Optional, List

from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QLabel,
    QPushButton,
    QMessageBox,
    QDialog,
)

from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.models.transaction import Transaction
from agentic_bookkeeper.models.database import Database
from agentic_bookkeeper.utils.config import Config


class TransactionsWidget(QWidget):
    """
    Widget for displaying and managing transactions.

    Provides a table view with sorting, filtering, and search capabilities.
    """

    # Signals
    transaction_selected = Signal(int)  # Emits transaction ID
    refresh_requested = Signal()

    def __init__(
        self,
        database: Optional[Database] = None,
        transaction_manager: Optional[TransactionManager] = None,
        config: Optional[Config] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Initialize the transactions widget.

        Args:
            database: Optional Database instance for dependency injection
            transaction_manager: Optional TransactionManager instance
            config: Optional Config instance for dependency injection
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing TransactionsWidget")

        # Backend services
        self.database = database
        self.transaction_manager = transaction_manager
        self.config = config if config else Config()

        # Data
        self._transactions: List[Transaction] = []
        self._filtered_transactions: List[Transaction] = []

        # Setup UI
        self._setup_ui()
        self._connect_signals()
        self._setup_shortcuts()

        # Load initial data
        if self.transaction_manager:
            self.load_transactions()

        self.logger.info("TransactionsWidget initialization complete")

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Filter controls
        filter_layout = self._create_filter_controls()
        layout.addLayout(filter_layout)

        # Transaction table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Date", "Type", "Category", "Vendor/Customer", "Amount", "Tax"]
        )

        # Table properties
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)

        # Column sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Category
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Vendor/Customer
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Amount
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Tax

        layout.addWidget(self.table)

        # Action buttons
        button_layout = self._create_action_buttons()
        layout.addLayout(button_layout)

    def _create_filter_controls(self) -> QHBoxLayout:
        """Create the filter control layout."""
        layout = QHBoxLayout()

        # Search box
        layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search transactions...")
        self.search_input.setToolTip(
            "Search transactions by description, vendor/customer name, or category. "
            "Search is applied automatically as you type."
        )
        layout.addWidget(self.search_input)

        # Type filter
        layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "Income", "Expense"])
        self.type_filter.setToolTip("Filter transactions by type (income or expense).")
        layout.addWidget(self.type_filter)

        # Category filter
        layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.setToolTip(
            "Filter transactions by category. Categories are determined by your tax jurisdiction."
        )
        layout.addWidget(self.category_filter)

        # Date range filters
        layout.addWidget(QLabel("From:"))
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-3))
        self.date_from.setToolTip(
            "Start date for filtering transactions. Click to open calendar picker."
        )
        layout.addWidget(self.date_from)

        layout.addWidget(QLabel("To:"))
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setToolTip(
            "End date for filtering transactions. Click to open calendar picker."
        )
        layout.addWidget(self.date_to)

        # Filter button
        self.filter_button = QPushButton("Apply Filters")
        self.filter_button.setToolTip(
            "Apply the selected filters to the transaction list. "
            "Search filter is applied automatically."
        )
        layout.addWidget(self.filter_button)

        # Clear filters button
        self.clear_filters_button = QPushButton("Clear")
        self.clear_filters_button.setToolTip("Reset all filters to their default values.")
        layout.addWidget(self.clear_filters_button)

        layout.addStretch()

        return layout

    def _create_action_buttons(self) -> QHBoxLayout:
        """Create action button layout."""
        layout = QHBoxLayout()

        self.add_button = QPushButton("Add Transaction")
        self.add_button.setToolTip(
            "Add a new transaction manually. Opens a dialog to enter transaction details. "
            "Keyboard shortcut: Ctrl+N"
        )
        layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Edit Transaction")
        self.edit_button.setEnabled(False)  # Disabled until selection
        self.edit_button.setToolTip(
            "Edit the selected transaction. Select a transaction from the table first."
        )
        layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete Transaction")
        self.delete_button.setEnabled(False)  # Disabled until selection
        self.delete_button.setToolTip(
            "Delete the selected transaction. Select a transaction from the table first. "
            "Keyboard shortcut: Delete"
        )
        layout.addWidget(self.delete_button)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setToolTip(
            "Reload all transactions from the database to display the latest data."
        )
        layout.addWidget(self.refresh_button)

        layout.addStretch()

        # Transaction count label
        self.count_label = QLabel("Transactions: 0")
        layout.addWidget(self.count_label)

        return layout

    def _connect_signals(self) -> None:
        """Connect widget signals to slots."""
        self.filter_button.clicked.connect(self.apply_filters)
        self.clear_filters_button.clicked.connect(self.clear_filters)
        self.refresh_button.clicked.connect(self.load_transactions)
        self.search_input.textChanged.connect(self._on_search_changed)
        self.table.itemDoubleClicked.connect(self._on_row_double_clicked)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.add_button.clicked.connect(self._on_add_clicked)
        self.edit_button.clicked.connect(self._on_edit_clicked)
        self.delete_button.clicked.connect(self._on_delete_clicked)

    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        # Ctrl+F: Focus search box
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(lambda: self.search_input.setFocus())

        # Ctrl+N: Add new transaction
        add_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        add_shortcut.activated.connect(self._on_add_clicked)

        # Delete: Delete selected transaction
        delete_shortcut = QShortcut(QKeySequence.StandardKey.Delete, self)
        delete_shortcut.activated.connect(self._on_delete_clicked)

    def set_backend_services(
        self, database: Database, transaction_manager: TransactionManager
    ) -> None:
        """
        Set backend services for the widget.

        Args:
            database: Database instance
            transaction_manager: TransactionManager instance
        """
        self.database = database
        self.transaction_manager = transaction_manager
        self.load_transactions()

    def load_transactions(self) -> None:
        """Load all transactions from the database."""
        if not self.transaction_manager:
            self.logger.warning("No transaction manager available")
            return

        try:
            self.logger.info("Loading transactions")
            self._transactions = self.transaction_manager.get_all_transactions()
            self._update_category_filter()
            self.apply_filters()
            self.logger.info(f"Loaded {len(self._transactions)} transactions")

        except Exception as e:
            self.logger.error(f"Failed to load transactions: {e}", exc_info=True)
            self._show_error("Failed to load transactions", str(e))

    def apply_filters(self) -> None:
        """Apply current filters to the transaction list."""
        if not self._transactions:
            self._filtered_transactions = []
            self._update_table()
            return

        filtered = self._transactions.copy()

        # Type filter
        type_filter = self.type_filter.currentText()
        if type_filter != "All":
            filtered = [t for t in filtered if t.type.lower() == type_filter.lower()]

        # Category filter
        category_filter = self.category_filter.currentText()
        if category_filter != "All Categories":
            filtered = [t for t in filtered if t.category == category_filter]

        # Date range filter
        date_from = self.date_from.date().toPython()
        date_to = self.date_to.date().toPython()
        filtered = [
            t
            for t in filtered
            if date_from <= datetime.strptime(t.date, "%Y-%m-%d").date() <= date_to
        ]

        # Search filter
        search_term = self.search_input.text().lower()
        if search_term:
            filtered = [
                t
                for t in filtered
                if (search_term in t.description.lower() if t.description else False)
                or (search_term in t.vendor_customer.lower() if t.vendor_customer else False)
                or (search_term in t.category.lower())
            ]

        self._filtered_transactions = filtered
        self._update_table()

    def clear_filters(self) -> None:
        """Clear all filters and reset to defaults."""
        self.search_input.clear()
        self.type_filter.setCurrentIndex(0)
        self.category_filter.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addMonths(-3))
        self.date_to.setDate(QDate.currentDate())
        self.apply_filters()

    def _update_table(self) -> None:
        """Update the table with filtered transactions."""
        # Disable sorting while updating
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        for transaction in self._filtered_transactions:
            self._add_transaction_row(transaction)

        # Update count label
        total = len(self._transactions)
        filtered = len(self._filtered_transactions)
        self.count_label.setText(f"Transactions: {filtered} of {total}")

        # Re-enable sorting
        self.table.setSortingEnabled(True)

    def _add_transaction_row(self, transaction: Transaction) -> None:
        """
        Add a transaction row to the table.

        Args:
            transaction: Transaction to add
        """
        row = self.table.rowCount()
        self.table.insertRow(row)

        # ID (hidden column, used for selection)
        id_item = QTableWidgetItem(str(transaction.id))
        self.table.setItem(row, 0, id_item)

        # Date
        date_item = QTableWidgetItem(transaction.date)
        self.table.setItem(row, 1, date_item)

        # Type (with color coding)
        type_item = QTableWidgetItem(transaction.type.capitalize())
        if transaction.type == "income":
            type_item.setForeground(QColor(0, 128, 0))  # Green
        else:
            type_item.setForeground(QColor(255, 0, 0))  # Red
        self.table.setItem(row, 2, type_item)

        # Category
        category_item = QTableWidgetItem(transaction.category)
        self.table.setItem(row, 3, category_item)

        # Vendor/Customer
        vendor_item = QTableWidgetItem(transaction.vendor_customer or "")
        self.table.setItem(row, 4, vendor_item)

        # Amount (right-aligned)
        amount_item = QTableWidgetItem(f"${transaction.amount:,.2f}")
        amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 5, amount_item)

        # Tax (right-aligned)
        tax_item = QTableWidgetItem(f"${transaction.tax_amount:,.2f}")
        tax_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 6, tax_item)

    def _update_category_filter(self) -> None:
        """Update the category filter dropdown with unique categories."""
        if not self._transactions:
            return

        # Get unique categories
        categories = sorted(set(t.category for t in self._transactions))

        # Update combo box
        current_text = self.category_filter.currentText()
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        self.category_filter.addItems(categories)

        # Restore previous selection if possible
        index = self.category_filter.findText(current_text)
        if index >= 0:
            self.category_filter.setCurrentIndex(index)

    def _on_search_changed(self, text: str) -> None:
        """
        Handle search text changes.

        Args:
            text: New search text
        """
        # Apply filters automatically when search changes
        self.apply_filters()

    def _on_row_double_clicked(self, item: QTableWidgetItem) -> None:
        """
        Handle row double-click event.

        Args:
            item: Clicked table item
        """
        row = item.row()
        transaction_id = int(self.table.item(row, 0).text())
        self.transaction_selected.emit(transaction_id)

    def get_selected_transaction_id(self) -> Optional[int]:
        """
        Get the ID of the currently selected transaction.

        Returns:
            Transaction ID if selected, None otherwise
        """
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None

        row = selected_items[0].row()
        return int(self.table.item(row, 0).text())

    def _show_error(self, title: str, message: str) -> None:
        """
        Show an error dialog.

        Args:
            title: Error dialog title
            message: Error message
        """
        # Check if running in test mode
        if os.environ.get("PYTEST_CURRENT_TEST"):
            self.logger.warning(f"Test mode: Skipping error dialog - {title}: {message}")
            return

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def _on_selection_changed(self) -> None:
        """Handle table selection change - enable/disable edit and delete buttons."""
        has_selection = len(self.table.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _on_edit_clicked(self) -> None:
        """Handle edit button click."""
        transaction_id = self.get_selected_transaction_id()
        if transaction_id is None:
            return

        # Find the transaction
        transaction = None
        for t in self._filtered_transactions:
            if t.id == transaction_id:
                transaction = t
                break

        if transaction is None:
            self.logger.error(f"Transaction {transaction_id} not found")
            self._show_error(
                "Transaction Not Found", f"Could not find transaction #{transaction_id}"
            )
            return

        # Open edit dialog
        self._open_edit_dialog(transaction)

    def _open_edit_dialog(self, transaction: Transaction) -> None:
        """
        Open the edit dialog for a transaction.

        Args:
            transaction: The transaction to edit
        """
        # Lazy import to avoid circular dependency
        from agentic_bookkeeper.gui.transaction_edit_dialog import TransactionEditDialog

        dialog = TransactionEditDialog(
            transaction=transaction,
            config=self.config,
            transaction_manager=self.transaction_manager,
            parent=self,
        )

        if dialog.exec() == QDialog.Accepted:
            self.logger.info(f"Transaction {transaction.id} edited successfully")
            # Reload transactions to reflect changes
            self.load_transactions()

    def _on_add_clicked(self) -> None:
        """Handle add button click."""
        self._open_add_dialog()

    def _open_add_dialog(self) -> None:
        """Open the add dialog for creating a new transaction."""
        # Lazy import to avoid circular dependency
        from agentic_bookkeeper.gui.transaction_add_dialog import TransactionAddDialog

        dialog = TransactionAddDialog(
            config=self.config, transaction_manager=self.transaction_manager, parent=self
        )

        if dialog.exec() == QDialog.Accepted:
            transaction = dialog.get_transaction()
            if transaction:
                self.logger.info(f"Transaction {transaction.id} created successfully")
                # Reload transactions to reflect changes
                self.load_transactions()

    def _on_delete_clicked(self) -> None:
        """Handle delete button click."""
        transaction_id = self.get_selected_transaction_id()
        if transaction_id is None:
            return

        # Find the transaction
        transaction = None
        for t in self._filtered_transactions:
            if t.id == transaction_id:
                transaction = t
                break

        if transaction is None:
            self.logger.error(f"Transaction {transaction_id} not found")
            self._show_error(
                "Transaction Not Found", f"Could not find transaction #{transaction_id}"
            )
            return

        # Show confirmation dialog
        if self._confirm_delete(transaction):
            self._delete_transaction(transaction_id)

    def _confirm_delete(self, transaction: Transaction) -> bool:
        """
        Show confirmation dialog for deleting a transaction.

        Args:
            transaction: The transaction to delete

        Returns:
            True if user confirms deletion, False otherwise
        """
        # Check if running in test mode
        if os.environ.get("PYTEST_CURRENT_TEST"):
            self.logger.info(f"Test mode: Auto-confirming delete for transaction {transaction.id}")
            return True

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirm Delete")
        msg_box.setText(f"Are you sure you want to delete this transaction?")
        msg_box.setInformativeText(
            f"ID: {transaction.id}\n"
            f"Date: {transaction.date}\n"
            f"Type: {transaction.type.capitalize()}\n"
            f"Category: {transaction.category}\n"
            f"Amount: ${transaction.amount:,.2f}\n\n"
            f"This action cannot be undone."
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        result = msg_box.exec()
        return result == QMessageBox.Yes

    def _delete_transaction(self, transaction_id: int) -> None:
        """
        Delete a transaction from the database.

        Args:
            transaction_id: The ID of the transaction to delete
        """
        if not self.transaction_manager:
            self.logger.error("No transaction manager available")
            self._show_error("Error", "Transaction manager is not available")
            return

        try:
            self.logger.info(f"Deleting transaction {transaction_id}")
            self.transaction_manager.delete_transaction(transaction_id)
            self.logger.info(f"Transaction {transaction_id} deleted successfully")

            # Reload transactions to reflect changes
            self.load_transactions()

        except Exception as e:
            self.logger.error(f"Failed to delete transaction {transaction_id}: {e}", exc_info=True)
            self._show_error("Delete Failed", f"Failed to delete transaction: {str(e)}")
