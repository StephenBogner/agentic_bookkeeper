"""
Package Name: agentic_bookkeeper
File Name: test_gui_dashboard.py
Description: Unit tests for the DashboardWidget GUI component
Author: Stephen Bogner, P.Eng.
LLM: claude-sonnet-4-5-20250929
Ownership: Stephen Bogner - All Rights Reserved.  See LICENSE
Date Created: 2025-10-27
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from agentic_bookkeeper.gui.dashboard_widget import DashboardWidget
from agentic_bookkeeper.models.transaction import Transaction


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_database():
    """Create mock Database instance."""
    database = MagicMock()
    return database


@pytest.fixture
def mock_transaction_manager():
    """Create mock TransactionManager instance."""
    manager = MagicMock()

    # Mock statistics
    manager.get_statistics.return_value = {
        "total_income": 15000.00,
        "total_expense": 8500.00,
        "count": 25,
    }

    # Mock query transactions
    transactions = [
        Transaction(
            date="2025-10-27",
            type="income",
            category="Consulting",
            vendor_customer="ABC Corp",
            description="Consulting services",
            amount=5000.00,
            tax_amount=650.00,
        ),
        Transaction(
            date="2025-10-26",
            type="expense",
            category="Office Supplies",
            vendor_customer="Office Depot",
            description="Office supplies",
            amount=250.00,
            tax_amount=32.50,
        ),
        Transaction(
            date="2025-10-25",
            type="income",
            category="Sales",
            vendor_customer="XYZ Inc",
            description="Product sales",
            amount=3500.00,
            tax_amount=455.00,
        ),
    ]
    manager.query_transactions.return_value = transactions

    return manager


@pytest.fixture
def mock_document_monitor():
    """Create mock DocumentMonitor instance."""
    monitor = MagicMock()
    monitor.start = MagicMock()
    monitor.stop = MagicMock()
    return monitor


@pytest.fixture
def dashboard_widget(qapp, qtbot, mock_database, mock_transaction_manager, mock_document_monitor):
    """Create DashboardWidget instance for testing."""
    widget = DashboardWidget(
        database=mock_database,
        transaction_manager=mock_transaction_manager,
        document_monitor=mock_document_monitor,
    )
    qtbot.addWidget(widget)
    return widget


def test_dashboard_initialization(dashboard_widget):
    """Test that the dashboard initializes correctly."""
    assert dashboard_widget is not None
    assert dashboard_widget.database is not None
    assert dashboard_widget.transaction_manager is not None
    assert dashboard_widget.document_monitor is not None
    assert dashboard_widget.get_monitoring_status() is False


def test_dashboard_layout_sections(dashboard_widget):
    """Test that all dashboard sections are present."""
    # Check for status section elements
    assert dashboard_widget.status_indicator is not None
    assert dashboard_widget.status_label is not None
    assert dashboard_widget.toggle_monitoring_button is not None

    # Check for statistics section elements
    assert dashboard_widget.income_label is not None
    assert dashboard_widget.expense_label is not None
    assert dashboard_widget.net_label is not None
    assert dashboard_widget.count_label is not None

    # Check for transactions table
    assert dashboard_widget.transactions_table is not None
    assert dashboard_widget.transactions_table.columnCount() == 5

    # Check for control buttons
    assert dashboard_widget.refresh_button is not None
    assert dashboard_widget.auto_refresh_button is not None


def test_statistics_display(dashboard_widget):
    """Test that statistics are displayed correctly."""
    # Statistics should be loaded on initialization
    assert dashboard_widget.income_label.text() == "$15,000.00"
    assert dashboard_widget.expense_label.text() == "$8,500.00"
    assert dashboard_widget.net_label.text() == "$6,500.00"
    assert dashboard_widget.count_label.text() == "25"


def test_recent_transactions_display(dashboard_widget):
    """Test that recent transactions are displayed correctly."""
    table = dashboard_widget.transactions_table

    # Should have 3 transactions loaded
    assert table.rowCount() == 3

    # Check first transaction
    assert table.item(0, 0).text() == "2025-10-27"  # Date
    assert table.item(0, 1).text() == "Income"  # Type
    assert table.item(0, 2).text() == "Consulting"  # Category
    assert "Consulting services" in table.item(0, 3).text()  # Description
    assert table.item(0, 4).text() == "$5,000.00"  # Amount


def test_monitoring_status_stopped(dashboard_widget):
    """Test that monitoring status is initially stopped."""
    assert dashboard_widget.get_monitoring_status() is False
    assert dashboard_widget.status_label.text() == "Monitoring: Stopped"
    assert dashboard_widget.toggle_monitoring_button.text() == "Start Monitoring"


def test_start_monitoring(dashboard_widget, mock_document_monitor, qtbot):
    """Test starting document monitoring."""
    # Click start button
    dashboard_widget.toggle_monitoring_button.click()

    # Should call monitor.start()
    mock_document_monitor.start.assert_called_once()

    # Status should be running
    assert dashboard_widget.get_monitoring_status() is True
    assert dashboard_widget.status_label.text() == "Monitoring: Running"
    assert dashboard_widget.toggle_monitoring_button.text() == "Stop Monitoring"


def test_stop_monitoring(dashboard_widget, mock_document_monitor, qtbot):
    """Test stopping document monitoring."""
    # Start monitoring first
    dashboard_widget._start_monitoring()

    # Click stop button
    dashboard_widget.toggle_monitoring_button.click()

    # Should call monitor.stop()
    mock_document_monitor.stop.assert_called_once()

    # Status should be stopped
    assert dashboard_widget.get_monitoring_status() is False
    assert dashboard_widget.status_label.text() == "Monitoring: Stopped"
    assert dashboard_widget.toggle_monitoring_button.text() == "Start Monitoring"


def test_refresh_button(dashboard_widget, mock_transaction_manager, qtbot):
    """Test manual refresh button."""
    # Reset mock call counts
    mock_transaction_manager.get_statistics.reset_mock()
    mock_transaction_manager.query_transactions.reset_mock()

    # Click refresh button
    dashboard_widget.refresh_button.click()

    # Should reload data
    mock_transaction_manager.get_statistics.assert_called_once()
    mock_transaction_manager.query_transactions.assert_called_once()


def test_auto_refresh_toggle(dashboard_widget, qtbot):
    """Test auto-refresh toggle."""
    # Initially auto-refresh should be disabled
    assert not dashboard_widget.refresh_timer.isActive()
    assert dashboard_widget.auto_refresh_button.text() == "Enable Auto-Refresh"

    # Enable auto-refresh
    dashboard_widget.auto_refresh_button.click()

    # Timer should be running
    assert dashboard_widget.refresh_timer.isActive()
    assert dashboard_widget.auto_refresh_button.text() == "Disable Auto-Refresh"

    # Disable auto-refresh
    dashboard_widget.auto_refresh_button.click()

    # Timer should be stopped
    assert not dashboard_widget.refresh_timer.isActive()
    assert dashboard_widget.auto_refresh_button.text() == "Enable Auto-Refresh"


def test_status_changed_signal(dashboard_widget, qtbot):
    """Test that status_changed signal is emitted."""
    with qtbot.waitSignal(dashboard_widget.status_changed, timeout=1000) as blocker:
        dashboard_widget._start_monitoring()

    assert blocker.args == ["running"]


def test_refresh_requested_signal(dashboard_widget, qtbot):
    """Test that refresh_requested signal is emitted."""
    with qtbot.waitSignal(dashboard_widget.refresh_requested, timeout=1000) as blocker:
        dashboard_widget.refresh_button.click()

    assert blocker.signal_triggered


def test_set_backend_services(dashboard_widget, qapp):
    """Test setting backend services."""
    new_database = MagicMock()
    new_manager = MagicMock()
    new_monitor = MagicMock()

    # Mock statistics for new manager
    new_manager.get_statistics.return_value = {
        "total_income": 20000.00,
        "total_expense": 10000.00,
        "count": 50,
    }
    new_manager.query_transactions.return_value = []

    # Set new services
    dashboard_widget.set_backend_services(
        database=new_database, transaction_manager=new_manager, document_monitor=new_monitor
    )

    # Services should be updated
    assert dashboard_widget.database is new_database
    assert dashboard_widget.transaction_manager is new_manager
    assert dashboard_widget.document_monitor is new_monitor

    # Data should be reloaded
    new_manager.get_statistics.assert_called()


def test_no_backend_services(qapp, qtbot):
    """Test dashboard with no backend services."""
    widget = DashboardWidget()
    qtbot.addWidget(widget)

    # Should not crash
    assert widget is not None

    # Statistics should show defaults
    assert widget.income_label.text() == "$0.00"
    assert widget.expense_label.text() == "$0.00"
    assert widget.net_label.text() == "$0.00"
    assert widget.count_label.text() == "0"

    # Table should be empty
    assert widget.transactions_table.rowCount() == 0


def test_transactions_table_headers(dashboard_widget):
    """Test that transactions table has correct headers."""
    table = dashboard_widget.transactions_table

    headers = []
    for i in range(table.columnCount()):
        headers.append(table.horizontalHeaderItem(i).text())

    assert headers == ["Date", "Type", "Category", "Description", "Amount"]


def test_transactions_table_readonly(dashboard_widget):
    """Test that transactions table is read-only."""
    table = dashboard_widget.transactions_table

    # Check edit triggers
    from PySide6.QtWidgets import QTableWidget

    assert table.editTriggers() == QTableWidget.EditTrigger.NoEditTriggers


def test_statistics_error_handling(dashboard_widget, mock_transaction_manager):
    """Test that statistics errors are handled gracefully."""
    # Make get_statistics raise an exception
    mock_transaction_manager.get_statistics.side_effect = Exception("Database error")

    # Should not crash
    dashboard_widget._load_statistics()

    # Statistics should remain unchanged (previous values)
    assert dashboard_widget.income_label.text() == "$15,000.00"


def test_transactions_error_handling(dashboard_widget, mock_transaction_manager):
    """Test that transaction loading errors are handled gracefully."""
    # Make query_transactions raise an exception
    mock_transaction_manager.query_transactions.side_effect = Exception("Database error")

    # Should not crash
    dashboard_widget._load_recent_transactions()

    # Table should have previous data (3 rows from fixture)
    assert dashboard_widget.transactions_table.rowCount() == 3


def test_monitoring_start_error_handling(dashboard_widget, mock_document_monitor):
    """Test that monitoring start errors are handled gracefully."""
    # Make start raise an exception
    mock_document_monitor.start.side_effect = Exception("Monitor error")

    # Should not crash
    dashboard_widget._start_monitoring()

    # Status should remain stopped
    assert dashboard_widget.get_monitoring_status() is False


def test_monitoring_stop_error_handling(dashboard_widget, mock_document_monitor):
    """Test that monitoring stop errors are handled gracefully."""
    # Start monitoring first
    mock_document_monitor.start.side_effect = None
    dashboard_widget._start_monitoring()

    # Make stop raise an exception
    mock_document_monitor.stop.side_effect = Exception("Monitor error")

    # Should not crash
    dashboard_widget._stop_monitoring()

    # Status should remain running (couldn't stop)
    assert dashboard_widget.get_monitoring_status() is True


def test_income_type_color(dashboard_widget):
    """Test that income transactions are displayed in green."""
    table = dashboard_widget.transactions_table

    # First row is income
    type_item = table.item(0, 1)
    assert type_item.text() == "Income"
    # Green color
    assert type_item.foreground().color().name() == "#27ae60"


def test_expense_type_color(dashboard_widget):
    """Test that expense transactions are displayed in red."""
    table = dashboard_widget.transactions_table

    # Second row is expense
    type_item = table.item(1, 1)
    assert type_item.text() == "Expense"
    # Red color
    assert type_item.foreground().color().name() == "#e74c3c"


def test_amount_alignment(dashboard_widget):
    """Test that amounts are right-aligned."""
    table = dashboard_widget.transactions_table

    # Check amount column alignment
    amount_item = table.item(0, 4)
    alignment = amount_item.textAlignment()

    # Should be right-aligned and vertically centered
    assert alignment & Qt.AlignmentFlag.AlignRight
    assert alignment & Qt.AlignmentFlag.AlignVCenter
