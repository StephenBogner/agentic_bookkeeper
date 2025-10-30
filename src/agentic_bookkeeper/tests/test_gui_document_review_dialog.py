"""
Unit tests for DocumentReviewDialog.

Tests document preview, form fields, validation, and accept/reject functionality.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QMessageBox

from agentic_bookkeeper.gui.document_review_dialog import DocumentReviewDialog
from agentic_bookkeeper.models.transaction import Transaction
from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.utils.config import Config


@pytest.fixture
def sample_extracted_data():
    """Sample extracted transaction data."""
    return {
        "date": "2025-10-28",
        "type": "expense",
        "category": "Advertising",  # Use a category that's in CRA list
        "vendor_customer": "Office Depot",
        "amount": 150.75,
        "tax_amount": 22.61,
        "description": "Printer paper and ink cartridges",
    }


@pytest.fixture
def sample_image_path(tmp_path):
    """Create a sample image file."""
    # Create a simple 100x100 image
    pixmap = QPixmap(100, 100)
    pixmap.fill(Qt.white)

    image_path = tmp_path / "test_receipt.png"
    pixmap.save(str(image_path))

    return str(image_path)


@pytest.fixture
def mock_config():
    """Mock Config instance."""
    config = Mock(spec=Config)
    config.get.return_value = "CRA"
    return config


@pytest.fixture
def mock_transaction_manager():
    """Mock TransactionManager instance."""
    manager = Mock(spec=TransactionManager)

    # Mock create_transaction to return a transaction with ID
    def create_transaction(transaction):
        transaction.id = 1
        return transaction

    manager.create_transaction.side_effect = create_transaction
    return manager


class TestDocumentReviewDialogInitialization:
    """Test document review dialog initialization."""

    def test_dialog_creation(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that dialog can be created."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)
        assert dialog is not None

    def test_dialog_with_backend(
        self, qtbot, sample_extracted_data, sample_image_path, mock_config, mock_transaction_manager
    ):
        """Test dialog creation with backend services."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data,
            document_path=sample_image_path,
            config=mock_config,
            transaction_manager=mock_transaction_manager,
        )
        qtbot.addWidget(dialog)

        assert dialog.config == mock_config
        assert dialog.transaction_manager == mock_transaction_manager

    def test_dialog_title(self, qtbot, sample_extracted_data, sample_image_path):
        """Test dialog has correct title."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Review Extracted Transaction"

    def test_form_fields_exist(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that all form fields are created."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        assert dialog.date_edit is not None
        assert dialog.type_combo is not None
        assert dialog.category_combo is not None
        assert dialog.vendor_edit is not None
        assert dialog.amount_spin is not None
        assert dialog.tax_spin is not None
        assert dialog.description_edit is not None

    def test_buttons_exist(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that accept and reject buttons are created."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        assert dialog.accept_button is not None
        assert dialog.reject_button is not None


class TestDataLoading:
    """Test loading extracted data into form fields."""

    def test_load_date(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that date is loaded correctly."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        assert dialog.date_edit.date() == QDate(2025, 10, 28)

    def test_load_type(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that transaction type is loaded correctly."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        assert dialog.type_combo.currentText() == "Expense"

    def test_load_category(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that category is loaded correctly."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        # Check that the category from sample data (Advertising) is loaded
        assert dialog.category_combo.currentText() == "Advertising"

    def test_load_vendor(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that vendor is loaded correctly."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        assert dialog.vendor_edit.text() == "Office Depot"

    def test_load_amount(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that amount is loaded correctly."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        assert dialog.amount_spin.value() == 150.75

    def test_load_tax(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that tax amount is loaded correctly."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        assert dialog.tax_spin.value() == 22.61

    def test_load_description(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that description is loaded correctly."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        assert dialog.description_edit.toPlainText() == "Printer paper and ink cartridges"

    def test_load_invalid_date(self, qtbot, sample_image_path):
        """Test handling of invalid date format."""
        data = {
            "date": "invalid-date",
            "type": "expense",
            "category": "Office Supplies",
            "amount": 100.0,
            "tax_amount": 0.0,
        }

        dialog = DocumentReviewDialog(extracted_data=data, document_path=sample_image_path)
        qtbot.addWidget(dialog)

        # Should use current date as fallback
        assert dialog.date_edit.date().isValid()

    def test_load_income_type(self, qtbot, sample_image_path):
        """Test loading income transaction type."""
        data = {
            "date": "2025-10-28",
            "type": "income",
            "category": "Sales Revenue",
            "amount": 1000.0,
            "tax_amount": 0.0,
        }

        dialog = DocumentReviewDialog(extracted_data=data, document_path=sample_image_path)
        qtbot.addWidget(dialog)

        assert dialog.type_combo.currentText() == "Income"


class TestDocumentPreview:
    """Test document preview functionality."""

    def test_preview_label_exists(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that preview label is created."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        assert dialog.preview_label is not None

    def test_preview_loads_image(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that image preview loads successfully."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        # Check that pixmap was loaded
        assert not dialog.preview_label.pixmap().isNull()

    def test_preview_missing_file(self, qtbot, sample_extracted_data):
        """Test preview handling when file doesn't exist."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path="/nonexistent/file.png"
        )
        qtbot.addWidget(dialog)

        # Should show error message
        assert dialog.preview_label.text() == "Document not found"

    def test_filename_displayed(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that filename is displayed."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        expected_filename = Path(sample_image_path).name
        assert expected_filename in dialog.filename_label.text()


class TestValidation:
    """Test field validation."""

    def test_validate_valid_data(self, qtbot, sample_extracted_data, sample_image_path):
        """Test validation with valid data."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        assert dialog._validate_fields() is True

    def test_validate_zero_amount(self, qtbot, sample_extracted_data, sample_image_path):
        """Test validation fails with zero amount."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        dialog.amount_spin.setValue(0.0)

        with patch.object(QMessageBox, "exec"):
            assert dialog._validate_fields() is False

    def test_validate_tax_spin_minimum(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that tax spinbox has minimum of 0."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        # Spinbox minimum should be 0
        assert dialog.tax_spin.minimum() == 0.0

        # Try to set negative value (should be clamped to 0)
        dialog.tax_spin.setValue(-10.0)
        assert dialog.tax_spin.value() == 0.0

    def test_validate_empty_category(self, qtbot, sample_image_path):
        """Test validation fails with empty category."""
        data = {
            "date": "2025-10-28",
            "type": "expense",
            "category": "",
            "amount": 100.0,
            "tax_amount": 0.0,
        }

        dialog = DocumentReviewDialog(extracted_data=data, document_path=sample_image_path)
        qtbot.addWidget(dialog)

        dialog.category_combo.setCurrentIndex(-1)

        with patch.object(QMessageBox, "exec"):
            assert dialog._validate_fields() is False


class TestTypeChange:
    """Test transaction type change functionality."""

    def test_type_change_repopulates_categories(
        self, qtbot, sample_extracted_data, sample_image_path
    ):
        """Test that changing type repopulates categories."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        initial_count = dialog.category_combo.count()

        # Change to income
        dialog.type_combo.setCurrentText("Income")

        # Category list should change
        assert dialog.category_combo.count() != initial_count

    def test_income_categories(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that income categories are shown for income type."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        dialog.type_combo.setCurrentText("Income")

        # Should have income-specific categories
        categories = [
            dialog.category_combo.itemText(i) for i in range(dialog.category_combo.count())
        ]
        assert "Sales Revenue" in categories


class TestAcceptFunctionality:
    """Test accept button functionality."""

    def test_accept_creates_transaction(
        self, qtbot, sample_extracted_data, sample_image_path, mock_transaction_manager
    ):
        """Test that accepting creates a transaction."""
        os.environ["PYTEST_CURRENT_TEST"] = "test"

        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data,
            document_path=sample_image_path,
            transaction_manager=mock_transaction_manager,
        )
        qtbot.addWidget(dialog)

        dialog._on_accept_clicked()

        # Verify transaction was created
        mock_transaction_manager.create_transaction.assert_called_once()

    def test_accept_validation_fails(
        self, qtbot, sample_extracted_data, sample_image_path, mock_transaction_manager
    ):
        """Test that accept fails if validation fails."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data,
            document_path=sample_image_path,
            transaction_manager=mock_transaction_manager,
        )
        qtbot.addWidget(dialog)

        # Set invalid amount
        dialog.amount_spin.setValue(0.0)

        with patch.object(QMessageBox, "exec"):
            dialog._on_accept_clicked()

        # Transaction should not be created
        mock_transaction_manager.create_transaction.assert_not_called()

    def test_accept_no_manager(self, qtbot, sample_extracted_data, sample_image_path):
        """Test accept when no transaction manager is available."""
        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        with patch.object(QMessageBox, "exec"):
            dialog._on_accept_clicked()

    def test_accept_stores_transaction(
        self, qtbot, sample_extracted_data, sample_image_path, mock_transaction_manager
    ):
        """Test that accepted transaction is stored."""
        os.environ["PYTEST_CURRENT_TEST"] = "test"

        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data,
            document_path=sample_image_path,
            transaction_manager=mock_transaction_manager,
        )
        qtbot.addWidget(dialog)

        dialog._on_accept_clicked()

        # Check transaction is stored
        transaction = dialog.get_transaction()
        assert transaction is not None
        assert transaction.id == 1

    def test_accept_includes_document_filename(
        self, qtbot, sample_extracted_data, sample_image_path, mock_transaction_manager
    ):
        """Test that transaction includes document filename."""
        os.environ["PYTEST_CURRENT_TEST"] = "test"

        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data,
            document_path=sample_image_path,
            transaction_manager=mock_transaction_manager,
        )
        qtbot.addWidget(dialog)

        dialog._on_accept_clicked()

        # Check that create_transaction was called with document filename
        call_args = mock_transaction_manager.create_transaction.call_args
        transaction = call_args[0][0]
        assert transaction.document_filename == Path(sample_image_path).name


