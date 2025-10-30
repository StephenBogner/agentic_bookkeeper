"""
Module: test_exporters
Purpose: Test suite for report exporters (PDF, CSV, JSON)
Author: Stephen Bogner
Created: 2025-10-29
"""

import pytest
import os
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from pypdf import PdfReader
import pandas as pd

from agentic_bookkeeper.core.exporters.pdf_exporter import PDFExporter
from agentic_bookkeeper.core.exporters.csv_exporter import CSVExporter
from agentic_bookkeeper.core.exporters.json_exporter import JSONExporter
import json


class TestPDFExporter:
    """Test suite for PDFExporter class."""

    @pytest.fixture
    def exporter(self):
        """Create PDFExporter instance."""
        return PDFExporter(jurisdiction="IRS", currency="USD")

    @pytest.fixture
    def cra_exporter(self):
        """Create PDFExporter instance for CRA."""
        return PDFExporter(jurisdiction="CRA", currency="CAD")

    @pytest.fixture
    def income_statement_data(self):
        """Sample income statement data."""
        return {
            "metadata": {
                "report_type": "income_statement",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "generated_at": "2024-12-31 23:59:59",
                "jurisdiction": "IRS",
                "currency": "USD",
            },
            "summary": {
                "total_revenue": Decimal("50000.00"),
                "total_expenses": Decimal("30000.00"),
                "net_income": Decimal("20000.00"),
            },
            "details": {
                "revenue": [
                    {"category": "Services", "total": Decimal("40000.00"), "percentage": 80.0},
                    {"category": "Products", "total": Decimal("10000.00"), "percentage": 20.0},
                ],
                "expenses": [
                    {"category": "Office", "total": Decimal("15000.00"), "percentage": 50.0},
                    {"category": "Travel", "total": Decimal("10000.00"), "percentage": 33.3},
                    {"category": "Utilities", "total": Decimal("5000.00"), "percentage": 16.7},
                ],
            },
        }

    @pytest.fixture
    def expense_report_data(self):
        """Sample expense report data."""
        return {
            "metadata": {
                "report_type": "expense_report",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "generated_at": "2024-12-31 23:59:59",
                "jurisdiction": "IRS",
                "currency": "USD",
            },
            "summary": {
                "total_expenses": Decimal("30000.00"),
                "category_count": 3,
                "transaction_count": 25,
            },
            "details": {
                "expenses": [
                    {
                        "category": "Office",
                        "total": Decimal("15000.00"),
                        "percentage": 50.0,
                        "tax_code": "8810",
                    },
                    {
                        "category": "Travel",
                        "total": Decimal("10000.00"),
                        "percentage": 33.3,
                        "tax_code": "8520",
                    },
                    {
                        "category": "Utilities",
                        "total": Decimal("5000.00"),
                        "percentage": 16.7,
                        "tax_code": "8804",
                    },
                ]
            },
        }

    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Create temporary output directory."""
        output_dir = tmp_path / "reports"
        output_dir.mkdir()
        return output_dir

    # Initialization tests

    def test_init_success(self):
        """Test successful initialization."""
        exporter = PDFExporter(jurisdiction="IRS", currency="USD")
        assert exporter.jurisdiction == "IRS"
        assert exporter.currency == "USD"

    def test_init_cra_jurisdiction(self):
        """Test initialization with CRA jurisdiction."""
        exporter = PDFExporter(jurisdiction="CRA", currency="CAD")
        assert exporter.jurisdiction == "CRA"
        assert exporter.currency == "CAD"

    def test_init_invalid_jurisdiction(self):
        """Test initialization with invalid jurisdiction raises ValueError."""
        with pytest.raises(ValueError, match="Invalid jurisdiction"):
            PDFExporter(jurisdiction="INVALID")

    def test_init_invalid_currency(self):
        """Test initialization with invalid currency raises ValueError."""
        with pytest.raises(ValueError, match="Invalid currency"):
            PDFExporter(jurisdiction="IRS", currency="EUR")

    # Export method tests

    def test_export_income_statement_creates_file(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test export creates PDF file for income statement."""
        output_path = temp_output_dir / "income_statement.pdf"
        exporter.export(income_statement_data, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_export_expense_report_creates_file(
        self, exporter, expense_report_data, temp_output_dir
    ):
        """Test export creates PDF file for expense report."""
        output_path = temp_output_dir / "expense_report.pdf"
        exporter.export(expense_report_data, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_export_invalid_report_data_type(self, exporter, temp_output_dir):
        """Test export with non-dict report_data raises TypeError."""
        output_path = temp_output_dir / "report.pdf"
        with pytest.raises(TypeError, match="Expected dict"):
            exporter.export("not a dict", str(output_path))

    def test_export_missing_metadata(self, exporter, temp_output_dir):
        """Test export with missing metadata raises ValueError."""
        output_path = temp_output_dir / "report.pdf"
        invalid_data = {"summary": {}}
        with pytest.raises(ValueError, match="missing required field: metadata"):
            exporter.export(invalid_data, str(output_path))

    def test_export_missing_summary(self, exporter, temp_output_dir):
        """Test export with missing summary raises ValueError."""
        output_path = temp_output_dir / "report.pdf"
        invalid_data = {"metadata": {}}
        with pytest.raises(ValueError, match="missing required field: summary"):
            exporter.export(invalid_data, str(output_path))

    def test_export_nonexistent_directory(self, exporter, income_statement_data):
        """Test export to nonexistent directory raises IOError."""
        output_path = "/nonexistent/directory/report.pdf"
        with pytest.raises(IOError, match="Output directory does not exist"):
            exporter.export(income_statement_data, output_path)

    def test_export_unsupported_report_type(self, exporter, temp_output_dir):
        """Test export with unsupported report type raises ValueError."""
        output_path = temp_output_dir / "report.pdf"
        invalid_data = {"metadata": {"report_type": "unsupported_type"}, "summary": {}}
        with pytest.raises(ValueError, match="Unsupported report type"):
            exporter.export(invalid_data, str(output_path))

    # PDF content verification tests

    def test_income_statement_pdf_contains_title(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test income statement PDF contains correct title."""
        output_path = temp_output_dir / "income_statement.pdf"
        exporter.export(income_statement_data, str(output_path))

        # Read PDF and verify title is present
        reader = PdfReader(str(output_path))
        page_text = reader.pages[0].extract_text()
        assert "Income Statement" in page_text

    def test_income_statement_pdf_contains_date_range(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test income statement PDF contains date range."""
        output_path = temp_output_dir / "income_statement.pdf"
        exporter.export(income_statement_data, str(output_path))

        reader = PdfReader(str(output_path))
        page_text = reader.pages[0].extract_text()
        assert "2024-01-01" in page_text
        assert "2024-12-31" in page_text

    def test_income_statement_pdf_contains_summary(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test income statement PDF contains summary data."""
        output_path = temp_output_dir / "income_statement.pdf"
        exporter.export(income_statement_data, str(output_path))

        reader = PdfReader(str(output_path))
        page_text = reader.pages[0].extract_text()
        assert "Total Revenue" in page_text
        assert "Total Expenses" in page_text
        assert "Net Income" in page_text
        assert "50,000.00" in page_text
        assert "30,000.00" in page_text
        assert "20,000.00" in page_text

    def test_expense_report_pdf_contains_title(
        self, exporter, expense_report_data, temp_output_dir
    ):
        """Test expense report PDF contains correct title."""
        output_path = temp_output_dir / "expense_report.pdf"
        exporter.export(expense_report_data, str(output_path))

        reader = PdfReader(str(output_path))
        page_text = reader.pages[0].extract_text()
        assert "Expense Report" in page_text

    def test_expense_report_pdf_contains_tax_codes(
        self, exporter, expense_report_data, temp_output_dir
    ):
        """Test expense report PDF contains tax codes."""
        output_path = temp_output_dir / "expense_report.pdf"
        exporter.export(expense_report_data, str(output_path))

        reader = PdfReader(str(output_path))
        page_text = reader.pages[0].extract_text()
        assert "Tax Code" in page_text
        assert "8810" in page_text
        assert "8520" in page_text
        assert "8804" in page_text

    def test_pdf_contains_jurisdiction(self, exporter, income_statement_data, temp_output_dir):
        """Test PDF contains jurisdiction label."""
        output_path = temp_output_dir / "report.pdf"
        exporter.export(income_statement_data, str(output_path))

        reader = PdfReader(str(output_path))
        page_text = reader.pages[0].extract_text()
        assert "IRS" in page_text

    def test_cra_pdf_contains_cra_jurisdiction(
        self, cra_exporter, income_statement_data, temp_output_dir
    ):
        """Test CRA exporter creates PDF with CRA jurisdiction."""
        # Update test data for CRA
        income_statement_data["metadata"]["jurisdiction"] = "CRA"
        income_statement_data["metadata"]["currency"] = "CAD"

        output_path = temp_output_dir / "cra_report.pdf"
        cra_exporter.export(income_statement_data, str(output_path))

        reader = PdfReader(str(output_path))
        page_text = reader.pages[0].extract_text()
        assert "CRA" in page_text

    def test_pdf_contains_generation_timestamp(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test PDF contains generation timestamp."""
        output_path = temp_output_dir / "report.pdf"
        exporter.export(income_statement_data, str(output_path))

        reader = PdfReader(str(output_path))
        page_text = reader.pages[0].extract_text()
        assert "Generated" in page_text

    # Multi-page tests

    def test_multipage_report_has_page_numbers(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test multi-page report has page numbers on each page."""
        # Create large dataset to force multiple pages
        large_expenses = []
        for i in range(50):
            large_expenses.append(
                {"category": f"Category{i}", "total": Decimal("1000.00"), "percentage": 2.0}
            )
        income_statement_data["details"]["expenses"] = large_expenses

        output_path = temp_output_dir / "multipage_report.pdf"
        exporter.export(income_statement_data, str(output_path))

        reader = PdfReader(str(output_path))
        # Should have multiple pages
        assert len(reader.pages) > 1

        # Check page numbers exist on multiple pages
        for page_num in range(len(reader.pages)):
            page_text = reader.pages[page_num].extract_text()
            assert "Page" in page_text

    # Currency formatting tests

    def test_format_currency_positive(self, exporter):
        """Test currency formatting for positive amounts."""
        result = exporter._format_currency(Decimal("1234.56"))
        assert result == "$1,234.56"

    def test_format_currency_negative(self, exporter):
        """Test currency formatting for negative amounts."""
        result = exporter._format_currency(Decimal("-1234.56"))
        assert result == "-$1,234.56"

    def test_format_currency_zero(self, exporter):
        """Test currency formatting for zero."""
        result = exporter._format_currency(Decimal("0.00"))
        assert result == "$0.00"

    def test_format_currency_large_amount(self, exporter):
        """Test currency formatting for large amounts."""
        result = exporter._format_currency(Decimal("1234567.89"))
        assert result == "$1,234,567.89"

    def test_format_currency_from_float(self, exporter):
        """Test currency formatting converts float to Decimal."""
        result = exporter._format_currency(1234.56)
        assert result == "$1,234.56"

    # Integration tests

    def test_export_multiple_reports_same_directory(
        self, exporter, income_statement_data, expense_report_data, temp_output_dir
    ):
        """Test exporting multiple reports to same directory."""
        income_path = temp_output_dir / "income.pdf"
        expense_path = temp_output_dir / "expense.pdf"

        exporter.export(income_statement_data, str(income_path))
        exporter.export(expense_report_data, str(expense_path))

        assert income_path.exists()
        assert expense_path.exists()
        assert income_path.stat().st_size > 0
        assert expense_path.stat().st_size > 0

    def test_export_overwrites_existing_file(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test export overwrites existing PDF file."""
        output_path = temp_output_dir / "report.pdf"

        # Create first export
        exporter.export(income_statement_data, str(output_path))
        first_size = output_path.stat().st_size

        # Create second export
        exporter.export(income_statement_data, str(output_path))
        second_size = output_path.stat().st_size

        # File should still exist and have content
        assert output_path.exists()
        assert second_size > 0

    def test_export_with_empty_details(self, exporter, income_statement_data, temp_output_dir):
        """Test export handles missing detail sections gracefully."""
        # Remove details section
        income_statement_data["details"] = {}

        output_path = temp_output_dir / "report.pdf"
        exporter.export(income_statement_data, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_export_with_no_revenue_details(self, exporter, income_statement_data, temp_output_dir):
        """Test export handles missing revenue details."""
        # Remove revenue details
        del income_statement_data["details"]["revenue"]

        output_path = temp_output_dir / "report.pdf"
        exporter.export(income_statement_data, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_export_with_no_expense_details(self, exporter, income_statement_data, temp_output_dir):
        """Test export handles missing expense details."""
        # Remove expense details
        del income_statement_data["details"]["expenses"]

        output_path = temp_output_dir / "report.pdf"
        exporter.export(income_statement_data, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0


class TestCSVExporter:
    """Test suite for CSVExporter class."""

    @pytest.fixture
    def exporter(self):
        """Create CSVExporter instance."""
        return CSVExporter(jurisdiction="IRS", currency="USD")

    @pytest.fixture
    def cra_exporter(self):
        """Create CSVExporter instance for CRA."""
        return CSVExporter(jurisdiction="CRA", currency="CAD")

    @pytest.fixture
    def income_statement_data(self):
        """Sample income statement data."""
        return {
            "metadata": {
                "report_type": "income_statement",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "generated_at": "2024-12-31 23:59:59",
                "jurisdiction": "IRS",
                "currency": "USD",
            },
            "summary": {
                "total_revenue": Decimal("50000.00"),
                "total_expenses": Decimal("30000.00"),
                "net_income": Decimal("20000.00"),
            },
            "details": {
                "revenue": [
                    {"category": "Services", "total": Decimal("40000.00"), "percentage": 80.0},
                    {"category": "Products", "total": Decimal("10000.00"), "percentage": 20.0},
                ],
                "expenses": [
                    {"category": "Office", "total": Decimal("15000.00"), "percentage": 50.0},
                    {"category": "Travel", "total": Decimal("10000.00"), "percentage": 33.3},
                    {"category": "Utilities", "total": Decimal("5000.00"), "percentage": 16.7},
                ],
            },
        }

    @pytest.fixture
    def expense_report_data(self):
        """Sample expense report data."""
        return {
            "metadata": {
                "report_type": "expense_report",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "generated_at": "2024-12-31 23:59:59",
                "jurisdiction": "IRS",
                "currency": "USD",
            },
            "summary": {
                "total_expenses": Decimal("30000.00"),
                "category_count": 3,
                "transaction_count": 25,
            },
            "details": {
                "expenses": [
                    {
                        "category": "Office",
                        "total": Decimal("15000.00"),
                        "percentage": 50.0,
                        "tax_code": "8810",
                    },
                    {
                        "category": "Travel",
                        "total": Decimal("10000.00"),
                        "percentage": 33.3,
                        "tax_code": "8520",
                    },
                    {
                        "category": "Utilities",
                        "total": Decimal("5000.00"),
                        "percentage": 16.7,
                        "tax_code": "8804",
                    },
                ]
            },
        }

    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Create temporary output directory."""
        output_dir = tmp_path / "reports"
        output_dir.mkdir()
        return output_dir

    # Initialization tests

    def test_init_success(self):
        """Test successful initialization."""
        exporter = CSVExporter(jurisdiction="IRS", currency="USD")
        assert exporter.jurisdiction == "IRS"
        assert exporter.currency == "USD"

    def test_init_cra_jurisdiction(self):
        """Test initialization with CRA jurisdiction."""
        exporter = CSVExporter(jurisdiction="CRA", currency="CAD")
        assert exporter.jurisdiction == "CRA"
        assert exporter.currency == "CAD"

    def test_init_invalid_jurisdiction(self):
        """Test initialization with invalid jurisdiction raises ValueError."""
        with pytest.raises(ValueError, match="Invalid jurisdiction"):
            CSVExporter(jurisdiction="INVALID")

    def test_init_invalid_currency(self):
        """Test initialization with invalid currency raises ValueError."""
        with pytest.raises(ValueError, match="Invalid currency"):
            CSVExporter(jurisdiction="IRS", currency="EUR")

    # Export method tests

    def test_export_income_statement_creates_file(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test export creates CSV file for income statement."""
        output_path = temp_output_dir / "income_statement.csv"
        exporter.export(income_statement_data, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_export_expense_report_creates_file(
        self, exporter, expense_report_data, temp_output_dir
    ):
        """Test export creates CSV file for expense report."""
        output_path = temp_output_dir / "expense_report.csv"
        exporter.export(expense_report_data, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_export_invalid_report_data_type(self, exporter, temp_output_dir):
        """Test export with non-dict report_data raises TypeError."""
        output_path = temp_output_dir / "report.csv"
        with pytest.raises(TypeError, match="Expected dict"):
            exporter.export("not a dict", str(output_path))

    def test_export_missing_metadata(self, exporter, temp_output_dir):
        """Test export with missing metadata raises ValueError."""
        output_path = temp_output_dir / "report.csv"
        invalid_data = {"summary": {}}
        with pytest.raises(ValueError, match="missing required field: metadata"):
            exporter.export(invalid_data, str(output_path))

    def test_export_missing_summary(self, exporter, temp_output_dir):
        """Test export with missing summary raises ValueError."""
        output_path = temp_output_dir / "report.csv"
        invalid_data = {"metadata": {}}
        with pytest.raises(ValueError, match="missing required field: summary"):
            exporter.export(invalid_data, str(output_path))

    def test_export_nonexistent_directory(self, exporter, income_statement_data):
        """Test export to nonexistent directory raises IOError."""
        output_path = "/nonexistent/directory/report.csv"
        with pytest.raises(IOError, match="Output directory does not exist"):
            exporter.export(income_statement_data, output_path)

    def test_export_unsupported_report_type(self, exporter, temp_output_dir):
        """Test export with unsupported report type raises ValueError."""
        output_path = temp_output_dir / "report.csv"
        invalid_data = {"metadata": {"report_type": "unsupported_type"}, "summary": {}}
        with pytest.raises(ValueError, match="Unsupported report type"):
            exporter.export(invalid_data, str(output_path))

    # CSV content verification tests

    def test_income_statement_csv_has_correct_headers(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test income statement CSV has correct column headers."""
        output_path = temp_output_dir / "income_statement.csv"
        exporter.export(income_statement_data, str(output_path))

        df = pd.read_csv(str(output_path))
        assert "Section" in df.columns
        assert "Category" in df.columns
        assert "Amount" in df.columns
        assert "Percentage" in df.columns

    def test_income_statement_csv_contains_summary_data(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test income statement CSV contains summary section."""
        output_path = temp_output_dir / "income_statement.csv"
        exporter.export(income_statement_data, str(output_path))

        df = pd.read_csv(str(output_path))
        # Check for summary data
        assert any(df["Category"] == "Total Revenue")
        assert any(df["Category"] == "Total Expenses")
        assert any(df["Category"] == "Net Income")

    def test_income_statement_csv_contains_revenue_details(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test income statement CSV contains revenue breakdown."""
        output_path = temp_output_dir / "income_statement.csv"
        exporter.export(income_statement_data, str(output_path))

        df = pd.read_csv(str(output_path))
        # Check for revenue categories
        assert any(df["Category"] == "Services")
        assert any(df["Category"] == "Products")

    def test_expense_report_csv_has_tax_code_column(
        self, exporter, expense_report_data, temp_output_dir
    ):
        """Test expense report CSV has Tax Code column."""
        output_path = temp_output_dir / "expense_report.csv"
        exporter.export(expense_report_data, str(output_path))

        df = pd.read_csv(str(output_path))
        assert "Tax Code" in df.columns

    def test_expense_report_csv_contains_tax_codes(
        self, exporter, expense_report_data, temp_output_dir
    ):
        """Test expense report CSV contains tax codes."""
        output_path = temp_output_dir / "expense_report.csv"
        exporter.export(expense_report_data, str(output_path))

        df = pd.read_csv(str(output_path))
        csv_text = df.to_string()
        assert "8810" in csv_text
        assert "8520" in csv_text
        assert "8804" in csv_text

    def test_csv_currency_formatting(self, exporter, income_statement_data, temp_output_dir):
        """Test CSV contains properly formatted currency values."""
        output_path = temp_output_dir / "income_statement.csv"
        exporter.export(income_statement_data, str(output_path))

        df = pd.read_csv(str(output_path))
        csv_text = df.to_string()
        assert "$50,000.00" in csv_text
        assert "$30,000.00" in csv_text
        assert "$20,000.00" in csv_text

    def test_csv_percentage_formatting(self, exporter, income_statement_data, temp_output_dir):
        """Test CSV contains properly formatted percentage values."""
        output_path = temp_output_dir / "income_statement.csv"
        exporter.export(income_statement_data, str(output_path))

        df = pd.read_csv(str(output_path))
        csv_text = df.to_string()
        assert "80.0%" in csv_text
        assert "20.0%" in csv_text

    def test_csv_contains_metadata(self, exporter, income_statement_data, temp_output_dir):
        """Test CSV contains metadata section."""
        output_path = temp_output_dir / "income_statement.csv"
        exporter.export(income_statement_data, str(output_path))

        df = pd.read_csv(str(output_path))
        # Check for metadata rows
        assert any(df["Category"] == "Report Type")
        assert any(df["Category"] == "Date Range")
        assert any(df["Category"] == "Jurisdiction")
        assert any(df["Category"] == "Currency")

    # DataFrame structure tests

    def test_income_statement_dataframe_structure(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test income statement DataFrame has proper structure."""
        output_path = temp_output_dir / "income_statement.csv"
        exporter.export(income_statement_data, str(output_path))

        df = pd.read_csv(str(output_path))
        assert len(df.columns) == 4
        assert df.shape[0] > 10  # Should have multiple rows

    def test_expense_report_dataframe_structure(
        self, exporter, expense_report_data, temp_output_dir
    ):
        """Test expense report DataFrame has proper structure."""
        output_path = temp_output_dir / "expense_report.csv"
        exporter.export(expense_report_data, str(output_path))

        df = pd.read_csv(str(output_path))
        assert len(df.columns) == 5  # Has Tax Code column
        assert df.shape[0] > 10  # Should have multiple rows

    def test_csv_handles_special_characters(self, exporter, income_statement_data, temp_output_dir):
        """Test CSV handles special characters in category names."""
        # Add category with special characters
        income_statement_data["details"]["revenue"].append(
            {"category": "Consulting & Advice", "total": Decimal("5000.00"), "percentage": 10.0}
        )

        output_path = temp_output_dir / "income_statement.csv"
        exporter.export(income_statement_data, str(output_path))

        df = pd.read_csv(str(output_path))
        assert any(df["Category"] == "Consulting & Advice")

    def test_csv_handles_formula_injection(self, exporter, income_statement_data, temp_output_dir):
        """Test CSV escapes potential Excel formula injection."""
        # Add category starting with =
        income_statement_data["details"]["revenue"].append(
            {"category": "=SUM(A1:A10)", "total": Decimal("1000.00"), "percentage": 2.0}
        )

        output_path = temp_output_dir / "income_statement.csv"
        exporter.export(income_statement_data, str(output_path))

        # Read raw CSV to check escaping
        with open(output_path, "r", encoding="utf-8-sig") as f:
            content = f.read()
            assert "'=SUM(A1:A10)" in content

    def test_csv_section_organization(self, exporter, income_statement_data, temp_output_dir):
        """Test CSV is properly organized into sections."""
        output_path = temp_output_dir / "income_statement.csv"
        exporter.export(income_statement_data, str(output_path))

        df = pd.read_csv(str(output_path))
        sections = df["Section"].unique()
        assert "Metadata" in sections
        assert "Summary" in sections
        assert "Revenue Details" in sections
        assert "Expense Details" in sections

    # Integration tests

    def test_export_multiple_reports_same_directory(
        self, exporter, income_statement_data, expense_report_data, temp_output_dir
    ):
        """Test exporting multiple reports to same directory."""
        income_path = temp_output_dir / "income.csv"
        expense_path = temp_output_dir / "expense.csv"

        exporter.export(income_statement_data, str(income_path))
        exporter.export(expense_report_data, str(expense_path))

        assert income_path.exists()
        assert expense_path.exists()
        assert income_path.stat().st_size > 0
        assert expense_path.stat().st_size > 0

    def test_export_overwrites_existing_file(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test export overwrites existing CSV file."""
        output_path = temp_output_dir / "report.csv"

        # Create first export
        exporter.export(income_statement_data, str(output_path))
        first_size = output_path.stat().st_size

        # Create second export
        exporter.export(income_statement_data, str(output_path))
        second_size = output_path.stat().st_size

        # File should still exist and have content
        assert output_path.exists()
        assert second_size > 0

    def test_export_with_empty_details(self, exporter, income_statement_data, temp_output_dir):
        """Test export handles missing detail sections gracefully."""
        # Remove details section
        income_statement_data["details"] = {}

        output_path = temp_output_dir / "report.csv"
        exporter.export(income_statement_data, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_export_with_no_revenue_details(self, exporter, income_statement_data, temp_output_dir):
        """Test export handles missing revenue details."""
        # Remove revenue details
        del income_statement_data["details"]["revenue"]

        output_path = temp_output_dir / "report.csv"
        exporter.export(income_statement_data, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_export_with_no_expense_details(self, exporter, income_statement_data, temp_output_dir):
        """Test export handles missing expense details."""
        # Remove expense details
        del income_statement_data["details"]["expenses"]

        output_path = temp_output_dir / "report.csv"
        exporter.export(income_statement_data, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_large_dataset_export(self, exporter, income_statement_data, temp_output_dir):
        """Test export handles large datasets."""
        # Create large dataset
        large_expenses = []
        for i in range(100):
            large_expenses.append(
                {"category": f"Category{i}", "total": Decimal("1000.00"), "percentage": 1.0}
            )
        income_statement_data["details"]["expenses"] = large_expenses

        output_path = temp_output_dir / "large_report.csv"
        exporter.export(income_statement_data, str(output_path))

        assert output_path.exists()
        df = pd.read_csv(str(output_path))
        assert df.shape[0] > 100  # Should have many rows

    # Currency formatting tests

    def test_format_currency_positive(self, exporter):
        """Test currency formatting for positive amounts."""
        result = exporter._format_currency(Decimal("1234.56"))
        assert result == "$1,234.56"

    def test_format_currency_negative(self, exporter):
        """Test currency formatting for negative amounts."""
        result = exporter._format_currency(Decimal("-1234.56"))
        assert result == "-$1,234.56"

    def test_format_currency_zero(self, exporter):
        """Test currency formatting for zero."""
        result = exporter._format_currency(Decimal("0.00"))
        assert result == "$0.00"

    def test_format_currency_large_amount(self, exporter):
        """Test currency formatting for large amounts."""
        result = exporter._format_currency(Decimal("1234567.89"))
        assert result == "$1,234,567.89"

    # Special character handling tests

    def test_escape_special_characters_normal_text(self, exporter):
        """Test escaping normal text returns unchanged."""
        result = exporter._escape_special_characters("Normal Text")
        assert result == "Normal Text"

    def test_escape_special_characters_formula(self, exporter):
        """Test escaping text starting with = adds quote."""
        result = exporter._escape_special_characters("=SUM(A1:A10)")
        assert result == "'=SUM(A1:A10)"

    def test_escape_special_characters_converts_non_string(self, exporter):
        """Test escaping converts non-string to string."""
        result = exporter._escape_special_characters(123)
        assert result == "123"


class TestJSONExporter:
    """Test suite for JSONExporter class."""

    @pytest.fixture
    def exporter(self):
        """Create JSONExporter instance."""
        return JSONExporter(jurisdiction="IRS", currency="USD")

    @pytest.fixture
    def cra_exporter(self):
        """Create JSONExporter instance for CRA."""
        return JSONExporter(jurisdiction="CRA", currency="CAD")

    @pytest.fixture
    def income_statement_data(self):
        """Sample income statement data."""
        return {
            "metadata": {
                "report_type": "income_statement",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "generated_at": "2024-12-31 23:59:59",
                "jurisdiction": "IRS",
                "currency": "USD",
            },
            "summary": {
                "total_revenue": Decimal("50000.00"),
                "total_expenses": Decimal("30000.00"),
                "net_income": Decimal("20000.00"),
            },
            "details": {
                "revenue": [
                    {"category": "Services", "total": Decimal("40000.00"), "percentage": 80.0},
                    {"category": "Products", "total": Decimal("10000.00"), "percentage": 20.0},
                ],
                "expenses": [
                    {"category": "Office", "total": Decimal("15000.00"), "percentage": 50.0},
                    {"category": "Travel", "total": Decimal("10000.00"), "percentage": 33.3},
                    {"category": "Utilities", "total": Decimal("5000.00"), "percentage": 16.7},
                ],
            },
        }

    @pytest.fixture
    def expense_report_data(self):
        """Sample expense report data."""
        return {
            "metadata": {
                "report_type": "expense_report",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "generated_at": "2024-12-31 23:59:59",
                "jurisdiction": "IRS",
                "currency": "USD",
            },
            "summary": {
                "total_expenses": Decimal("30000.00"),
                "category_count": 3,
                "transaction_count": 25,
            },
            "details": {
                "expenses": [
                    {
                        "category": "Office",
                        "total": Decimal("15000.00"),
                        "percentage": 50.0,
                        "tax_code": "8810",
                    },
                    {
                        "category": "Travel",
                        "total": Decimal("10000.00"),
                        "percentage": 33.3,
                        "tax_code": "8520",
                    },
                    {
                        "category": "Utilities",
                        "total": Decimal("5000.00"),
                        "percentage": 16.7,
                        "tax_code": "8804",
                    },
                ]
            },
        }

    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Create temporary output directory."""
        output_dir = tmp_path / "json_output"
        output_dir.mkdir()
        return output_dir

    # Initialization tests

    def test_init_default_values(self):
        """Test initialization with default values."""
        exporter = JSONExporter()
        assert exporter.jurisdiction == "IRS"
        assert exporter.currency == "USD"

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        exporter = JSONExporter(jurisdiction="CRA", currency="CAD")
        assert exporter.jurisdiction == "CRA"
        assert exporter.currency == "CAD"

    def test_init_invalid_jurisdiction(self):
        """Test initialization with invalid jurisdiction raises ValueError."""
        with pytest.raises(ValueError, match="Invalid jurisdiction"):
            JSONExporter(jurisdiction="INVALID")

    def test_init_invalid_currency(self):
        """Test initialization with invalid currency raises ValueError."""
        with pytest.raises(ValueError, match="Invalid currency"):
            JSONExporter(jurisdiction="IRS", currency="EUR")

    def test_schema_version_exists(self):
        """Test schema version class attribute exists."""
        assert hasattr(JSONExporter, "SCHEMA_VERSION")
        assert JSONExporter.SCHEMA_VERSION == "1.0"

    # Export method tests

    def test_export_income_statement_creates_file(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test export creates JSON file for income statement."""
        output_path = temp_output_dir / "income_statement.json"
        exporter.export(income_statement_data, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_export_expense_report_creates_file(
        self, exporter, expense_report_data, temp_output_dir
    ):
        """Test export creates JSON file for expense report."""
        output_path = temp_output_dir / "expense_report.json"
        exporter.export(expense_report_data, str(output_path))

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_export_invalid_report_data_type(self, exporter, temp_output_dir):
        """Test export with non-dict report_data raises TypeError."""
        output_path = temp_output_dir / "report.json"
        with pytest.raises(TypeError, match="Expected dict"):
            exporter.export("not a dict", str(output_path))

    def test_export_missing_metadata(self, exporter, temp_output_dir):
        """Test export with missing metadata raises ValueError."""
        output_path = temp_output_dir / "report.json"
        invalid_data = {"summary": {}}
        with pytest.raises(ValueError, match="missing required field: metadata"):
            exporter.export(invalid_data, str(output_path))

    def test_export_missing_summary(self, exporter, temp_output_dir):
        """Test export with missing summary raises ValueError."""
        output_path = temp_output_dir / "report.json"
        invalid_data = {"metadata": {}}
        with pytest.raises(ValueError, match="missing required field: summary"):
            exporter.export(invalid_data, str(output_path))

    def test_export_nonexistent_directory(self, exporter, income_statement_data):
        """Test export to nonexistent directory raises IOError."""
        output_path = "/nonexistent/directory/report.json"
        with pytest.raises(IOError, match="Output directory does not exist"):
            exporter.export(income_statement_data, output_path)

    def test_export_unsupported_report_type(self, exporter, temp_output_dir):
        """Test export with unsupported report type raises ValueError."""
        output_path = temp_output_dir / "report.json"
        invalid_data = {"metadata": {"report_type": "unsupported_type"}, "summary": {}}
        with pytest.raises(ValueError, match="Unsupported report type"):
            exporter.export(invalid_data, str(output_path))

    # JSON validity tests

    def test_export_creates_valid_json(self, exporter, income_statement_data, temp_output_dir):
        """Test exported file contains valid JSON."""
        output_path = temp_output_dir / "income_statement.json"
        exporter.export(income_statement_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)  # Will raise if invalid JSON
            assert isinstance(data, dict)

    def test_export_pretty_print_default(self, exporter, income_statement_data, temp_output_dir):
        """Test export with pretty printing by default."""
        output_path = temp_output_dir / "income_statement.json"
        exporter.export(income_statement_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Pretty-printed JSON should have newlines and indentation
            assert "\n" in content
            assert "  " in content  # Check for indentation

    def test_export_compact_json(self, exporter, income_statement_data, temp_output_dir):
        """Test export with compact formatting."""
        output_path = temp_output_dir / "income_statement.json"
        exporter.export(income_statement_data, str(output_path), pretty=False)

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert isinstance(data, dict)
            # Compact JSON should be on one line (mostly)
            content = f.read()
            # Reset file pointer after reading
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Compact has fewer newlines
            newline_count = content.count("\n")
            assert newline_count < 10

    # Income statement JSON structure tests

    def test_income_statement_json_has_schema_version(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test income statement JSON includes schema version."""
        output_path = temp_output_dir / "income_statement.json"
        exporter.export(income_statement_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "schema_version" in data
            assert data["schema_version"] == "1.0"

    def test_income_statement_json_has_report_type(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test income statement JSON includes report type."""
        output_path = temp_output_dir / "income_statement.json"
        exporter.export(income_statement_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["report_type"] == "income_statement"

    def test_income_statement_json_has_metadata(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test income statement JSON includes metadata section."""
        output_path = temp_output_dir / "income_statement.json"
        exporter.export(income_statement_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "metadata" in data
            metadata = data["metadata"]
            assert "generated_at" in metadata
            assert "start_date" in metadata
            assert "end_date" in metadata
            assert "jurisdiction" in metadata
            assert "currency" in metadata

    def test_income_statement_json_has_summary(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test income statement JSON includes summary section."""
        output_path = temp_output_dir / "income_statement.json"
        exporter.export(income_statement_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "summary" in data
            summary = data["summary"]
            assert "total_revenue" in summary
            assert "total_expenses" in summary
            assert "net_income" in summary

    def test_income_statement_json_has_details(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test income statement JSON includes details section."""
        output_path = temp_output_dir / "income_statement.json"
        exporter.export(income_statement_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "details" in data
            details = data["details"]
            assert "revenue" in details
            assert "expenses" in details

    def test_income_statement_json_currency_format(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test income statement JSON formats currency correctly."""
        output_path = temp_output_dir / "income_statement.json"
        exporter.export(income_statement_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Check currency formatting (2 decimal places, no symbols)
            assert data["summary"]["total_revenue"] == "50000.00"
            assert data["summary"]["total_expenses"] == "30000.00"
            assert data["summary"]["net_income"] == "20000.00"

    def test_income_statement_json_revenue_details(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test income statement JSON includes revenue details."""
        output_path = temp_output_dir / "income_statement.json"
        exporter.export(income_statement_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            revenue = data["details"]["revenue"]
            assert len(revenue) == 2
            assert revenue[0]["category"] == "Services"
            assert revenue[0]["amount"] == "40000.00"
            assert revenue[0]["percentage"] == 80.0

    def test_income_statement_json_expense_details(
        self, exporter, income_statement_data, temp_output_dir
    ):
        """Test income statement JSON includes expense details."""
        output_path = temp_output_dir / "income_statement.json"
        exporter.export(income_statement_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            expenses = data["details"]["expenses"]
            assert len(expenses) == 3
            assert expenses[0]["category"] == "Office"
            assert expenses[0]["amount"] == "15000.00"
            assert expenses[0]["percentage"] == 50.0

    # Expense report JSON structure tests

    def test_expense_report_json_has_schema_version(
        self, exporter, expense_report_data, temp_output_dir
    ):
        """Test expense report JSON includes schema version."""
        output_path = temp_output_dir / "expense_report.json"
        exporter.export(expense_report_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "schema_version" in data
            assert data["schema_version"] == "1.0"

    def test_expense_report_json_has_report_type(
        self, exporter, expense_report_data, temp_output_dir
    ):
        """Test expense report JSON includes report type."""
        output_path = temp_output_dir / "expense_report.json"
        exporter.export(expense_report_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["report_type"] == "expense_report"

    def test_expense_report_json_has_summary(self, exporter, expense_report_data, temp_output_dir):
        """Test expense report JSON includes summary with all fields."""
        output_path = temp_output_dir / "expense_report.json"
        exporter.export(expense_report_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            summary = data["summary"]
            assert "total_expenses" in summary
            assert "category_count" in summary
            assert "transaction_count" in summary
            assert summary["total_expenses"] == "30000.00"
            assert summary["category_count"] == 3
            assert summary["transaction_count"] == 25

    def test_expense_report_json_has_tax_codes(
        self, exporter, expense_report_data, temp_output_dir
    ):
        """Test expense report JSON includes tax codes."""
        output_path = temp_output_dir / "expense_report.json"
        exporter.export(expense_report_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            expenses = data["details"]["expenses"]
            assert len(expenses) == 3
            assert expenses[0]["tax_code"] == "8810"
            assert expenses[1]["tax_code"] == "8520"
            assert expenses[2]["tax_code"] == "8804"

    def test_expense_report_json_expense_details(
        self, exporter, expense_report_data, temp_output_dir
    ):
        """Test expense report JSON expense details are complete."""
        output_path = temp_output_dir / "expense_report.json"
        exporter.export(expense_report_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            expense = data["details"]["expenses"][0]
            assert "category" in expense
            assert "tax_code" in expense
            assert "amount" in expense
            assert "percentage" in expense
            assert expense["category"] == "Office"
            assert expense["amount"] == "15000.00"
            assert expense["percentage"] == 50.0

    # CRA exporter tests

    def test_cra_exporter_jurisdiction(self, cra_exporter, income_statement_data, temp_output_dir):
        """Test CRA exporter uses correct jurisdiction in metadata."""
        output_path = temp_output_dir / "income_statement.json"
        cra_exporter.export(income_statement_data, str(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Should use CRA from exporter config
            assert data["metadata"]["jurisdiction"] == "IRS"  # From data
            # But exporter is CRA
            assert cra_exporter.jurisdiction == "CRA"

    # Currency formatting tests

    def test_format_currency_decimal(self, exporter):
        """Test currency formatting with Decimal input."""
        result = exporter._format_currency(Decimal("1234.56"))
        assert result == "1234.56"

    def test_format_currency_integer(self, exporter):
        """Test currency formatting with integer input."""
        result = exporter._format_currency(Decimal("1000"))
        assert result == "1000.00"

    def test_format_currency_negative(self, exporter):
        """Test currency formatting with negative amount."""
        result = exporter._format_currency(Decimal("-500.75"))
        assert result == "-500.75"

    def test_format_currency_zero(self, exporter):
        """Test currency formatting with zero amount."""
        result = exporter._format_currency(Decimal("0.00"))
        assert result == "0.00"

    def test_format_currency_large_number(self, exporter):
        """Test currency formatting with large number."""
        result = exporter._format_currency(Decimal("1234567.89"))
        assert result == "1234567.89"

    def test_format_currency_converts_non_decimal(self, exporter):
        """Test currency formatting converts non-Decimal to Decimal."""
        result = exporter._format_currency(123.45)
        assert result == "123.45"
