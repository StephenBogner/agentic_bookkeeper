"""Reports widget for generating and exporting financial reports.

Package Name: agentic_bookkeeper
File Name: reports_widget.py
Author: Stephen Bogner, P.Eng.
LLM: claude-sonnet-4-5-20250929
Ownership: Stephen Bogner - All Rights Reserved.  See LICENSE
Date Created: 2025-10-29
"""

import logging
from datetime import datetime, date
from typing import Optional, Dict, Any
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QComboBox,
    QDateEdit,
    QTextEdit,
    QProgressBar,
    QFileDialog,
    QMessageBox,
)

from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.core.report_generator import ReportGenerator
from agentic_bookkeeper.core.exporters.pdf_exporter import PDFExporter
from agentic_bookkeeper.core.exporters.csv_exporter import CSVExporter
from agentic_bookkeeper.core.exporters.json_exporter import JSONExporter
from agentic_bookkeeper.models.database import Database
from agentic_bookkeeper.utils.config import Config


class ReportsWidget(QWidget):
    """
    Widget for generating and exporting financial reports.

    Provides report type selection, date range picker, format selector,
    preview functionality, and export capabilities.
    """

    # Signals
    report_generated = Signal(dict)  # Emitted when report is generated
    export_completed = Signal(str)  # Emitted when export completes

    def __init__(
        self,
        database: Optional[Database] = None,
        transaction_manager: Optional[TransactionManager] = None,
        config: Optional[Config] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Initialize the reports widget.

        Args:
            database: Database instance for querying data
            transaction_manager: Transaction manager for operations
            config: Configuration instance
            parent: Optional parent widget

        Raises:
            TypeError: If arguments are wrong type
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing ReportsWidget")

        # Validate inputs
        if database is not None and not isinstance(database, Database):
            raise TypeError(f"Expected Database, got {type(database)}")
        if transaction_manager is not None and not isinstance(
            transaction_manager, TransactionManager
        ):
            raise TypeError(f"Expected TransactionManager, got {type(transaction_manager)}")
        if config is not None and not isinstance(config, Config):
            raise TypeError(f"Expected Config, got {type(config)}")

        # Backend services
        self.database = database
        self.transaction_manager = transaction_manager
        self.config = config if config else Config()

        # Initialize report generator
        self.report_generator = None
        if self.transaction_manager:
            self.report_generator = ReportGenerator(self.transaction_manager)

        # Current report data
        self._current_report_data: Optional[Dict[str, Any]] = None

        # Setup UI
        self._setup_ui()
        self._connect_signals()
        self._setup_shortcuts()

        self.logger.info("ReportsWidget initialization complete")

    def _setup_ui(self) -> None:
        """Set up the user interface layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Report controls section
        main_layout.addWidget(self._create_report_controls())

        # Preview section
        main_layout.addWidget(self._create_preview_section())

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Action buttons
        main_layout.addLayout(self._create_action_buttons())

        self.setLayout(main_layout)

    def _create_report_controls(self) -> QGroupBox:
        """Create report control widgets."""
        group = QGroupBox("Report Parameters")
        layout = QVBoxLayout()

        # Report type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Report Type:"))
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["Income Statement", "Expense Report"])
        self.report_type_combo.setToolTip(
            "Select report type: Income Statement shows income and expenses with net income, "
            "Expense Report shows detailed expense breakdown by category."
        )
        type_layout.addWidget(self.report_type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Date range section
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date Range:"))

        # Date preset selector
        self.date_preset_combo = QComboBox()
        self.date_preset_combo.addItems(
            [
                "Custom",
                "This Month",
                "Last Month",
                "This Quarter",
                "Last Quarter",
                "This Year",
                "Last Year",
            ]
        )
        self.date_preset_combo.setToolTip(
            "Quick date range presets. Select 'Custom' to manually set start and end dates. "
            "Preset selections automatically update the date range below."
        )
        date_layout.addWidget(self.date_preset_combo)

        # Start date
        date_layout.addWidget(QLabel("From:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.start_date_edit.setToolTip(
            "Report start date. Click to open calendar picker. "
            "Transactions from this date onwards will be included."
        )
        date_layout.addWidget(self.start_date_edit)

        # End date
        date_layout.addWidget(QLabel("To:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setToolTip(
            "Report end date. Click to open calendar picker. "
            "Transactions up to and including this date will be included."
        )
        date_layout.addWidget(self.end_date_edit)

        date_layout.addStretch()
        layout.addLayout(date_layout)

        # Format selector
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Export Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PDF", "CSV", "JSON"])
        self.format_combo.setToolTip(
            "Export format for the report: PDF for formatted documents, "
            "CSV for spreadsheet import, JSON for data processing."
        )
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        layout.addLayout(format_layout)

        group.setLayout(layout)
        return group

    def _create_preview_section(self) -> QGroupBox:
        """Create preview section."""
        group = QGroupBox("Preview")
        layout = QVBoxLayout()

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Click 'Generate Preview' to see report preview...")
        layout.addWidget(self.preview_text)

        group.setLayout(layout)
        return group

    def _create_action_buttons(self) -> QHBoxLayout:
        """Create action buttons."""
        layout = QHBoxLayout()
        layout.addStretch()

        self.generate_button = QPushButton("Generate Preview")
        self.generate_button.setEnabled(self.report_generator is not None)
        self.generate_button.setToolTip(
            "Generate report preview with selected parameters. "
            "Review the preview before exporting. Keyboard shortcut: Ctrl+G"
        )
        layout.addWidget(self.generate_button)

        self.export_button = QPushButton("Export Report")
        self.export_button.setEnabled(False)
        self.export_button.setToolTip(
            "Export the generated report to a file in the selected format. "
            "Generate a preview first before exporting. Keyboard shortcut: Ctrl+E"
        )
        layout.addWidget(self.export_button)

        return layout

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self.date_preset_combo.currentTextChanged.connect(self._on_preset_changed)
        self.generate_button.clicked.connect(self._on_generate_clicked)
        self.export_button.clicked.connect(self._on_export_clicked)

    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        # Ctrl+G: Generate report preview
        generate_shortcut = QShortcut(QKeySequence("Ctrl+G"), self)
        generate_shortcut.activated.connect(self._on_generate_clicked)

        # Ctrl+E: Export report
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(self._on_export_clicked)

    def _on_preset_changed(self, preset: str) -> None:
        """
        Handle date preset selection.

        Args:
            preset: Selected preset name
        """
        if preset == "Custom":
            return

        today = date.today()
        start_date = today
        end_date = today

        if preset == "This Month":
            start_date = today.replace(day=1)
            end_date = today
        elif preset == "Last Month":
            last_month = today.replace(day=1)
            if last_month.month == 1:
                last_month = last_month.replace(year=last_month.year - 1, month=12)
            else:
                last_month = last_month.replace(month=last_month.month - 1)
            start_date = last_month
            # Last day of last month
            if last_month.month == 12:
                end_date = last_month.replace(year=last_month.year + 1, month=1, day=1)
            else:
                end_date = last_month.replace(month=last_month.month + 1, day=1)
            from datetime import timedelta

            end_date = end_date - timedelta(days=1)
        elif preset == "This Quarter":
            quarter = (today.month - 1) // 3
            start_date = today.replace(month=quarter * 3 + 1, day=1)
            end_date = today
        elif preset == "Last Quarter":
            quarter = (today.month - 1) // 3
            if quarter == 0:
                start_date = today.replace(year=today.year - 1, month=10, day=1)
                end_date = today.replace(year=today.year - 1, month=12, day=31)
            else:
                start_date = today.replace(month=(quarter - 1) * 3 + 1, day=1)
                end_month = quarter * 3
                if end_month == 12:
                    end_date = today.replace(month=12, day=31)
                else:
                    from datetime import timedelta

                    end_date = today.replace(month=end_month + 1, day=1) - timedelta(days=1)
        elif preset == "This Year":
            start_date = today.replace(month=1, day=1)
            end_date = today
        elif preset == "Last Year":
            start_date = today.replace(year=today.year - 1, month=1, day=1)
            end_date = today.replace(year=today.year - 1, month=12, day=31)

        # Update date edits
        self.start_date_edit.setDate(QDate(start_date.year, start_date.month, start_date.day))
        self.end_date_edit.setDate(QDate(end_date.year, end_date.month, end_date.day))

    def _on_generate_clicked(self) -> None:
        """Handle generate button click."""
        try:
            # Validate inputs
            if not self._validate_inputs():
                return

            # Show progress
            self._show_progress("Generating report...")

            # Get parameters
            report_type = self.report_type_combo.currentText()
            start_date = self.start_date_edit.date().toPython()
            end_date = self.end_date_edit.date().toPython()

            # Generate report
            if report_type == "Income Statement":
                report_data = self.report_generator.generate_income_statement(start_date, end_date)
            else:  # Expense Report
                report_data = self.report_generator.generate_expense_report(start_date, end_date)

            # Store report data
            self._current_report_data = report_data

            # Update preview
            self._update_preview(report_data)

            # Enable export button
            self.export_button.setEnabled(True)

            # Emit signal
            self.report_generated.emit(report_data)

            self.logger.info(f"Generated {report_type} successfully")

        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            self._show_error(f"Error generating report: {str(e)}")
        finally:
            self._hide_progress()

    def _on_export_clicked(self) -> None:
        """Handle export button click."""
        if not self._current_report_data:
            self._show_error("No report to export. Generate a report first.")
            return

        try:
            # Get export format
            export_format = self.format_combo.currentText()

            # Get save file path
            file_filter = f"{export_format} Files (*.{export_format.lower()})"
            default_filename = self._get_default_filename(export_format)
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Report", default_filename, file_filter
            )

            if not file_path:
                return  # User cancelled

            # Show progress
            self._show_progress(f"Exporting to {export_format}...")

            # Get jurisdiction and currency from config
            jurisdiction = self.config.get("tax_jurisdiction", "CRA")
            currency = self.config.get("currency", "CAD")

            # Export based on format
            if export_format == "PDF":
                exporter = PDFExporter(jurisdiction, currency)
            elif export_format == "CSV":
                exporter = CSVExporter(jurisdiction, currency)
            else:  # JSON
                exporter = JSONExporter(jurisdiction, currency)

            exporter.export(self._current_report_data, file_path)

            # Show success message
            QMessageBox.information(
                self, "Export Complete", f"Report exported successfully to:\n{file_path}"
            )

            # Emit signal
            self.export_completed.emit(file_path)

            self.logger.info(f"Exported report to {file_path}")

        except Exception as e:
            self.logger.error(f"Error exporting report: {e}")
            self._show_error(f"Error exporting report: {str(e)}")
        finally:
            self._hide_progress()

    def _update_preview(self, report_data: Dict[str, Any]) -> None:
        """
        Update preview text with report data.

        Args:
            report_data: Report data dictionary
        """
        preview_text = []

        # Metadata
        metadata = report_data.get("metadata", {})
        preview_text.append("=" * 60)
        preview_text.append(metadata.get("title", "Report").upper())
        preview_text.append("=" * 60)
        preview_text.append(f"Period: {metadata.get('start_date')} to {metadata.get('end_date')}")
        preview_text.append(f"Generated: {metadata.get('generated_at')}")
        preview_text.append("")

        # Summary
        summary = report_data.get("summary", {})
        preview_text.append("SUMMARY")
        preview_text.append("-" * 60)

        if "total_income" in summary:
            preview_text.append(f"Total Income:    {summary['total_income']}")
            preview_text.append(f"Total Expenses:  {summary['total_expenses']}")
            preview_text.append(f"Net Income:      {summary['net_income']}")
        else:
            preview_text.append(f"Total Expenses:  {summary['total_expenses']}")

        preview_text.append("")

        # Categories
        report_type = metadata.get("report_type")
        if report_type == "income_statement":
            # Income categories
            income_categories = report_data.get("income_categories", [])
            if income_categories:
                preview_text.append("INCOME BY CATEGORY")
                preview_text.append("-" * 60)
                for cat in income_categories:
                    preview_text.append(
                        f"{cat['category']:30s} {cat['amount']:>15s} " f"({cat['percentage']:>6s})"
                    )
                preview_text.append("")

            # Expense categories
            expense_categories = report_data.get("expense_categories", [])
            if expense_categories:
                preview_text.append("EXPENSES BY CATEGORY")
                preview_text.append("-" * 60)
                for cat in expense_categories:
                    preview_text.append(
                        f"{cat['category']:30s} {cat['amount']:>15s} " f"({cat['percentage']:>6s})"
                    )
        else:  # expense_report
            categories = report_data.get("categories", [])
            if categories:
                preview_text.append("EXPENSES BY CATEGORY")
                preview_text.append("-" * 60)
                for cat in categories:
                    tax_code = cat.get("tax_code", "N/A")
                    preview_text.append(
                        f"{cat['category']:25s} {tax_code:10s} "
                        f"{cat['amount']:>15s} ({cat['percentage']:>6s})"
                    )

        self.preview_text.setPlainText("\n".join(preview_text))

    def _validate_inputs(self) -> bool:
        """
        Validate user inputs.

        Returns:
            True if inputs are valid, False otherwise
        """
        # Check date range
        start_date = self.start_date_edit.date().toPython()
        end_date = self.end_date_edit.date().toPython()

        if start_date > end_date:
            self._show_error("Start date must be before or equal to end date.")
            return False

        # Check if report generator is available
        if not self.report_generator:
            self._show_error("Report generator not available.")
            return False

        return True

    def _show_progress(self, message: str) -> None:
        """
        Show progress indicator.

        Args:
            message: Progress message to display
        """
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.generate_button.setEnabled(False)
        self.export_button.setEnabled(False)

    def _hide_progress(self) -> None:
        """Hide progress indicator."""
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)
        if self._current_report_data:
            self.export_button.setEnabled(True)

    def _show_error(self, message: str) -> None:
        """
        Show error message to user.

        Args:
            message: Error message to display
        """
        QMessageBox.critical(self, "Error", message)

    def _get_default_filename(self, export_format: str) -> str:
        """
        Get default filename for export.

        Args:
            export_format: Export format (PDF, CSV, JSON)

        Returns:
            Default filename string
        """
        report_type = self.report_type_combo.currentText().lower().replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = export_format.lower()
        return f"{report_type}_{timestamp}.{extension}"
