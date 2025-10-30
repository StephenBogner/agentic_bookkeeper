"""
Unit tests for TransactionsWidget.

Tests transaction display, filtering, sorting, and backend integration.
"""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QTableWidgetItem, QMessageBox

from agentic_bookkeeper.gui.transactions_widget import TransactionsWidget
from agentic_bookkeeper.models.transaction import Transaction
from agentic_bookkeeper.models.database import Database
from agentic_bookkeeper.core.transaction_manager import TransactionManager


class TestTransactionsWidgetInitialization:
    """Test transactions widget initialization."""

    def test_widget_creation(self, qtbot):
        """Test that widget can be created."""
        widget = TransactionsWidget()
        qtbot.addWidget(widget)
        assert widget is not None

    def test_widget_with_backend(self, qtbot, mock_database, mock_transaction_manager):
        """Test widget creation with backend services."""
        widget = TransactionsWidget(
            database=mock_database, transaction_manager=mock_transaction_manager
        )
        qtbot.addWidget(widget)

        assert widget.database == mock_database
        assert widget.transaction_manager == mock_transaction_manager

    def test_table_setup(self, qtbot):
        """Test that table is set up correctly."""
        widget = TransactionsWidget()
        qtbot.addWidget(widget)

        assert widget.table.columnCount() == 7
        assert widget.table.horizontalHeaderItem(0).text() == "ID"
        assert widget.table.horizontalHeaderItem(1).text() == "Date"
        assert widget.table.horizontalHeaderItem(2).text() == "Type"
        assert widget.table.horizontalHeaderItem(3).text() == "Category"
        assert widget.table.horizontalHeaderItem(4).text() == "Vendor/Customer"
        assert widget.table.horizontalHeaderItem(5).text() == "Amount"
        assert widget.table.horizontalHeaderItem(6).text() == "Tax"

    def test_filter_controls_exist(self, qtbot):
        """Test that filter controls are created."""
        widget = TransactionsWidget()
        qtbot.addWidget(widget)

        assert widget.search_input is not None
        assert widget.type_filter is not None
        assert widget.category_filter is not None
        assert widget.date_from is not None
        assert widget.date_to is not None
        assert widget.filter_button is not None
        assert widget.clear_filters_button is not None


class TestLoadTransactions:
    """Test loading transactions."""

    def test_load_transactions_success(self, qtbot, mock_transaction_manager, sample_transactions):
        """Test successful transaction loading."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        assert len(widget._transactions) == len(sample_transactions)
        assert widget.table.rowCount() == len(sample_transactions)

    def test_load_transactions_no_manager(self, qtbot):
        """Test loading transactions without transaction manager."""
        widget = TransactionsWidget()
        qtbot.addWidget(widget)

        widget.load_transactions()
        assert len(widget._transactions) == 0

    def test_load_transactions_error(self, qtbot, mock_transaction_manager):
        """Test error handling when loading transactions fails."""
        mock_transaction_manager.get_all_transactions.side_effect = Exception("Database error")

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        with patch.object(QMessageBox, "exec"):
            widget.load_transactions()

        assert len(widget._transactions) == 0

    def test_category_filter_updated(self, qtbot, mock_transaction_manager, sample_transactions):
        """Test that category filter is updated after loading."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Should have "All Categories" plus unique categories
        assert widget.category_filter.count() > 1


