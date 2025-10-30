"""Dialog for adding new transactions manually.

Package Name: agentic_bookkeeper
File Name: transaction_add_dialog.py
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


class TransactionAddDialog(QDialog):
    """
    Dialog for adding a new transaction manually.

    Provides form fields for all transaction attributes with validation
    and connects to the transaction manager for persistence.
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        transaction_manager: Optional[TransactionManager] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Initialize the transaction add dialog.

        Args:
            config: Optional Config instance for dependency injection
            transaction_manager: Optional TransactionManager instance
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing TransactionAddDialog")

        # Store dependencies
        self.config = config if config else Config()
        self.transaction_manager = transaction_manager
        self.created_transaction: Optional[Transaction] = None

        # Get tax jurisdiction for category filtering
        self.jurisdiction = self.config.get("tax_jurisdiction", "CRA")

        # Setup UI
        self.setWindowTitle("Add New Transaction")
        self.setModal(True)
        self.resize(500, 400)

        self._setup_ui()
        self._set_defaults()
        self._setup_shortcuts()

        self.logger.info("TransactionAddDialog initialization complete")

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
        self._populate_categories()
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

        layout.addLayout(form)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._on_save)
        button_box.rejected.connect(self.reject)

        # Add tooltip to Save button
        save_button = button_box.button(QDialogButtonBox.Save)
        if save_button:
            save_button.setToolTip("Save the new transaction. Keyboard shortcut: Ctrl+S")

        # Add tooltip to Cancel button
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        if cancel_button:
            cancel_button.setToolTip(
                "Cancel and close dialog without saving. Keyboard shortcut: Esc"
            )

        layout.addWidget(button_box)

    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        # Ctrl+S: Save transaction
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self._on_save)

    def _populate_categories(self) -> None:
        """Populate category dropdown based on tax jurisdiction."""
        try:
            categories = get_categories_for_jurisdiction(self.jurisdiction)
            self.category_combo.clear()
            self.category_combo.addItems(categories)
            self.logger.debug(f"Populated {len(categories)} categories for {self.jurisdiction}")
        except Exception as e:
            self.logger.error(f"Failed to populate categories: {e}")
            self.category_combo.clear()

    def _set_defaults(self) -> None:
        """Set default values for new transaction."""
        try:
            # Set date to today
            today = datetime.now().date()
            qdate = QDate(today.year, today.month, today.day)
            self.date_edit.setDate(qdate)

            # Set default type to expense (most common)
            self.type_combo.setCurrentText("expense")

            # Set default amount to 0.00
            self.amount_spin.setValue(0.00)
            self.tax_spin.setValue(0.00)

            self.logger.debug("Default values set for new transaction")

        except Exception as e:
            self.logger.error(f"Failed to set default values: {e}")

    def _on_type_changed(self, new_type: str) -> None:
        """
        Handle transaction type change.

        Args:
            new_type: The new transaction type ('income' or 'expense')
        """
        self.logger.debug(f"Transaction type changed to: {new_type}")
        # Could update UI styling based on type if desired

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
            # Create new transaction object
            qdate = self.date_edit.date()
            date_str = f"{qdate.year()}-{qdate.month():02d}-{qdate.day():02d}"

            transaction = Transaction(
                date=date_str,
                type=self.type_combo.currentText(),
                category=self.category_combo.currentText(),
                amount=self.amount_spin.value(),
                vendor_customer=self.vendor_edit.text().strip() or None,
                description=self.description_edit.toPlainText().strip() or None,
                tax_amount=self.tax_spin.value(),
                document_filename=None,  # Manual entry has no document
            )

            # Validate transaction
            transaction.validate()

            # Create in database if transaction manager is available
            if self.transaction_manager:
                created_id = self.transaction_manager.create_transaction(transaction)
                transaction.id = created_id
                self.created_transaction = transaction
                self.logger.info(f"Transaction {created_id} created successfully")
            else:
                self.logger.warning("No transaction manager available - changes not persisted")
                self.created_transaction = transaction

            # Accept dialog
            self.accept()

        except ValueError as e:
            self.logger.error(f"Validation error: {e}")
            self._show_error("Validation Error", str(e))
        except Exception as e:
            self.logger.error(f"Failed to create transaction: {e}")
            self._show_error("Save Failed", f"Failed to create transaction: {str(e)}")

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

    def get_transaction(self) -> Optional[Transaction]:
        """
        Get the created transaction.

        Returns:
            The created transaction object, or None if not created
        """
        return self.created_transaction
