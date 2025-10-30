"""Dialog for reviewing and editing extracted transaction data from documents.

Package Name: agentic_bookkeeper
File Name: document_review_dialog.py
Author: Stephen Bogner, P.Eng.
LLM: claude-sonnet-4-5-20250929
Ownership: Stephen Bogner - All Rights Reserved.  See LICENSE.md
Date Created: 2025-10-28
"""

import logging
import os
from datetime import datetime
from typing import Optional
from pathlib import Path

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap, QShortcut, QKeySequence
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
    QMessageBox,
    QDoubleSpinBox,
    QWidget,
    QScrollArea,
    QSplitter,
)

from agentic_bookkeeper.models.transaction import (
    Transaction,
    get_categories_for_jurisdiction,
)
from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.utils.config import Config


class DocumentReviewDialog(QDialog):
    """
    Dialog for reviewing and editing extracted transaction data.

    Shows the document preview alongside editable form fields for the
    extracted transaction data. Allows user to accept (save) or reject
    (discard) the extraction.
    """

    def __init__(
        self,
        extracted_data: dict,
        document_path: str,
        config: Optional[Config] = None,
        transaction_manager: Optional[TransactionManager] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Initialize the document review dialog.

        Args:
            extracted_data: Dictionary containing extracted transaction data
            document_path: Path to the document file
            config: Optional Config instance for dependency injection
            transaction_manager: Optional TransactionManager instance
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing DocumentReviewDialog for document: {document_path}")

        # Store data
        self.extracted_data = extracted_data
        self.document_path = document_path
        self.config = config if config else Config()
        self.transaction_manager = transaction_manager
        self.transaction: Optional[Transaction] = None

        # Get tax jurisdiction for category filtering
        self.jurisdiction = self.config.get("tax_jurisdiction", "CRA")

        # Setup UI
        self.setWindowTitle("Review Extracted Transaction")
        self.setModal(True)
        self.resize(900, 600)

        self._setup_ui()
        self._load_extracted_data()
        self._setup_shortcuts()

        self.logger.info("DocumentReviewDialog initialization complete")

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Create splitter for document preview and form
        splitter = QSplitter(Qt.Horizontal)

        # Left side: Document preview
        preview_widget = self._create_preview_widget()
        splitter.addWidget(preview_widget)

        # Right side: Form
        form_widget = self._create_form_widget()
        splitter.addWidget(form_widget)

        # Set splitter proportions (40% preview, 60% form)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)

        layout.addWidget(splitter)

        # Buttons
        button_layout = self._create_button_layout()
        layout.addLayout(button_layout)

    def _create_preview_widget(self) -> QWidget:
        """Create the document preview widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("Document Preview")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Document filename
        filename = Path(self.document_path).name
        self.filename_label = QLabel(f"File: {filename}")
        self.filename_label.setWordWrap(True)
        layout.addWidget(self.filename_label)

        # Image preview in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(300)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setScaledContents(False)

        # Load and display the image
        self._load_preview_image()

        scroll.setWidget(self.preview_label)
        layout.addWidget(scroll)

        return widget

    def _load_preview_image(self) -> None:
        """Load and display the document preview image."""
        try:
            if not os.path.exists(self.document_path):
                self.preview_label.setText("Document not found")
                return

            # Load image
            pixmap = QPixmap(self.document_path)
            if pixmap.isNull():
                self.preview_label.setText("Cannot preview this document type")
                return

            # Scale to fit while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(400, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)

        except Exception as e:
            self.logger.error(f"Failed to load preview image: {e}", exc_info=True)
            self.preview_label.setText(f"Error loading preview: {str(e)}")

    def _create_form_widget(self) -> QWidget:
        """Create the form widget with transaction fields."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("Extracted Transaction Data")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Review and edit the extracted data below. "
            "Click Accept to save or Reject to discard."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: gray; margin-bottom: 10px;")
        layout.addWidget(instructions)

        # Form layout
        form = QFormLayout()

        # Date picker
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setToolTip(
            "Transaction date extracted from document. Click to open calendar picker if correction needed."
        )
        form.addRow("Date:", self.date_edit)

        # Type dropdown
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Expense", "Income"])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        self.type_combo.setToolTip(
            "Transaction type extracted from document. Select income or expense as appropriate."
        )
        form.addRow("Type:", self.type_combo)

        # Category dropdown (filtered by jurisdiction)
        self.category_combo = QComboBox()
        self._populate_categories()
        self.category_combo.setToolTip(
            "Suggested transaction category based on LLM analysis. Review and adjust if needed."
        )
        form.addRow("Category:", self.category_combo)

        # Vendor/Customer
        self.vendor_edit = QLineEdit()
        self.vendor_edit.setPlaceholderText("Enter vendor or customer name")
        self.vendor_edit.setToolTip(
            "Vendor or customer name extracted from document. Edit if extraction was incorrect."
        )
        form.addRow("Vendor/Customer:", self.vendor_edit)

        # Amount
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setPrefix("$ ")
        self.amount_spin.setDecimals(2)
        self.amount_spin.setMinimum(0.00)
        self.amount_spin.setMaximum(999999.99)
        self.amount_spin.setValue(0.00)
        self.amount_spin.setToolTip(
            "Transaction amount extracted from document. Verify accuracy before accepting."
        )
        form.addRow("Amount:", self.amount_spin)

        # Tax amount
        self.tax_spin = QDoubleSpinBox()
        self.tax_spin.setPrefix("$ ")
        self.tax_spin.setDecimals(2)
        self.tax_spin.setMinimum(0.00)
        self.tax_spin.setMaximum(999999.99)
        self.tax_spin.setValue(0.00)
        self.tax_spin.setToolTip(
            "Tax amount extracted from document. Verify GST/HST or other tax calculations."
        )
        form.addRow("Tax Amount:", self.tax_spin)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter transaction description")
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setToolTip(
            "Transaction description extracted from document. Add or edit notes as needed."
        )
        form.addRow("Description:", self.description_edit)

        layout.addLayout(form)
        layout.addStretch()

        return widget

    def _create_button_layout(self) -> QHBoxLayout:
        """Create the button layout."""
        layout = QHBoxLayout()

        layout.addStretch()

        # Reject button
        self.reject_button = QPushButton("Reject")
        self.reject_button.setToolTip(
            "Reject the extracted data and discard this transaction. "
            "The document will not be saved. Keyboard shortcut: Ctrl+R"
        )
        self.reject_button.clicked.connect(self._on_reject_clicked)
        layout.addWidget(self.reject_button)

        # Accept button
        self.accept_button = QPushButton("Accept && Save")
        self.accept_button.setDefault(True)
        self.accept_button.setToolTip(
            "Accept the reviewed data and save the transaction to the database. "
            "Keyboard shortcut: Ctrl+S"
        )
        self.accept_button.clicked.connect(self._on_accept_clicked)
        layout.addWidget(self.accept_button)

        return layout

    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        # Ctrl+S: Accept and save transaction
        accept_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        accept_shortcut.activated.connect(self._on_accept_clicked)

        # Ctrl+R: Reject transaction
        reject_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        reject_shortcut.activated.connect(self._on_reject_clicked)

    def _populate_categories(self) -> None:
        """Populate the category dropdown based on tax jurisdiction and type."""
        transaction_type = self.type_combo.currentText().lower()
        categories = get_categories_for_jurisdiction(self.jurisdiction)

        # Filter categories by type (expense categories only for expenses)
        # Income categories are typically more generic
        self.category_combo.clear()

        if transaction_type == "expense":
            # Add all categories for expenses
            self.category_combo.addItems(sorted(categories))
        else:
            # For income, use a simpler set of categories
            income_categories = [
                "Sales Revenue",
                "Service Revenue",
                "Interest Income",
                "Other Income",
            ]
            self.category_combo.addItems(income_categories)

    def _on_type_changed(self, type_text: str) -> None:
        """
        Handle transaction type change.

        Args:
            type_text: New type text (Income or Expense)
        """
        # Repopulate categories when type changes
        self._populate_categories()

    def _load_extracted_data(self) -> None:
        """Load extracted data into form fields."""
        try:
            # Date
            date_str = self.extracted_data.get("date", "")
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    self.date_edit.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
                except ValueError:
                    self.logger.warning(f"Invalid date format: {date_str}")

            # Type
            trans_type = self.extracted_data.get("type", "expense").lower()
            if trans_type == "income":
                self.type_combo.setCurrentText("Income")
            else:
                self.type_combo.setCurrentText("Expense")

            # Category
            category = self.extracted_data.get("category", "")
            if category:
                index = self.category_combo.findText(category)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)

            # Vendor/Customer
            vendor = self.extracted_data.get("vendor_customer", "")
            self.vendor_edit.setText(vendor)

            # Amount
            amount = self.extracted_data.get("amount", 0.0)
            if isinstance(amount, (int, float)):
                self.amount_spin.setValue(float(amount))

            # Tax
            tax = self.extracted_data.get("tax_amount", 0.0)
            if isinstance(tax, (int, float)):
                self.tax_spin.setValue(float(tax))

            # Description
            description = self.extracted_data.get("description", "")
            self.description_edit.setPlainText(description)

        except Exception as e:
            self.logger.error(f"Failed to load extracted data: {e}", exc_info=True)
            self._show_error("Load Error", f"Failed to load extracted data: {str(e)}")

    def _validate_fields(self) -> bool:
        """
        Validate all form fields.

        Returns:
            True if all fields are valid, False otherwise
        """
        errors = []

        # Date validation (must be valid date)
        if not self.date_edit.date().isValid():
            errors.append("Date must be a valid date")

        # Category validation (must be selected)
        if not self.category_combo.currentText():
            errors.append("Category must be selected")

        # Amount validation (must be > 0)
        if self.amount_spin.value() <= 0:
            errors.append("Amount must be greater than zero")

        # Tax validation (must be >= 0)
        if self.tax_spin.value() < 0:
            errors.append("Tax amount cannot be negative")

        if errors:
            self._show_error("Validation Error", "\n".join(errors))
            return False

        return True

    def _on_accept_clicked(self) -> None:
        """Handle accept button click."""
        if not self._validate_fields():
            return

        if not self.transaction_manager:
            self._show_error("Error", "Transaction manager is not available")
            return

        try:
            # Create transaction from form data
            date = self.date_edit.date().toString("yyyy-MM-dd")
            trans_type = self.type_combo.currentText().lower()
            category = self.category_combo.currentText()
            vendor = self.vendor_edit.text().strip()
            amount = self.amount_spin.value()
            tax = self.tax_spin.value()
            description = self.description_edit.toPlainText().strip()
            document_filename = Path(self.document_path).name

            # Create transaction
            transaction = Transaction(
                date=date,
                type=trans_type,
                category=category,
                vendor_customer=vendor if vendor else None,
                description=description if description else None,
                amount=amount,
                tax_amount=tax,
                document_filename=document_filename,
            )

            # Save transaction
            self.logger.info(f"Saving transaction from document: {document_filename}")
            saved_transaction = self.transaction_manager.create_transaction(transaction)
            self.transaction = saved_transaction

            self.logger.info(f"Transaction saved successfully with ID: {saved_transaction.id}")

            # Accept dialog
            self.accept()

        except Exception as e:
            self.logger.error(f"Failed to save transaction: {e}", exc_info=True)
            self._show_error("Save Error", f"Failed to save transaction: {str(e)}")

    def _on_reject_clicked(self) -> None:
        """Handle reject button click."""
        # Confirm rejection
        if self._confirm_reject():
            self.logger.info("Transaction rejected by user")
            self.reject()

    def _confirm_reject(self) -> bool:
        """
        Show confirmation dialog for rejection.

        Returns:
            True if user confirms rejection, False otherwise
        """
        # Check if running in test mode
        if os.environ.get("PYTEST_CURRENT_TEST"):
            self.logger.info("Test mode: Auto-confirming reject")
            return True

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirm Reject")
        msg_box.setText("Are you sure you want to reject this transaction?")
        msg_box.setInformativeText(
            "The extracted data will be discarded and the document "
            "will not be saved to the database."
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        result = msg_box.exec()
        return result == QMessageBox.Yes

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

    def get_transaction(self) -> Optional[Transaction]:
        """
        Get the saved transaction.

        Returns:
            The saved transaction if accepted, None otherwise
        """
        return self.transaction
