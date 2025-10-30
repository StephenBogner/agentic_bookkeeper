"""
Tests for transaction edit dialog.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-28
"""

import pytest
import os
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QDialogButtonBox

from agentic_bookkeeper.gui.transaction_edit_dialog import TransactionEditDialog
from agentic_bookkeeper.models.transaction import Transaction
from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.utils.config import Config


@pytest.fixture
def sample_transaction():
    """Create a sample transaction for testing."""
    return Transaction(
        id=1,
        date="2025-01-15",
        type="expense",
        category="Office expenses",
        vendor_customer="Office Supplies Inc",
        description="Monthly office supplies",
        amount=125.50,
        tax_amount=16.25,
        document_filename="invoice_001.pdf",
    )


@pytest.fixture
def mock_config():
    """Create a mock Config instance."""
    config = Mock(spec=Config)
    config.get = Mock(return_value="CRA")
    return config


@pytest.fixture
def mock_transaction_manager():
    """Create a mock TransactionManager."""
    return Mock(spec=TransactionManager)


@pytest.fixture
def edit_dialog(qtbot, sample_transaction, mock_config, mock_transaction_manager):
    """Create a TransactionEditDialog for testing."""
    # Set test mode environment variable
    original_test_env = os.environ.get("PYTEST_CURRENT_TEST")
    os.environ["PYTEST_CURRENT_TEST"] = "test"

    dialog = TransactionEditDialog(
        transaction=sample_transaction,
        config=mock_config,
        transaction_manager=mock_transaction_manager,
    )
    qtbot.addWidget(dialog)

    yield dialog

    # Restore environment variable
    if original_test_env is not None:
        os.environ["PYTEST_CURRENT_TEST"] = original_test_env
    else:
        os.environ.pop("PYTEST_CURRENT_TEST", None)


class TestTransactionEditDialogInitialization:
    """Test dialog initialization."""

    def test_initialization(self, edit_dialog, sample_transaction):
        """Test dialog initializes correctly."""
        assert edit_dialog.transaction == sample_transaction
        assert edit_dialog.windowTitle() == "Edit Transaction #1"
        assert edit_dialog.isModal()

    def test_loads_transaction_data(self, edit_dialog, sample_transaction):
        """Test transaction data is loaded into form fields."""
        # Date
        qdate = edit_dialog.date_edit.date()
        assert qdate.year() == 2025
        assert qdate.month() == 1
        assert qdate.day() == 15

        # Type
        assert edit_dialog.type_combo.currentText() == "expense"

        # Category
        assert edit_dialog.category_combo.currentText() == "Office expenses"

        # Vendor/Customer
        assert edit_dialog.vendor_edit.text() == "Office Supplies Inc"

        # Amount
        assert edit_dialog.amount_spin.value() == 125.50

        # Tax
        assert edit_dialog.tax_spin.value() == 16.25

        # Description
        assert edit_dialog.description_edit.toPlainText() == "Monthly office supplies"

        # Document
        assert edit_dialog.document_label.text() == "invoice_001.pdf"


class TestTransactionEditDialogWidgets:
    """Test individual widget functionality."""

    def test_date_edit_exists(self, edit_dialog):
        """Test date edit widget exists and is configured."""
        assert edit_dialog.date_edit is not None
        assert edit_dialog.date_edit.calendarPopup()
        assert edit_dialog.date_edit.displayFormat() == "yyyy-MM-dd"

    def test_type_combo_exists(self, edit_dialog):
        """Test type combo box exists with correct items."""
        assert edit_dialog.type_combo is not None
        assert edit_dialog.type_combo.count() == 2
        assert edit_dialog.type_combo.itemText(0) == "income"
        assert edit_dialog.type_combo.itemText(1) == "expense"

    def test_category_combo_populated(self, edit_dialog):
        """Test category combo is populated."""
        assert edit_dialog.category_combo is not None
        assert edit_dialog.category_combo.count() > 0

    def test_vendor_edit_exists(self, edit_dialog):
        """Test vendor/customer edit exists."""
        assert edit_dialog.vendor_edit is not None
        assert edit_dialog.vendor_edit.placeholderText() == "Enter vendor or customer name"

    def test_amount_spin_configured(self, edit_dialog):
        """Test amount spin box is configured correctly."""
        assert edit_dialog.amount_spin is not None
        assert edit_dialog.amount_spin.prefix() == "$"
        assert edit_dialog.amount_spin.decimals() == 2
        assert edit_dialog.amount_spin.minimum() == 0.00
        assert edit_dialog.amount_spin.maximum() == 999999.99

    def test_tax_spin_configured(self, edit_dialog):
        """Test tax spin box is configured correctly."""
        assert edit_dialog.tax_spin is not None
        assert edit_dialog.tax_spin.prefix() == "$"
        assert edit_dialog.tax_spin.decimals() == 2
        assert edit_dialog.tax_spin.minimum() == 0.00

    def test_description_edit_exists(self, edit_dialog):
        """Test description text edit exists."""
        assert edit_dialog.description_edit is not None
        assert edit_dialog.description_edit.placeholderText() == "Enter transaction description"


