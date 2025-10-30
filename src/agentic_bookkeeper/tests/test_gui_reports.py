"""
Package Name: agentic_bookkeeper
File Name: test_gui_reports.py
Description: Test suite for ReportsWidget GUI component
Author: Stephen Bogner, P.Eng.
LLM: claude-sonnet-4-5-20250929
Ownership: Stephen Bogner - All Rights Reserved.  See LICENSE
Date Created: 2025-10-29
"""

import pytest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from decimal import Decimal

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QMessageBox

from agentic_bookkeeper.gui.reports_widget import ReportsWidget
from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.core.report_generator import ReportGenerator
from agentic_bookkeeper.models.database import Database
from agentic_bookkeeper.models.transaction import Transaction
from agentic_bookkeeper.utils.config import Config


class TestReportsWidget:
    """Test suite for ReportsWidget."""

    @pytest.fixture
    def mock_database(self):
        """Create mock database."""
        return Mock(spec=Database)

    @pytest.fixture
    def mock_config(self):
        """Create mock config."""
        config = Mock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            "tax_jurisdiction": "CRA",
            "currency": "CAD",
        }.get(key, default)
        return config

    @pytest.fixture
    def mock_transaction_manager(self, mock_database):
        """Create mock transaction manager."""
        return Mock(spec=TransactionManager)

    @pytest.fixture
    def sample_transactions(self):
        """Create sample transactions for testing."""
        return [
            Transaction(
                id=1,
                transaction_date=date(2025, 1, 15),
                amount=Decimal("1500.00"),
                transaction_type="income",
                category="Sales",
                description="Product sales",
                vendor_customer="Customer A",
            ),
            Transaction(
                id=2,
                transaction_date=date(2025, 1, 20),
                amount=Decimal("500.00"),
                transaction_type="expense",
                category="Office Supplies",
                description="Office equipment",
                vendor_customer="Vendor B",
            ),
        ]

    @pytest.fixture
    def sample_report_data(self):
        """Create sample report data."""
        return {
            "metadata": {
                "title": "Income Statement",
                "report_type": "income_statement",
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
                "generated_at": "2025-01-31 12:00:00",
                "jurisdiction": "CRA",
                "currency": "CAD",
            },
            "summary": {
                "total_income": "$1,500.00",
                "total_expenses": "$500.00",
                "net_income": "$1,000.00",
            },
            "income_categories": [
                {
                    "category": "Sales",
                    "amount": "$1,500.00",
                    "percentage": "100.0%",
                }
            ],
            "expense_categories": [
                {
                    "category": "Office Supplies",
                    "amount": "$500.00",
                    "percentage": "100.0%",
                }
            ],
        }

    @pytest.fixture
    def widget(self, qtbot, mock_database, mock_transaction_manager, mock_config):
        """Create ReportsWidget for testing."""
        widget = ReportsWidget(
            database=mock_database,
            transaction_manager=mock_transaction_manager,
            config=mock_config,
        )
        qtbot.addWidget(widget)
        return widget

    def test_initialization_with_valid_inputs(
        self, qtbot, mock_database, mock_transaction_manager, mock_config
    ):
        """Test widget initializes with valid inputs."""
        widget = ReportsWidget(
            database=mock_database,
            transaction_manager=mock_transaction_manager,
            config=mock_config,
        )
        qtbot.addWidget(widget)

        assert widget.database == mock_database
        assert widget.transaction_manager == mock_transaction_manager
        assert widget.config == mock_config
        assert widget.report_generator is not None

    def test_initialization_without_dependencies(self, qtbot):
        """Test widget initializes without dependencies."""
        widget = ReportsWidget()
        qtbot.addWidget(widget)

        assert widget.database is None
        assert widget.transaction_manager is None
        assert widget.config is not None
        assert widget.report_generator is None

    def test_initialization_with_invalid_database(self, qtbot):
        """Test widget raises error with invalid database."""
        with pytest.raises(TypeError, match="Expected Database"):
            ReportsWidget(database="invalid")

    def test_initialization_with_invalid_transaction_manager(self, qtbot, mock_database):
        """Test widget raises error with invalid transaction manager."""
        with pytest.raises(TypeError, match="Expected TransactionManager"):
            ReportsWidget(database=mock_database, transaction_manager="invalid")

    def test_initialization_with_invalid_config(self, qtbot, mock_database):
        """Test widget raises error with invalid config."""
        with pytest.raises(TypeError, match="Expected Config"):
            ReportsWidget(database=mock_database, config="invalid")

    def test_ui_elements_created(self, widget):
        """Test all UI elements are created."""
        assert widget.report_type_combo is not None
        assert widget.date_preset_combo is not None
        assert widget.start_date_edit is not None
        assert widget.end_date_edit is not None
        assert widget.format_combo is not None
        assert widget.preview_text is not None
        assert widget.progress_bar is not None
        assert widget.generate_button is not None
        assert widget.export_button is not None

    def test_report_type_combo_items(self, widget):
        """Test report type combo has correct items."""
        assert widget.report_type_combo.count() == 2
        assert widget.report_type_combo.itemText(0) == "Income Statement"
        assert widget.report_type_combo.itemText(1) == "Expense Report"

    def test_date_preset_combo_items(self, widget):
        """Test date preset combo has correct items."""
        expected_items = [
            "Custom",
            "This Month",
            "Last Month",
            "This Quarter",
            "Last Quarter",
            "This Year",
            "Last Year",
        ]
        assert widget.date_preset_combo.count() == len(expected_items)
        for i, item in enumerate(expected_items):
            assert widget.date_preset_combo.itemText(i) == item

    def test_format_combo_items(self, widget):
        """Test format combo has correct items."""
        assert widget.format_combo.count() == 3
        assert widget.format_combo.itemText(0) == "PDF"
        assert widget.format_combo.itemText(1) == "CSV"
        assert widget.format_combo.itemText(2) == "JSON"

    def test_generate_button_disabled_without_report_generator(self, qtbot):
        """Test generate button disabled without report generator."""
        widget = ReportsWidget()
        qtbot.addWidget(widget)
        assert not widget.generate_button.isEnabled()

    def test_generate_button_enabled_with_report_generator(self, widget):
        """Test generate button enabled with report generator."""
        assert widget.generate_button.isEnabled()

    def test_export_button_initially_disabled(self, widget):
        """Test export button initially disabled."""
        assert not widget.export_button.isEnabled()

    def test_progress_bar_initially_hidden(self, widget):
        """Test progress bar initially hidden."""
        assert not widget.progress_bar.isVisible()

    def test_preset_this_month(self, widget):
        """Test 'This Month' preset."""
        widget.date_preset_combo.setCurrentText("This Month")

        today = date.today()
        start_expected = today.replace(day=1)

        assert widget.start_date_edit.date().toPython() == start_expected
        assert widget.end_date_edit.date().toPython() == today

    def test_preset_last_month(self, widget):
        """Test 'Last Month' preset."""
        widget.date_preset_combo.setCurrentText("Last Month")

        start = widget.start_date_edit.date().toPython()
        end = widget.end_date_edit.date().toPython()

        # Verify it's the previous month
        today = date.today()
        if today.month == 1:
            assert start.month == 12
            assert start.year == today.year - 1
        else:
            assert start.month == today.month - 1

    def test_preset_this_year(self, widget):
        """Test 'This Year' preset."""
        widget.date_preset_combo.setCurrentText("This Year")

        today = date.today()
        start_expected = today.replace(month=1, day=1)

        assert widget.start_date_edit.date().toPython() == start_expected
        assert widget.end_date_edit.date().toPython() == today

    def test_preset_last_year(self, widget):
        """Test 'Last Year' preset."""
        widget.date_preset_combo.setCurrentText("Last Year")

        today = date.today()
        start_expected = today.replace(year=today.year - 1, month=1, day=1)
        end_expected = today.replace(year=today.year - 1, month=12, day=31)

        assert widget.start_date_edit.date().toPython() == start_expected
        assert widget.end_date_edit.date().toPython() == end_expected

    def test_preset_custom_does_not_change_dates(self, widget):
        """Test 'Custom' preset does not change dates."""
        # Set specific dates
        widget.start_date_edit.setDate(QDate(2025, 1, 1))
        widget.end_date_edit.setDate(QDate(2025, 1, 31))

        original_start = widget.start_date_edit.date()
        original_end = widget.end_date_edit.date()

        # Select Custom
        widget.date_preset_combo.setCurrentText("Custom")

        # Dates should not change
        assert widget.start_date_edit.date() == original_start
        assert widget.end_date_edit.date() == original_end

    def test_validate_inputs_success(self, widget):
        """Test input validation succeeds with valid inputs."""
        widget.start_date_edit.setDate(QDate(2025, 1, 1))
        widget.end_date_edit.setDate(QDate(2025, 1, 31))

        assert widget._validate_inputs() is True

    def test_validate_inputs_start_after_end(self, widget):
        """Test input validation fails when start date after end date."""
        widget.start_date_edit.setDate(QDate(2025, 1, 31))
        widget.end_date_edit.setDate(QDate(2025, 1, 1))

        with patch.object(widget, "_show_error") as mock_error:
            result = widget._validate_inputs()
            assert result is False
            mock_error.assert_called_once()

    def test_validate_inputs_no_report_generator(self, qtbot):
        """Test input validation fails without report generator."""
        widget = ReportsWidget()
        qtbot.addWidget(widget)

        with patch.object(widget, "_show_error") as mock_error:
            result = widget._validate_inputs()
            assert result is False
            mock_error.assert_called_once()

    def test_generate_income_statement(self, widget, sample_report_data):
        """Test generating income statement."""
        widget.report_type_combo.setCurrentText("Income Statement")
        widget.start_date_edit.setDate(QDate(2025, 1, 1))
        widget.end_date_edit.setDate(QDate(2025, 1, 31))

        # Mock report generator
        widget.report_generator.generate_income_statement = Mock(return_value=sample_report_data)

        # Generate report
        widget._on_generate_clicked()

        # Verify report was generated
        widget.report_generator.generate_income_statement.assert_called_once()
        assert widget._current_report_data == sample_report_data
        assert widget.export_button.isEnabled()

    def test_generate_expense_report(self, widget):
        """Test generating expense report."""
        widget.report_type_combo.setCurrentText("Expense Report")
        widget.start_date_edit.setDate(QDate(2025, 1, 1))
        widget.end_date_edit.setDate(QDate(2025, 1, 31))

        # Mock report generator
        expense_data = {
            "metadata": {
                "title": "Expense Report",
                "report_type": "expense_report",
            },
            "summary": {"total_expenses": "$500.00"},
            "categories": [],
        }
        widget.report_generator.generate_expense_report = Mock(return_value=expense_data)

        # Generate report
        widget._on_generate_clicked()

        # Verify report was generated
        widget.report_generator.generate_expense_report.assert_called_once()
        assert widget._current_report_data == expense_data

    def test_generate_report_with_invalid_inputs(self, widget):
        """Test generate report with invalid inputs."""
        widget.start_date_edit.setDate(QDate(2025, 1, 31))
        widget.end_date_edit.setDate(QDate(2025, 1, 1))

        with patch.object(widget, "_show_error"):
            widget._on_generate_clicked()

        # Report should not be generated
        assert widget._current_report_data is None
        assert not widget.export_button.isEnabled()

    def test_generate_report_error_handling(self, widget):
        """Test error handling during report generation."""
        widget.report_generator.generate_income_statement = Mock(
            side_effect=Exception("Test error")
        )

        with patch.object(widget, "_show_error") as mock_error:
            widget._on_generate_clicked()
            mock_error.assert_called_once()

        assert widget._current_report_data is None

    def test_update_preview_income_statement(self, widget, sample_report_data):
        """Test preview update for income statement."""
        widget._update_preview(sample_report_data)

        preview_text = widget.preview_text.toPlainText()

        assert "INCOME STATEMENT" in preview_text
        assert "2025-01-01 to 2025-01-31" in preview_text
        assert "$1,500.00" in preview_text
        assert "$500.00" in preview_text
        assert "$1,000.00" in preview_text

    def test_update_preview_expense_report(self, widget):
        """Test preview update for expense report."""
        expense_data = {
            "metadata": {
                "title": "Expense Report",
                "report_type": "expense_report",
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
                "generated_at": "2025-01-31 12:00:00",
            },
            "summary": {"total_expenses": "$500.00"},
            "categories": [
                {
                    "category": "Office Supplies",
                    "tax_code": "8810",
                    "amount": "$500.00",
                    "percentage": "100.0%",
                }
            ],
        }

        widget._update_preview(expense_data)

        preview_text = widget.preview_text.toPlainText()

        assert "EXPENSE REPORT" in preview_text
        assert "$500.00" in preview_text
        assert "Office Supplies" in preview_text

    @patch("agentic_bookkeeper.gui.reports_widget.QFileDialog.getSaveFileName")
    @patch("agentic_bookkeeper.gui.reports_widget.PDFExporter")
    @patch("agentic_bookkeeper.gui.reports_widget.QMessageBox.information")
    def test_export_pdf(
        self, mock_msgbox, mock_exporter_class, mock_dialog, widget, sample_report_data
    ):
        """Test exporting report to PDF."""
        widget._current_report_data = sample_report_data
        widget.format_combo.setCurrentText("PDF")

        # Mock file dialog
        mock_dialog.return_value = ("/path/to/report.pdf", "PDF Files (*.pdf)")

        # Mock exporter
        mock_exporter = Mock()
        mock_exporter_class.return_value = mock_exporter

        # Export
        widget._on_export_clicked()

        # Verify exporter was created and called
        mock_exporter_class.assert_called_once_with("CRA", "CAD")
        mock_exporter.export.assert_called_once_with(sample_report_data, "/path/to/report.pdf")
        mock_msgbox.assert_called_once()

    @patch("agentic_bookkeeper.gui.reports_widget.QFileDialog.getSaveFileName")
    @patch("agentic_bookkeeper.gui.reports_widget.CSVExporter")
    @patch("agentic_bookkeeper.gui.reports_widget.QMessageBox.information")
    def test_export_csv(
        self, mock_msgbox, mock_exporter_class, mock_dialog, widget, sample_report_data
    ):
        """Test exporting report to CSV."""
        widget._current_report_data = sample_report_data
        widget.format_combo.setCurrentText("CSV")

        # Mock file dialog
        mock_dialog.return_value = ("/path/to/report.csv", "CSV Files (*.csv)")

        # Mock exporter
        mock_exporter = Mock()
        mock_exporter_class.return_value = mock_exporter

        # Export
        widget._on_export_clicked()

        # Verify exporter was created and called
        mock_exporter_class.assert_called_once_with("CRA", "CAD")
        mock_exporter.export.assert_called_once()

    @patch("agentic_bookkeeper.gui.reports_widget.QFileDialog.getSaveFileName")
    @patch("agentic_bookkeeper.gui.reports_widget.JSONExporter")
    @patch("agentic_bookkeeper.gui.reports_widget.QMessageBox.information")
    def test_export_json(
        self, mock_msgbox, mock_exporter_class, mock_dialog, widget, sample_report_data
    ):
        """Test exporting report to JSON."""
        widget._current_report_data = sample_report_data
        widget.format_combo.setCurrentText("JSON")

        # Mock file dialog
        mock_dialog.return_value = ("/path/to/report.json", "JSON Files (*.json)")

        # Mock exporter
        mock_exporter = Mock()
        mock_exporter_class.return_value = mock_exporter

        # Export
        widget._on_export_clicked()

        # Verify exporter was created and called
        mock_exporter_class.assert_called_once_with("CRA", "CAD")
        mock_exporter.export.assert_called_once()

    @patch("agentic_bookkeeper.gui.reports_widget.QFileDialog.getSaveFileName")
    def test_export_cancelled_by_user(self, mock_dialog, widget, sample_report_data):
        """Test export cancelled by user."""
        widget._current_report_data = sample_report_data

        # Mock file dialog to return empty path (cancelled)
        mock_dialog.return_value = ("", "")

        # Export should not proceed
        widget._on_export_clicked()

        # No error should be shown
        # (This is implicitly tested by not patching _show_error)

    def test_export_without_report_data(self, widget):
        """Test export without generating report first."""
        widget._current_report_data = None

        with patch.object(widget, "_show_error") as mock_error:
            widget._on_export_clicked()
            mock_error.assert_called_once()

    @patch("agentic_bookkeeper.gui.reports_widget.QFileDialog.getSaveFileName")
    @patch("agentic_bookkeeper.gui.reports_widget.PDFExporter")
    def test_export_error_handling(
        self, mock_exporter_class, mock_dialog, widget, sample_report_data
    ):
        """Test error handling during export."""
        widget._current_report_data = sample_report_data

        # Mock file dialog
        mock_dialog.return_value = ("/path/to/report.pdf", "PDF Files (*.pdf)")

        # Mock exporter to raise error
        mock_exporter = Mock()
        mock_exporter.export.side_effect = Exception("Export error")
        mock_exporter_class.return_value = mock_exporter

        with patch.object(widget, "_show_error") as mock_error:
            widget._on_export_clicked()
            mock_error.assert_called_once()

    def test_show_progress(self, widget, qtbot):
        """Test showing progress indicator."""
        from PySide6.QtWidgets import QApplication

        # Show the widget so visibility changes work
        widget.show()
        qtbot.waitExposed(widget)

        widget._show_progress("Testing...")

        # Process Qt events to ensure UI updates
        QApplication.processEvents()

        assert widget.progress_bar.isVisible()
        assert not widget.generate_button.isEnabled()
        assert not widget.export_button.isEnabled()

    def test_hide_progress(self, widget):
        """Test hiding progress indicator."""
        widget._show_progress("Testing...")
        widget._hide_progress()

        assert not widget.progress_bar.isVisible()
        assert widget.generate_button.isEnabled()

    def test_hide_progress_with_report_data(self, widget, sample_report_data):
        """Test hiding progress with report data enables export."""
        widget._current_report_data = sample_report_data
        widget._show_progress("Testing...")
        widget._hide_progress()

        assert widget.export_button.isEnabled()

    def test_get_default_filename(self, widget):
        """Test default filename generation."""
        widget.report_type_combo.setCurrentText("Income Statement")

        filename = widget._get_default_filename("PDF")

        assert "income_statement" in filename
        assert filename.endswith(".pdf")

    def test_signals_emitted(self, widget, qtbot, sample_report_data):
        """Test signals are emitted correctly."""
        # Mock report generator
        widget.report_generator.generate_income_statement = Mock(return_value=sample_report_data)

        # Connect signal spy
        with qtbot.waitSignal(widget.report_generated, timeout=1000):
            widget._on_generate_clicked()

    @patch("agentic_bookkeeper.gui.reports_widget.QFileDialog.getSaveFileName")
    @patch("agentic_bookkeeper.gui.reports_widget.PDFExporter")
    @patch("agentic_bookkeeper.gui.reports_widget.QMessageBox.information")
    def test_export_signal_emitted(
        self, mock_msgbox, mock_exporter_class, mock_dialog, widget, qtbot, sample_report_data
    ):
        """Test export signal is emitted."""
        widget._current_report_data = sample_report_data

        # Mock file dialog and exporter
        mock_dialog.return_value = ("/path/to/report.pdf", "PDF Files (*.pdf)")
        mock_exporter = Mock()
        mock_exporter_class.return_value = mock_exporter

        # Connect signal spy
        with qtbot.waitSignal(widget.export_completed, timeout=1000):
            widget._on_export_clicked()
