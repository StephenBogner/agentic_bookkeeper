"""Professional CSV export using pandas for Excel compatibility.

Module: csv_exporter
Author: Stephen Bogner
Created: 2025-10-29
"""

import logging
from pathlib import Path
from typing import Dict, Any
from decimal import Decimal

import pandas as pd

logger = logging.getLogger(__name__)


class CSVExporter:
    """
    Export financial reports to CSV format for Excel compatibility.

    This class generates CSV files with:
    - Professional headers with proper column names
    - Currency formatting with 2 decimal places
    - Special character handling for Excel compatibility
    - Optional metadata as comments
    - Tax jurisdiction support

    Attributes:
        jurisdiction: Tax jurisdiction ('CRA' or 'IRS')
        currency: Currency code for formatting ('USD' or 'CAD')
    """

    def __init__(self, jurisdiction: str = "IRS", currency: str = "USD"):
        """
        Initialize CSV exporter.

        Args:
            jurisdiction: Tax jurisdiction ('CRA' or 'IRS')
            currency: Currency code ('USD' or 'CAD')

        Raises:
            ValueError: If jurisdiction or currency is invalid
        """
        if jurisdiction not in ("CRA", "IRS"):
            raise ValueError(f"Invalid jurisdiction: {jurisdiction}. Must be 'CRA' or 'IRS'")

        if currency not in ("USD", "CAD"):
            raise ValueError(f"Invalid currency: {currency}. Must be 'USD' or 'CAD'")

        self.jurisdiction = jurisdiction
        self.currency = currency

        logger.info(
            f"CSV exporter initialized (jurisdiction={jurisdiction}, " f"currency={currency})"
        )

    def export(self, report_data: Dict[str, Any], output_path: str) -> None:
        """
        Export report data to CSV file.

        Args:
            report_data: Report data dictionary from ReportGenerator
            output_path: Path where CSV file should be saved

        Raises:
            ValueError: If report_data is missing required fields
            TypeError: If report_data is not a dictionary
            IOError: If output path is not writable
        """
        if not isinstance(report_data, dict):
            raise TypeError(f"Expected dict, got {type(report_data)}")

        if "metadata" not in report_data:
            raise ValueError("report_data missing required field: metadata")

        if "summary" not in report_data:
            raise ValueError("report_data missing required field: summary")

        # Validate output path
        output_file = Path(output_path)
        if not output_file.parent.exists():
            raise IOError(f"Output directory does not exist: {output_file.parent}")

        # Get report type from metadata
        report_type = report_data["metadata"].get("report_type", "unknown")

        logger.info(f"Generating CSV for {report_type} report: {output_path}")

        # Build DataFrame based on report type
        if report_type == "income_statement":
            df = self._build_income_statement_csv(report_data)
        elif report_type == "expense_report":
            df = self._build_expense_report_csv(report_data)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")

        # Write to CSV with Excel compatibility
        df.to_csv(output_path, index=False, encoding="utf-8-sig")

        logger.info(f"CSV generated successfully: {output_path}")

    def _build_income_statement_csv(self, report_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Build DataFrame for income statement report.

        Args:
            report_data: Income statement data from ReportGenerator

        Returns:
            pandas DataFrame with income statement data
        """
        metadata = report_data["metadata"]
        summary = report_data["summary"]
        details = report_data.get("details", {})

        rows = []

        # Metadata section
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Report Type",
                "Amount": "Income Statement",
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Date Range",
                "Amount": f"{metadata['start_date']} to {metadata['end_date']}",
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Jurisdiction",
                "Amount": metadata.get("jurisdiction", self.jurisdiction),
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Currency",
                "Amount": metadata.get("currency", self.currency),
                "Percentage": "",
            }
        )
        rows.append({"Section": "", "Category": "", "Amount": "", "Percentage": ""})  # Blank row

        # Summary section
        rows.append(
            {
                "Section": "Summary",
                "Category": "Total Revenue",
                "Amount": self._format_currency(summary["total_revenue"]),
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Summary",
                "Category": "Total Expenses",
                "Amount": self._format_currency(summary["total_expenses"]),
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Summary",
                "Category": "Net Income",
                "Amount": self._format_currency(summary["net_income"]),
                "Percentage": "",
            }
        )
        rows.append({"Section": "", "Category": "", "Amount": "", "Percentage": ""})  # Blank row

        # Revenue breakdown
        if "revenue" in details and details["revenue"]:
            rows.append(
                {
                    "Section": "Revenue Details",
                    "Category": "Category",
                    "Amount": "Amount",
                    "Percentage": "Percentage",
                }
            )
            for category in details["revenue"]:
                rows.append(
                    {
                        "Section": "Revenue Details",
                        "Category": self._escape_special_characters(category["category"]),
                        "Amount": self._format_currency(category["total"]),
                        "Percentage": f"{category['percentage']:.1f}%",
                    }
                )
            rows.append(
                {"Section": "", "Category": "", "Amount": "", "Percentage": ""}
            )  # Blank row

        # Expense breakdown
        if "expenses" in details and details["expenses"]:
            rows.append(
                {
                    "Section": "Expense Details",
                    "Category": "Category",
                    "Amount": "Amount",
                    "Percentage": "Percentage",
                }
            )
            for category in details["expenses"]:
                rows.append(
                    {
                        "Section": "Expense Details",
                        "Category": self._escape_special_characters(category["category"]),
                        "Amount": self._format_currency(category["total"]),
                        "Percentage": f"{category['percentage']:.1f}%",
                    }
                )

        return pd.DataFrame(rows)

    def _build_expense_report_csv(self, report_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Build DataFrame for expense report.

        Args:
            report_data: Expense report data from ReportGenerator

        Returns:
            pandas DataFrame with expense report data
        """
        metadata = report_data["metadata"]
        summary = report_data["summary"]
        details = report_data.get("details", {})

        rows = []

        # Metadata section
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Report Type",
                "Tax Code": "Expense Report",
                "Amount": "",
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Date Range",
                "Tax Code": f"{metadata['start_date']} to {metadata['end_date']}",
                "Amount": "",
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Jurisdiction",
                "Tax Code": metadata.get("jurisdiction", self.jurisdiction),
                "Amount": "",
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Currency",
                "Tax Code": metadata.get("currency", self.currency),
                "Amount": "",
                "Percentage": "",
            }
        )
        rows.append(
            {"Section": "", "Category": "", "Tax Code": "", "Amount": "", "Percentage": ""}
        )  # Blank row

        # Summary section
        rows.append(
            {
                "Section": "Summary",
                "Category": "Total Expenses",
                "Tax Code": "",
                "Amount": self._format_currency(summary["total_expenses"]),
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Summary",
                "Category": "Number of Categories",
                "Tax Code": "",
                "Amount": str(summary["category_count"]),
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Summary",
                "Category": "Transaction Count",
                "Tax Code": "",
                "Amount": str(summary.get("transaction_count", 0)),
                "Percentage": "",
            }
        )
        rows.append(
            {"Section": "", "Category": "", "Tax Code": "", "Amount": "", "Percentage": ""}
        )  # Blank row

        # Expense breakdown with tax codes
        if "expenses" in details and details["expenses"]:
            rows.append(
                {
                    "Section": "Expense Details",
                    "Category": "Category",
                    "Tax Code": "Tax Code",
                    "Amount": "Amount",
                    "Percentage": "Percentage",
                }
            )
            for category in details["expenses"]:
                rows.append(
                    {
                        "Section": "Expense Details",
                        "Category": self._escape_special_characters(category["category"]),
                        "Tax Code": category.get("tax_code", "N/A"),
                        "Amount": self._format_currency(category["total"]),
                        "Percentage": f"{category['percentage']:.1f}%",
                    }
                )

        return pd.DataFrame(rows)

    def _format_currency(self, amount: Decimal) -> str:
        """
        Format Decimal amount as currency string.

        Args:
            amount: Decimal amount to format

        Returns:
            Formatted currency string (e.g., "$1,234.56")
        """
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        symbol = "$"
        sign = "-" if amount < 0 else ""
        abs_amount = abs(amount)

        # Format with thousands separator and 2 decimal places
        formatted = f"{abs_amount:,.2f}"

        return f"{sign}{symbol}{formatted}"

    def _escape_special_characters(self, text: str) -> str:
        """
        Escape special characters for CSV/Excel compatibility.

        Args:
            text: Text to escape

        Returns:
            Escaped text safe for CSV
        """
        if not isinstance(text, str):
            text = str(text)

        # Excel treats leading = as formula, so escape it
        if text.startswith("="):
            text = "'" + text

        return text