class TestRejectFunctionality:
    """Test reject button functionality."""

    def test_reject_confirmation_in_test_mode(
        self, qtbot, sample_extracted_data, sample_image_path
    ):
        """Test that rejection auto-confirms in test mode."""
        os.environ["PYTEST_CURRENT_TEST"] = "test"

        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        # Should auto-confirm in test mode
        assert dialog._confirm_reject() is True

    def test_reject_no_transaction_created(
        self, qtbot, sample_extracted_data, sample_image_path, mock_transaction_manager
    ):
        """Test that rejecting doesn't create a transaction."""
        os.environ["PYTEST_CURRENT_TEST"] = "test"

        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data,
            document_path=sample_image_path,
            transaction_manager=mock_transaction_manager,
        )
        qtbot.addWidget(dialog)

        dialog._on_reject_clicked()

        # Transaction should not be created
        mock_transaction_manager.create_transaction.assert_not_called()

    def test_get_transaction_after_reject(self, qtbot, sample_extracted_data, sample_image_path):
        """Test that get_transaction returns None after rejection."""
        os.environ["PYTEST_CURRENT_TEST"] = "test"

        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data, document_path=sample_image_path
        )
        qtbot.addWidget(dialog)

        dialog._on_reject_clicked()

        assert dialog.get_transaction() is None


class TestErrorHandling:
    """Test error handling."""

    def test_accept_error_handling(
        self, qtbot, sample_extracted_data, sample_image_path, mock_transaction_manager
    ):
        """Test error handling when accept fails."""
        mock_transaction_manager.create_transaction.side_effect = Exception("Database error")

        dialog = DocumentReviewDialog(
            extracted_data=sample_extracted_data,
            document_path=sample_image_path,
            transaction_manager=mock_transaction_manager,
        )
        qtbot.addWidget(dialog)

        with patch.object(QMessageBox, "exec"):
            dialog._on_accept_clicked()

        # Transaction should not be stored
        assert dialog.get_transaction() is None
