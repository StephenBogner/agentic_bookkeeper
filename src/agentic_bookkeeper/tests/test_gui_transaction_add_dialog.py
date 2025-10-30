"""
Tests for transaction add dialog.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-28
"""

import pytest
import os
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QDialogButtonBox, QDialog

from agentic_bookkeeper.gui.transaction_add_dialog import TransactionAddDialog
from agentic_bookkeeper.models.transaction import Transaction
from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.utils.config import Config


@pytest.fixture
def mock_config():
    """Create a mock Config instance."""
    config = Mock(spec=Config)
    config.get = Mock(return_value="CRA")
    return config


@pytest.fixture
def mock_transaction_manager():
    """Create a mock TransactionManager."""
    tm = Mock(spec=TransactionManager)
    tm.create_transaction = Mock(return_value=123)  # Mock ID for created transaction
    return tm


@pytest.fixture
def add_dialog(qtbot, mock_config, mock_transaction_manager):
    """Create a TransactionAddDialog for testing."""
    # Set test mode environment variable
    original_test_env = os.environ.get("PYTEST_CURRENT_TEST")
    os.environ["PYTEST_CURRENT_TEST"] = "test"

    dialog = TransactionAddDialog(config=mock_config, transaction_manager=mock_transaction_manager)
    qtbot.addWidget(dialog)

    yield dialog

    # Restore environment variable
    if original_test_env is not None:
        os.environ["PYTEST_CURRENT_TEST"] = original_test_env
    else:
        os.environ.pop("PYTEST_CURRENT_TEST", None)


class TestTransactionAddDialogInitialization:
    """Test dialog initialization."""

    def test_initialization(self, add_dialog):
        """Test dialog initializes correctly."""
        assert add_dialog.windowTitle() == "Add New Transaction"
        assert add_dialog.isModal()
        assert add_dialog.created_transaction is None

    def test_default_values_set(self, add_dialog):
        """Test default values are set correctly."""
        # Date should be today
        today = datetime.now().date()
        qdate = add_dialog.date_edit.date()
        assert qdate.year() == today.year
        assert qdate.month() == today.month
        assert qdate.day() == today.day

        # Default type should be expense
        assert add_dialog.type_combo.currentText() == "expense"

        # Default amounts should be 0.00
        assert add_dialog.amount_spin.value() == 0.00
        assert add_dialog.tax_spin.value() == 0.00

        # Fields should be empty
        assert add_dialog.vendor_edit.text() == ""
        assert add_dialog.description_edit.toPlainText() == ""


class TestTransactionAddDialogWidgets:
    """Test dialog widgets."""

    def test_has_date_edit(self, add_dialog):
        """Test dialog has date edit widget."""
        assert add_dialog.date_edit is not None
        assert add_dialog.date_edit.calendarPopup()
        assert add_dialog.date_edit.displayFormat() == "yyyy-MM-dd"

    def test_has_type_combo(self, add_dialog):
        """Test dialog has type combo box."""
        assert add_dialog.type_combo is not None
        assert add_dialog.type_combo.count() == 2
        assert add_dialog.type_combo.itemText(0) == "income"
        assert add_dialog.type_combo.itemText(1) == "expense"

    def test_has_category_combo(self, add_dialog):
        """Test dialog has category combo box."""
        assert add_dialog.category_combo is not None
        # Should have categories populated
        assert add_dialog.category_combo.count() > 0

    def test_has_vendor_edit(self, add_dialog):
        """Test dialog has vendor/customer edit."""
        assert add_dialog.vendor_edit is not None
        assert add_dialog.vendor_edit.placeholderText() == "Enter vendor or customer name"

    def test_has_amount_spin(self, add_dialog):
        """Test dialog has amount spin box."""
        assert add_dialog.amount_spin is not None
        assert add_dialog.amount_spin.prefix() == "$"
        assert add_dialog.amount_spin.decimals() == 2
        assert add_dialog.amount_spin.minimum() == 0.00
        assert add_dialog.amount_spin.maximum() == 999999.99

    def test_has_tax_spin(self, add_dialog):
        """Test dialog has tax amount spin box."""
        assert add_dialog.tax_spin is not None
        assert add_dialog.tax_spin.prefix() == "$"
        assert add_dialog.tax_spin.decimals() == 2
        assert add_dialog.tax_spin.minimum() == 0.00

    def test_has_description_edit(self, add_dialog):
        """Test dialog has description text edit."""
        assert add_dialog.description_edit is not None
        assert add_dialog.description_edit.placeholderText() == "Enter transaction description"