class TestFiltering:
    """Test filtering functionality."""

    def test_type_filter_income(self, qtbot, mock_transaction_manager, sample_transactions):
        """Test filtering by income type."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        widget.type_filter.setCurrentText("Income")
        widget.apply_filters()

        income_count = sum(1 for t in sample_transactions if t.type == "income")
        assert widget.table.rowCount() == income_count

    def test_type_filter_expense(self, qtbot, mock_transaction_manager, sample_transactions):
        """Test filtering by expense type."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        widget.type_filter.setCurrentText("Expense")
        widget.apply_filters()

        expense_count = sum(1 for t in sample_transactions if t.type == "expense")
        assert widget.table.rowCount() == expense_count

    def test_category_filter(self, qtbot, mock_transaction_manager, sample_transactions):
        """Test filtering by category."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Get first category
        category = sample_transactions[0].category
        widget.category_filter.setCurrentText(category)
        widget.apply_filters()

        category_count = sum(1 for t in sample_transactions if t.category == category)
        assert widget.table.rowCount() == category_count

    def test_date_range_filter(self, qtbot, mock_transaction_manager, sample_transactions):
        """Test filtering by date range."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Set date range to last 30 days
        today = date.today()
        widget.date_from.setDate(QDate(today.year, today.month, 1))
        widget.date_to.setDate(QDate(today.year, today.month, today.day))
        widget.apply_filters()

        # Count transactions in range
        filtered_count = len(widget._filtered_transactions)
        assert widget.table.rowCount() == filtered_count

    def test_search_filter(self, qtbot, mock_transaction_manager, sample_transactions):
        """Test search filtering."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Search for a term that should match
        widget.search_input.setText("consulting")
        # Search automatically triggers filter

        # Should have filtered results
        assert widget.table.rowCount() <= len(sample_transactions)

    def test_clear_filters(self, qtbot, mock_transaction_manager, sample_transactions):
        """Test clearing all filters."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Apply some filters
        widget.type_filter.setCurrentText("Income")
        widget.search_input.setText("test")
        widget.apply_filters()

        # Clear filters
        widget.clear_filters()

        assert widget.type_filter.currentText() == "All"
        assert widget.search_input.text() == ""
        assert widget.table.rowCount() == len(sample_transactions)