class TestTransactionEditDialogValidation:
    """Test form validation."""

    def test_validate_fields_with_valid_data(self, edit_dialog):
        """Test validation passes with valid data."""
        assert edit_dialog._validate_fields() is True

    def test_validate_fields_with_zero_amount(self, edit_dialog, qtbot):
        """Test validation fails with zero amount."""
        edit_dialog.amount_spin.setValue(0.00)
        assert edit_dialog._validate_fields() is False

    def test_validate_fields_with_negative_tax(self, edit_dialog):
        """Test validation with negative tax (spin box prevents this)."""
        # QDoubleSpinBox with minimum 0.00 prevents negative values
        # Attempting to set negative value will be clamped to minimum
        edit_dialog.tax_spin.setValue(-10.00)
        # Value should be clamped to 0.00 (minimum)
        assert edit_dialog.tax_spin.value() == 0.00
        # Validation should still pass with clamped value
        assert edit_dialog._validate_fields() is True

    def test_validate_fields_without_category(self, edit_dialog):
        """Test validation with empty category."""
        # Clear all items first, then validation should fail
        edit_dialog.category_combo.clear()
        assert edit_dialog._validate_fields() is False


class TestTransactionEditDialogSave:
    """Test save functionality."""

    def test_save_updates_transaction(self, edit_dialog, mock_transaction_manager, qtbot):
        """Test saving updates the transaction object."""
        # Modify some fields
        edit_dialog.vendor_edit.setText("New Vendor")
        edit_dialog.amount_spin.setValue(200.00)
        edit_dialog.description_edit.setPlainText("Updated description")

        # Click save button
        edit_dialog._on_save()

        # Verify transaction was updated
        assert edit_dialog.transaction.vendor_customer == "New Vendor"
        assert edit_dialog.transaction.amount == 200.00
        assert edit_dialog.transaction.description == "Updated description"

    def test_save_calls_transaction_manager(self, edit_dialog, mock_transaction_manager, qtbot):
        """Test save calls transaction manager update."""
        edit_dialog._on_save()

        # Verify transaction manager was called
        mock_transaction_manager.update_transaction.assert_called_once()
        assert (
            mock_transaction_manager.update_transaction.call_args[0][0] == edit_dialog.transaction
        )

    def test_save_updates_modified_timestamp(self, edit_dialog, qtbot):
        """Test save updates modified timestamp."""
        original_modified = edit_dialog.transaction.modified_at

        # Wait a moment to ensure timestamp changes
        import time

        time.sleep(0.01)

        edit_dialog._on_save()

        # Modified timestamp should be updated
        assert edit_dialog.transaction.modified_at != original_modified

    def test_save_with_validation_error(self, edit_dialog, mock_transaction_manager, qtbot):
        """Test save doesn't proceed with validation error."""
        # Set invalid amount
        edit_dialog.amount_spin.setValue(0.00)

        edit_dialog._on_save()

        # Transaction manager should not be called
        mock_transaction_manager.update_transaction.assert_not_called()

    def test_save_without_transaction_manager(self, qtbot, sample_transaction, mock_config):
        """Test save without transaction manager (no persistence)."""
        dialog = TransactionEditDialog(
            transaction=sample_transaction, config=mock_config, transaction_manager=None
        )
        qtbot.addWidget(dialog)

        # Should not raise exception
        dialog._on_save()

    def test_save_accepts_dialog(self, edit_dialog, qtbot):
        """Test successful save accepts the dialog."""
        with patch.object(edit_dialog, "accept") as mock_accept:
            edit_dialog._on_save()
            mock_accept.assert_called_once()


class TestTransactionEditDialogButtons:
    """Test button functionality."""

    def test_has_save_button(self, edit_dialog):
        """Test dialog has save button."""
        button_box = edit_dialog.findChild(QDialogButtonBox)
        assert button_box is not None
        assert button_box.button(QDialogButtonBox.Save) is not None

    def test_has_cancel_button(self, edit_dialog):
        """Test dialog has cancel button."""
        button_box = edit_dialog.findChild(QDialogButtonBox)
        assert button_box is not None
        assert button_box.button(QDialogButtonBox.Cancel) is not None

    def test_cancel_button_rejects_dialog(self, edit_dialog, qtbot):
        """Test cancel button rejects the dialog."""
        with patch.object(edit_dialog, "reject") as mock_reject:
            button_box = edit_dialog.findChild(QDialogButtonBox)
            cancel_button = button_box.button(QDialogButtonBox.Cancel)
            qtbot.mouseClick(cancel_button, Qt.LeftButton)
            mock_reject.assert_called_once()