class TestTransactionAddDialogValidation:
    """Test field validation."""

    def test_validation_requires_positive_amount(self, add_dialog):
        """Test validation fails for zero amount."""
        add_dialog.amount_spin.setValue(0.00)
        assert not add_dialog._validate_fields()

    def test_validation_passes_for_positive_amount(self, add_dialog):
        """Test validation passes for positive amount."""
        add_dialog.amount_spin.setValue(100.00)
        assert add_dialog._validate_fields()

    def test_validation_requires_category(self, add_dialog):
        """Test validation requires a category."""
        # Clear the combo box completely
        add_dialog.category_combo.clear()
        add_dialog.amount_spin.setValue(100.00)
        assert not add_dialog._validate_fields()

    def test_validation_allows_zero_tax(self, add_dialog):
        """Test validation allows zero tax amount."""
        add_dialog.amount_spin.setValue(100.00)
        add_dialog.tax_spin.setValue(0.00)
        assert add_dialog._validate_fields()

    def test_validation_enforces_non_negative_tax(self, add_dialog):
        """Test that tax spin box enforces non-negative values."""
        # The QDoubleSpinBox has minimum set to 0.00, so it won't accept negative values
        add_dialog.amount_spin.setValue(100.00)
        add_dialog.tax_spin.setValue(0.00)  # Minimum value
        assert add_dialog.tax_spin.minimum() == 0.00
        assert add_dialog._validate_fields()


class TestTransactionAddDialogSave:
    """Test save functionality."""

    def test_save_creates_transaction(self, add_dialog, mock_transaction_manager, qtbot):
        """Test save button creates transaction."""
        # Set valid values
        add_dialog.date_edit.setDate(QDate(2025, 10, 28))
        add_dialog.type_combo.setCurrentText("expense")
        add_dialog.category_combo.setCurrentIndex(0)
        add_dialog.vendor_edit.setText("Test Vendor")
        add_dialog.amount_spin.setValue(100.00)
        add_dialog.tax_spin.setValue(13.00)
        add_dialog.description_edit.setPlainText("Test transaction")

        # Trigger save
        add_dialog._on_save()

        # Verify transaction manager was called
        mock_transaction_manager.create_transaction.assert_called_once()

        # Verify created transaction has correct values
        created_transaction = add_dialog.get_transaction()
        assert created_transaction is not None
        assert created_transaction.id == 123
        assert created_transaction.date == "2025-10-28"
        assert created_transaction.type == "expense"
        assert created_transaction.vendor_customer == "Test Vendor"
        assert created_transaction.amount == 100.00
        assert created_transaction.tax_amount == 13.00
        assert created_transaction.description == "Test transaction"
        assert created_transaction.document_filename is None

    def test_save_validates_before_creating(self, add_dialog, mock_transaction_manager):
        """Test save validates fields before creating."""
        # Set invalid amount (zero)
        add_dialog.amount_spin.setValue(0.00)

        # Trigger save
        add_dialog._on_save()

        # Verify transaction manager was not called
        mock_transaction_manager.create_transaction.assert_not_called()

    def test_save_strips_whitespace_from_text_fields(self, add_dialog, mock_transaction_manager):
        """Test save strips whitespace from text fields."""
        add_dialog.date_edit.setDate(QDate(2025, 10, 28))
        add_dialog.type_combo.setCurrentText("income")
        add_dialog.category_combo.setCurrentIndex(0)
        add_dialog.vendor_edit.setText("  Test Vendor  ")
        add_dialog.amount_spin.setValue(100.00)
        add_dialog.description_edit.setPlainText("  Test description  ")

        add_dialog._on_save()

        created_transaction = add_dialog.get_transaction()
        assert created_transaction.vendor_customer == "Test Vendor"
        assert created_transaction.description == "Test description"

    def test_save_converts_empty_strings_to_none(self, add_dialog, mock_transaction_manager):
        """Test save converts empty strings to None."""
        add_dialog.date_edit.setDate(QDate(2025, 10, 28))
        add_dialog.type_combo.setCurrentText("expense")
        add_dialog.category_combo.setCurrentIndex(0)
        add_dialog.vendor_edit.setText("")
        add_dialog.amount_spin.setValue(100.00)
        add_dialog.description_edit.setPlainText("")

        add_dialog._on_save()

        created_transaction = add_dialog.get_transaction()
        assert created_transaction.vendor_customer is None
        assert created_transaction.description is None


