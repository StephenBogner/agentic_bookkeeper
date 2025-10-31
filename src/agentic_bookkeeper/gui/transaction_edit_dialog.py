"""Dialog for editing existing transactions.

Package Name: agentic_bookkeeper
File Name: transaction_edit_dialog.py
Author: Stephen Bogner, P.Eng.
LLM: claude-sonnet-4-5-20250929
Ownership: Stephen Bogner - All Rights Reserved.  See LICENSE
Date Created: 2025-10-28
"""

import logging
import os
from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QDateEdit,
    QPushButton,
    QDialogButtonBox,
    QMessageBox,
    QDoubleSpinBox,
    QWidget,
)

from agentic_bookkeeper.models.transaction import (
    Transaction,
    get_categories_for_jurisdiction,
)
from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.utils.config import Config


class TransactionEditDialog(QDialog):
    """
    Dialog for editing an existing transaction.

    Provides form fields for all transaction attributes with validation
    and connects to the transaction manager for persistence.
    """

    def __init__(
        self,
        transaction: Transaction,
        config: Optional[Config] = None,
        transaction_manager: Optional[TransactionManager] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Initialize the transaction edit dialog.

        Args:
            transaction: The transaction to edit
            config: Optional Config instance for dependency injection
            transaction_manager: Optional TransactionManager instance
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing TransactionEditDialog for transaction ID: {transaction.id}")

        # Store original transaction
        self.transaction = transaction
        self.config = config if config else Config()
        self.transaction_manager = transaction_manager

        # Get tax jurisdiction for category filtering
        self.jurisdiction = self.config.get("tax_jurisdiction", "CRA")

        # Setup UI
        self.setWindowTitle(f"Edit Transaction #{transaction.id}")
        self.setModal(True)
        self.resize(500, 400)

        self._setup_ui()
        self._load_transaction_data()
        self._setup_shortcuts()

        self.logger.info("TransactionEditDialog initialization complete")

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Form layout
        form = QFormLayout()

        # Date picker
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setToolTip(
            "Transaction date. Click to open calendar picker for easy date selection."
        )
        form.addRow("Date:", self.date_edit)

        # Type selector
        self.type_combo = QComboBox()
        self.type_combo.addItems(["income", "expense"])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        self.type_combo.setToolTip(
            "Transaction type: income for money received, expense for money spent."
        )
        form.addRow("Type:", self.type_combo)

        # Category dropdown
        self.category_combo = QComboBox()
        # Categories will be populated in _load_transaction_data() with proper filtering
        self.category_combo.setToolTip(
            "Transaction category for tax reporting. Categories are based on your tax jurisdiction."
        )
        form.addRow("Category:", self.category_combo)

        # Vendor/Customer input
        self.vendor_edit = QLineEdit()
        self.vendor_edit.setPlaceholderText("Enter vendor or customer name")
        self.vendor_edit.setToolTip(
            "Name of the vendor (for expenses) or customer (for income). Optional field."
        )
        form.addRow("Vendor/Customer:", self.vendor_edit)

        # Amount input
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setPrefix("$")
        self.amount_spin.setDecimals(2)
        self.amount_spin.setMinimum(0.00)
        self.amount_spin.setMaximum(999999.99)
        self.amount_spin.setSingleStep(0.01)
        self.amount_spin.setToolTip(
            "Transaction amount before tax. Enter the base amount in your local currency."
        )
        form.addRow("Amount:", self.amount_spin)

        # Tax amount input
        self.tax_spin = QDoubleSpinBox()
        self.tax_spin.setPrefix("$")
        self.tax_spin.setDecimals(2)
        self.tax_spin.setMinimum(0.00)
        self.tax_spin.setMaximum(999999.99)
        self.tax_spin.setSingleStep(0.01)
        self.tax_spin.setToolTip(
            "Tax amount (e.g., GST, HST, sales tax). Enter 0 if no tax applies."
        )
        form.addRow("Tax Amount:", self.tax_spin)

        # Description text area
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter transaction description")
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setToolTip(
            "Optional description or notes about this transaction for future reference."
        )
        form.addRow("Description:", self.description_edit)

        # Document filename (read-only)
        self.document_label = QLabel()
        self.document_label.setStyleSheet("color: gray;")
        self.document_label.setToolTip(
            "Source document filename if this transaction was extracted from a document."
        )
        form.addRow("Document:", self.document_label)

        layout.addLayout(form)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._on_save)
        button_box.rejected.connect(self.reject)

        # Add tooltip to Save button
        save_button = button_box.button(QDialogButtonBox.Save)
        if save_button:
            save_button.setToolTip("Save changes to the transaction. Keyboard shortcut: Ctrl+S")

        # Add tooltip to Cancel button
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        if cancel_button:
            cancel_button.setToolTip(
                "Cancel editing and close dialog without saving. Keyboard shortcut: Esc"
            )

        layout.addWidget(button_box)

    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        # Ctrl+S: Save transaction
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self._on_save)

    def _populate_categories(self, transaction_type: Optional[str] = None) -> None:
        """
        Populate category dropdown based on tax jurisdiction and transaction type.

        Args:
            transaction_type: Optional filter by 'income' or 'expense'
        """
        try:
            # Get current selection to preserve it if possible
            current_category = self.category_combo.currentText()

            # Get categories filtered by type
            categories = get_categories_for_jurisdiction(self.jurisdiction, transaction_type)
            self.category_combo.clear()
            self.category_combo.addItems(categories)

            # Try to restore previous selection if it's still valid
            if current_category and current_category in categories:
                self.category_combo.setCurrentText(current_category)

            self.logger.debug(
                f"Populated {len(categories)} {transaction_type or 'all'} categories for {self.jurisdiction}"
            )
        except Exception as e:
            self.logger.error(f"Failed to populate categories: {e}")
            self.category_combo.clear()

    def _load_transaction_data(self) -> None:
        """Load transaction data into form fields."""
        try:
            # Date
            date_obj = datetime.strptime(self.transaction.date, "%Y-%m-%d").date()
            qdate = QDate(date_obj.year, date_obj.month, date_obj.day)
            self.date_edit.setDate(qdate)

            # Type
            type_index = self.type_combo.findText(self.transaction.type)
            if type_index >= 0:
                self.type_combo.setCurrentIndex(type_index)

            # Re-populate categories based on transaction type
            self._populate_categories(transaction_type=self.transaction.type)

            # Category
            category_index = self.category_combo.findText(self.transaction.category)
            if category_index >= 0:
                self.category_combo.setCurrentIndex(category_index)
            else:
                # Category not found - add it temporarily
                self.category_combo.addItem(self.transaction.category)
                self.category_combo.setCurrentText(self.transaction.category)
                self.logger.warning(
                    f"Category '{self.transaction.category}' not in {self.jurisdiction} list"
                )

            # Vendor/Customer
            if self.transaction.vendor_customer:
                self.vendor_edit.setText(self.transaction.vendor_customer)

            # Amount
            self.amount_spin.setValue(self.transaction.amount)

            # Tax
            self.tax_spin.setValue(self.transaction.tax_amount)

            # Description
            if self.transaction.description:
                self.description_edit.setPlainText(self.transaction.description)

            # Document filename
            if self.transaction.document_filename:
                self.document_label.setText(self.transaction.document_filename)
            else:
                self.document_label.setText("(none)")

            self.logger.debug("Transaction data loaded into form")

        except Exception as e:
            self.logger.error(f"Failed to load transaction data: {e}")
            self._show_error("Failed to load transaction data", str(e))

    def _on_type_changed(self, new_type: str) -> None:
        """
        Handle transaction type change.

        Args:
            new_type: The new transaction type ('income' or 'expense')
        """
        self.logger.debug(f"Transaction type changed to: {new_type}")
        # Re-populate categories based on the new type
        self._populate_categories(transaction_type=new_type)

    def _validate_fields(self) -> bool:
        """
        Validate all form fields.

        Returns:
            True if all fields are valid, False otherwise
        """
        # Validate date
        if not self.date_edit.date().isValid():
            self._show_error("Invalid Date", "Please select a valid date.")
            return False

        # Validate category
        if not self.category_combo.currentText():
            self._show_error("Invalid Category", "Please select a category.")
            return False

        # Validate amount (must be > 0)
        if self.amount_spin.value() <= 0:
            self._show_error("Invalid Amount", "Amount must be greater than zero.")
            return False

        # Validate tax amount (must be >= 0)
        if self.tax_spin.value() < 0:
            self._show_error("Invalid Tax", "Tax amount must be greater than or equal to zero.")
            return False

        return True

    def _on_save(self) -> None:
        """Handle save button click."""
        if not self._validate_fields():
            return

        try:
            # Update transaction object
            qdate = self.date_edit.date()
            self.transaction.date = f"{qdate.year()}-{qdate.month():02d}-{qdate.day():02d}"
            self.transaction.type = self.type_combo.currentText()
            self.transaction.category = self.category_combo.currentText()
            self.transaction.vendor_customer = self.vendor_edit.text().strip() or None
            self.transaction.amount = self.amount_spin.value()
            self.transaction.tax_amount = self.tax_spin.value()
            self.transaction.description = self.description_edit.toPlainText().strip() or None

            # Update modified timestamp
            self.transaction.update_modified_timestamp()

            # Validate transaction
            self.transaction.validate()

            # Update in database if transaction manager is available
            if self.transaction_manager:
                self.transaction_manager.update_transaction(self.transaction)
                self.logger.info(f"Transaction {self.transaction.id} updated successfully")
            else:
                self.logger.warning("No transaction manager available - changes not persisted")

            # Accept dialog
            self.accept()

        except ValueError as e:
            self.logger.error(f"Validation error: {e}")
            self._show_error("Validation Error", str(e))
        except Exception as e:
            self.logger.error(f"Failed to save transaction: {e}")
            self._show_error("Save Failed", f"Failed to save transaction: {str(e)}")

    def _show_error(self, title: str, message: str) -> None:
        """
        Show error message dialog.

        Args:
            title: Error dialog title
            message: Error message
        """
        # Check if running in test mode
        if os.environ.get("PYTEST_CURRENT_TEST"):
            self.logger.warning(f"Test mode: Skipping error dialog - {title}: {message}")
            return

        QMessageBox.critical(self, title, message)

    def get_transaction(self) -> Transaction:
        """
        Get the updated transaction.

        Returns:
            The modified transaction object
        """
        return self.transaction