class TestTransactionEditDialogTypeChange:
    """Test transaction type changes."""

    def test_type_change_signal(self, edit_dialog, qtbot):
        """Test changing transaction type triggers handler."""
        with patch.object(edit_dialog, "_on_type_changed") as mock_handler:
            edit_dialog.type_combo.setCurrentText("income")
            mock_handler.assert_called_with("income")


class TestTransactionEditDialogCategoryPopulation:
    """Test category population based on jurisdiction."""

    def test_categories_populated_for_cra(
        self, qtbot, sample_transaction, mock_transaction_manager
    ):
        """Test categories are populated for CRA jurisdiction."""
        config = Mock(spec=Config)
        config.get = Mock(return_value="CRA")

        dialog = TransactionEditDialog(
            transaction=sample_transaction,
            config=config,
            transaction_manager=mock_transaction_manager,
        )
        qtbot.addWidget(dialog)

        # Should have CRA categories
        assert dialog.category_combo.count() > 0
        # Check for a known CRA category
        categories = [
            dialog.category_combo.itemText(i) for i in range(dialog.category_combo.count())
        ]
        assert "Office expenses" in categories

    def test_categories_populated_for_irs(
        self, qtbot, sample_transaction, mock_transaction_manager
    ):
        """Test categories are populated for IRS jurisdiction."""
        config = Mock(spec=Config)
        config.get = Mock(return_value="IRS")

        dialog = TransactionEditDialog(
            transaction=sample_transaction,
            config=config,
            transaction_manager=mock_transaction_manager,
        )
        qtbot.addWidget(dialog)

        # Should have IRS categories
        assert dialog.category_combo.count() > 0


class TestTransactionEditDialogGetTransaction:
    """Test get_transaction method."""

    def test_get_transaction_returns_transaction(self, edit_dialog):
        """Test get_transaction returns the transaction object."""
        transaction = edit_dialog.get_transaction()
        assert transaction == edit_dialog.transaction
        assert transaction.id == 1


class TestTransactionEditDialogEdgeCases:
    """Test edge cases and error handling."""

    def test_transaction_without_optional_fields(
        self, qtbot, mock_config, mock_transaction_manager
    ):
        """Test editing transaction with minimal data."""
        transaction = Transaction(
            id=2, date="2025-01-20", type="income", category="Sales", amount=500.00
        )

        dialog = TransactionEditDialog(
            transaction=transaction,
            config=mock_config,
            transaction_manager=mock_transaction_manager,
        )
        qtbot.addWidget(dialog)

        # Should load successfully
        assert dialog.vendor_edit.text() == ""
        assert dialog.description_edit.toPlainText() == ""
        assert dialog.document_label.text() == "(none)"

    def test_transaction_with_category_not_in_list(
        self, qtbot, mock_config, mock_transaction_manager
    ):
        """Test transaction with category not in current jurisdiction list."""
        transaction = Transaction(
            id=3, date="2025-01-20", type="expense", category="Custom Category", amount=100.00
        )

        dialog = TransactionEditDialog(
            transaction=transaction,
            config=mock_config,
            transaction_manager=mock_transaction_manager,
        )
        qtbot.addWidget(dialog)

        # Category should still be set (added temporarily)
        assert dialog.category_combo.currentText() == "Custom Category"

    def test_save_with_empty_vendor(self, edit_dialog, qtbot):
        """Test save with empty vendor (should be None)."""
        edit_dialog.vendor_edit.setText("")
        edit_dialog._on_save()

        assert edit_dialog.transaction.vendor_customer is None

    def test_save_with_whitespace_only_description(self, edit_dialog, qtbot):
        """Test save with whitespace-only description (should be None)."""
        edit_dialog.description_edit.setPlainText("   ")
        edit_dialog._on_save()

        assert edit_dialog.transaction.description is None


class TestTransactionEditDialogTestMode:
    """Test dialog behavior in test mode."""

    def test_error_dialog_skipped_in_test_mode(self, edit_dialog, qtbot):
        """Test error dialogs are skipped in test mode."""
        # Set invalid amount to trigger validation error
        edit_dialog.amount_spin.setValue(0.00)

        # Should not raise exception or show dialog
        edit_dialog._on_save()
        # Test passes if no exception is raised


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