class TestTransactionAddDialogButtons:
    """Test dialog buttons."""

    def test_has_save_button(self, add_dialog):
        """Test dialog has save button."""
        button_box = add_dialog.findChild(QDialogButtonBox)
        assert button_box is not None
        save_button = button_box.button(QDialogButtonBox.Save)
        assert save_button is not None

    def test_has_cancel_button(self, add_dialog):
        """Test dialog has cancel button."""
        button_box = add_dialog.findChild(QDialogButtonBox)
        assert button_box is not None
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        assert cancel_button is not None

    def test_cancel_button_rejects_dialog(self, add_dialog, qtbot):
        """Test cancel button rejects the dialog."""
        button_box = add_dialog.findChild(QDialogButtonBox)
        cancel_button = button_box.button(QDialogButtonBox.Cancel)

        with qtbot.waitSignal(add_dialog.rejected):
            cancel_button.click()

        assert add_dialog.created_transaction is None

    def test_save_button_accepts_dialog_on_valid_data(self, add_dialog, qtbot):
        """Test save button accepts dialog when data is valid."""
        # Set valid values
        add_dialog.date_edit.setDate(QDate(2025, 10, 28))
        add_dialog.type_combo.setCurrentText("expense")
        add_dialog.category_combo.setCurrentIndex(0)
        add_dialog.amount_spin.setValue(100.00)

        button_box = add_dialog.findChild(QDialogButtonBox)
        save_button = button_box.button(QDialogButtonBox.Save)

        with qtbot.waitSignal(add_dialog.accepted):
            save_button.click()

        assert add_dialog.created_transaction is not None


class TestTransactionAddDialogCategories:
    """Test category handling."""

    def test_populates_categories_for_cra(self, qtbot, mock_transaction_manager):
        """Test categories are populated for CRA jurisdiction."""
        config = Mock(spec=Config)
        config.get = Mock(return_value="CRA")

        os.environ["PYTEST_CURRENT_TEST"] = "test"
        dialog = TransactionAddDialog(config=config, transaction_manager=mock_transaction_manager)
        qtbot.addWidget(dialog)

        # Should have CRA categories
        assert dialog.category_combo.count() > 0
        os.environ.pop("PYTEST_CURRENT_TEST", None)

    def test_populates_categories_for_irs(self, qtbot, mock_transaction_manager):
        """Test categories are populated for IRS jurisdiction."""
        config = Mock(spec=Config)
        config.get = Mock(return_value="IRS")

        os.environ["PYTEST_CURRENT_TEST"] = "test"
        dialog = TransactionAddDialog(config=config, transaction_manager=mock_transaction_manager)
        qtbot.addWidget(dialog)

        # Should have IRS categories
        assert dialog.category_combo.count() > 0
        os.environ.pop("PYTEST_CURRENT_TEST", None)


class TestTransactionAddDialogTypeChange:
    """Test transaction type change handling."""

    def test_type_change_triggers_handler(self, add_dialog, qtbot):
        """Test type change triggers the handler."""
        with patch.object(add_dialog, "_on_type_changed") as mock_handler:
            add_dialog.type_combo.setCurrentText("income")
            mock_handler.assert_called()


class TestTransactionAddDialogEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_transaction_manager_error(self, add_dialog, mock_transaction_manager):
        """Test handles transaction manager errors gracefully."""
        # Make transaction manager raise an error
        mock_transaction_manager.create_transaction.side_effect = Exception("Database error")

        # Set valid values
        add_dialog.date_edit.setDate(QDate(2025, 10, 28))
        add_dialog.type_combo.setCurrentText("expense")
        add_dialog.category_combo.setCurrentIndex(0)
        add_dialog.amount_spin.setValue(100.00)

        # Should not crash
        add_dialog._on_save()

        # Should not create transaction
        assert add_dialog.created_transaction is None

    def test_works_without_transaction_manager(self, qtbot, mock_config):
        """Test dialog works without transaction manager."""
        os.environ["PYTEST_CURRENT_TEST"] = "test"
        dialog = TransactionAddDialog(config=mock_config, transaction_manager=None)
        qtbot.addWidget(dialog)

        # Set valid values
        dialog.date_edit.setDate(QDate(2025, 10, 28))
        dialog.type_combo.setCurrentText("expense")
        dialog.category_combo.setCurrentIndex(0)
        dialog.amount_spin.setValue(100.00)

        # Should not crash
        dialog._on_save()

        # Should create transaction object but not persist
        assert dialog.created_transaction is not None
        assert dialog.created_transaction.id is None  # Not persisted

        os.environ.pop("PYTEST_CURRENT_TEST", None)

    def test_get_transaction_returns_none_before_save(self, add_dialog):
        """Test get_transaction returns None before save."""
        assert add_dialog.get_transaction() is None

    def test_maximum_amount_values(self, add_dialog):
        """Test maximum amount values."""
        add_dialog.amount_spin.setValue(999999.99)
        add_dialog.tax_spin.setValue(999999.99)

        assert add_dialog.amount_spin.value() == 999999.99
        assert add_dialog.tax_spin.value() == 999999.99