class TestTableDisplay:
    """Test table display functionality."""

    def test_transaction_row_display(self, qtbot, mock_transaction_manager, sample_transactions):
        """Test that transaction rows are displayed correctly."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Check first row
        transaction = sample_transactions[0]
        assert widget.table.item(0, 1).text() == transaction.date
        assert widget.table.item(0, 2).text() == transaction.type.capitalize()
        assert widget.table.item(0, 3).text() == transaction.category

    def test_income_color_coding(self, qtbot, mock_transaction_manager):
        """Test that income transactions are colored green."""
        income_transaction = Transaction(
            date="2025-10-28",
            type="income",
            category="Consulting",
            vendor_customer="Client A",
            amount=1000.0,
            tax_amount=150.0,
        )
        income_transaction.id = 1

        mock_transaction_manager.get_all_transactions.return_value = [income_transaction]

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        type_item = widget.table.item(0, 2)
        assert type_item.foreground().color().green() > 0

    def test_expense_color_coding(self, qtbot, mock_transaction_manager):
        """Test that expense transactions are colored red."""
        expense_transaction = Transaction(
            date="2025-10-28",
            type="expense",
            category="Office Supplies",
            vendor_customer="Vendor B",
            amount=500.0,
            tax_amount=75.0,
        )
        expense_transaction.id = 1

        mock_transaction_manager.get_all_transactions.return_value = [expense_transaction]

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        type_item = widget.table.item(0, 2)
        assert type_item.foreground().color().red() > 0

    def test_amount_formatting(self, qtbot, mock_transaction_manager, sample_transactions):
        """Test that amounts are formatted correctly."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Check amount formatting (should have $ and commas)
        amount_text = widget.table.item(0, 5).text()
        assert amount_text.startswith("$")
        assert "," in amount_text or len(amount_text) < 8  # Small amounts may not have commas

    def test_count_label_update(self, qtbot, mock_transaction_manager, sample_transactions):
        """Test that count label updates correctly."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        expected_text = f"Transactions: {len(sample_transactions)} of {len(sample_transactions)}"
        assert widget.count_label.text() == expected_text


class TestSignals:
    """Test widget signals."""

    def test_transaction_selected_signal(
        self, qtbot, mock_transaction_manager, sample_transactions
    ):
        """Test that double-click emits transaction_selected signal."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Connect signal to spy
        with qtbot.waitSignal(widget.transaction_selected, timeout=1000):
            # Simulate double-click on first row
            item = widget.table.item(0, 0)
            widget._on_row_double_clicked(item)

    def test_get_selected_transaction_id(
        self, qtbot, mock_transaction_manager, sample_transactions
    ):
        """Test getting selected transaction ID."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Select first row
        widget.table.selectRow(0)

        transaction_id = widget.get_selected_transaction_id()
        assert transaction_id == sample_transactions[0].id

    def test_get_selected_transaction_id_none(self, qtbot):
        """Test getting selected transaction ID when nothing selected."""
        widget = TransactionsWidget()
        qtbot.addWidget(widget)

        transaction_id = widget.get_selected_transaction_id()
        assert transaction_id is None


class TestBackendIntegration:
    """Test backend service integration."""

    def test_set_backend_services(
        self, qtbot, mock_database, mock_transaction_manager, sample_transactions
    ):
        """Test setting backend services."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget()
        qtbot.addWidget(widget)

        widget.set_backend_services(mock_database, mock_transaction_manager)

        assert widget.database == mock_database
        assert widget.transaction_manager == mock_transaction_manager
        assert len(widget._transactions) == len(sample_transactions)

    def test_refresh_button(self, qtbot, mock_transaction_manager, sample_transactions):
        """Test refresh button reloads transactions."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Click refresh
        widget.refresh_button.click()

        # Should call get_all_transactions again
        assert (
            mock_transaction_manager.get_all_transactions.call_count == 2
        )  # Once on init, once on refresh


# Pytest fixtures
@pytest.fixture
def mock_database():
    """Create a mock Database instance."""
    database = Mock(spec=Database)
    return database


@pytest.fixture
def mock_transaction_manager():
    """Create a mock TransactionManager instance."""
    manager = Mock(spec=TransactionManager)
    manager.get_all_transactions.return_value = []
    return manager


@pytest.fixture
def sample_transactions():
    """Create sample transactions for testing."""
    transactions = []

    # Create income transaction
    income = Transaction(
        date="2025-10-28",
        type="income",
        category="Consulting",
        vendor_customer="Client A",
        description="Web development consulting",
        amount=5000.0,
        tax_amount=750.0,
    )
    income.id = 1
    transactions.append(income)

    # Create expense transaction
    expense = Transaction(
        date="2025-10-27",
        type="expense",
        category="Office Supplies",
        vendor_customer="Vendor B",
        description="Office supplies purchase",
        amount=250.0,
        tax_amount=37.50,
    )
    expense.id = 2
    transactions.append(expense)

    # Create another income
    income2 = Transaction(
        date="2025-10-26",
        type="income",
        category="Services",
        vendor_customer="Client C",
        description="Design services",
        amount=3000.0,
        tax_amount=450.0,
    )
    income2.id = 3
    transactions.append(income2)

    return transactions


class TestDeleteFunctionality:
    """Test transaction delete functionality."""

    def test_delete_button_exists(self, qtbot):
        """Test that delete button is created."""
        widget = TransactionsWidget()
        qtbot.addWidget(widget)

        assert widget.delete_button is not None
        assert not widget.delete_button.isEnabled()  # Disabled by default

    def test_delete_button_enabled_on_selection(
        self, qtbot, mock_transaction_manager, sample_transactions
    ):
        """Test that delete button is enabled when transaction is selected."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Initially disabled
        assert not widget.delete_button.isEnabled()

        # Select a row
        widget.table.selectRow(0)

        # Should be enabled now
        assert widget.delete_button.isEnabled()

    def test_delete_button_disabled_on_deselection(
        self, qtbot, mock_transaction_manager, sample_transactions
    ):
        """Test that delete button is disabled when selection is cleared."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Select and then deselect
        widget.table.selectRow(0)
        assert widget.delete_button.isEnabled()

        widget.table.clearSelection()
        assert not widget.delete_button.isEnabled()

    def test_delete_transaction_success(self, qtbot, mock_transaction_manager, sample_transactions):
        """Test successful transaction deletion."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions
        mock_transaction_manager.delete_transaction.return_value = None

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Select first transaction
        widget.table.selectRow(0)
        transaction_id = int(widget.table.item(0, 0).text())

        # Click delete button (confirmation auto-accepted in test mode)
        initial_count = len(widget._transactions)
        widget._on_delete_clicked()

        # Verify delete was called
        mock_transaction_manager.delete_transaction.assert_called_once_with(transaction_id)

    def test_delete_transaction_no_selection(
        self, qtbot, mock_transaction_manager, sample_transactions
    ):
        """Test delete with no selection does nothing."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # No selection, click delete
        widget._on_delete_clicked()

        # Delete should not be called
        mock_transaction_manager.delete_transaction.assert_not_called()

    def test_delete_transaction_not_found(
        self, qtbot, mock_transaction_manager, sample_transactions
    ):
        """Test delete when transaction is not found in filtered list."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Manually clear filtered transactions to simulate not found
        widget._filtered_transactions = []

        # Select a row (will have stale data)
        widget.table.selectRow(0)

        # Try to delete
        widget._on_delete_clicked()

        # Delete should not be called
        mock_transaction_manager.delete_transaction.assert_not_called()

    def test_delete_transaction_error(self, qtbot, mock_transaction_manager, sample_transactions):
        """Test error handling when deletion fails."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions
        mock_transaction_manager.delete_transaction.side_effect = Exception("Database error")

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Select first transaction
        widget.table.selectRow(0)

        # Try to delete (should show error dialog)
        with patch.object(QMessageBox, "exec"):
            widget._on_delete_clicked()

        # Delete was attempted
        assert mock_transaction_manager.delete_transaction.called

    def test_delete_transaction_no_manager(self, qtbot):
        """Test delete when no transaction manager is available."""
        widget = TransactionsWidget()
        qtbot.addWidget(widget)

        # Manually add a transaction to the filtered list
        transaction = Transaction(
            date="2025-10-28",
            type="expense",
            category="Office Supplies",
            vendor_customer="Test Vendor",
            amount=100.0,
            tax_amount=10.0,
        )
        transaction.id = 1
        widget._filtered_transactions = [transaction]

        # Add to table manually
        widget._add_transaction_row(transaction)

        # Select the row
        widget.table.selectRow(0)

        # Try to delete (should show error)
        with patch.object(QMessageBox, "exec"):
            widget._on_delete_clicked()

    def test_confirm_delete_dialog_in_test_mode(
        self, qtbot, mock_transaction_manager, sample_transactions
    ):
        """Test that confirmation dialog auto-accepts in test mode."""
        import os

        os.environ["PYTEST_CURRENT_TEST"] = "test"

        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        transaction = sample_transactions[0]

        # Should return True in test mode
        result = widget._confirm_delete(transaction)
        assert result is True

    def test_delete_updates_ui(self, qtbot, mock_transaction_manager, sample_transactions):
        """Test that UI is updated after deletion."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        initial_count = widget.table.rowCount()

        # Select and delete first transaction
        widget.table.selectRow(0)
        transaction_id = int(widget.table.item(0, 0).text())

        # Set up mock to return fewer transactions after delete
        remaining_transactions = [t for t in sample_transactions if t.id != transaction_id]
        mock_transaction_manager.get_all_transactions.return_value = remaining_transactions

        # Delete
        widget._on_delete_clicked()

        # Verify load_transactions was called (which updates UI)
        assert (
            mock_transaction_manager.get_all_transactions.call_count >= 2
        )  # Initial + after delete

    def test_delete_button_click_signal_connected(
        self, qtbot, mock_transaction_manager, sample_transactions
    ):
        """Test that delete button click signal is properly connected."""
        mock_transaction_manager.get_all_transactions.return_value = sample_transactions

        widget = TransactionsWidget(transaction_manager=mock_transaction_manager)
        qtbot.addWidget(widget)

        # Select a transaction to enable the button
        widget.table.selectRow(0)

        # Verify the signal is connected by checking delete is called
        initial_delete_count = mock_transaction_manager.delete_transaction.call_count
        widget.delete_button.click()

        # After clicking, delete_transaction should have been called
        assert mock_transaction_manager.delete_transaction.call_count == initial_delete_count + 1
