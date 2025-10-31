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
        elif report_type == "tax_summary":
            df = self._build_tax_summary_csv(report_data)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")

        # Write to CSV with Excel compatibility
        df.to_csv(output_path, index=False, encoding="utf-8-sig")

        logger.info(f"CSV generated successfully: {output_path}")

    def _build_income_statement_csv(self, report_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Build DataFrame for income statement report (cash basis with tax breakdown).

        Args:
            report_data: Income statement data from ReportGenerator

        Returns:
            pandas DataFrame with income statement data
        """
        metadata = report_data["metadata"]
        revenue = report_data.get("revenue", {})
        expenses = report_data.get("expenses", {})
        net_income = report_data.get("net_income", {})

        rows = []

        # Metadata section
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Report Type",
                "Pre-Tax": "Income Statement (Cash Basis)",
                "Tax": "",
                "Cash Total": "",
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Date Range",
                "Pre-Tax": f"{metadata['start_date']} to {metadata['end_date']}",
                "Tax": "",
                "Cash Total": "",
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Jurisdiction",
                "Pre-Tax": metadata.get("jurisdiction", self.jurisdiction),
                "Tax": "",
                "Cash Total": "",
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Currency",
                "Pre-Tax": metadata.get("currency", self.currency),
                "Tax": "",
                "Cash Total": "",
                "Percentage": "",
            }
        )
        rows.append(
            {"Section": "", "Category": "", "Pre-Tax": "", "Tax": "", "Cash Total": "", "Percentage": ""}
        )  # Blank row

        # Summary section with cash-basis breakdown
        rows.append(
            {
                "Section": "Summary",
                "Category": "Total Revenue (Cash)",
                "Pre-Tax": revenue.get("total_formatted", "$0.00"),
                "Tax": revenue.get("tax_total_formatted", "$0.00"),
                "Cash Total": revenue.get("cash_total_formatted", "$0.00"),
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Summary",
                "Category": "Total Expenses (Cash)",
                "Pre-Tax": expenses.get("total_formatted", "$0.00"),
                "Tax": expenses.get("tax_total_formatted", "$0.00"),
                "Cash Total": expenses.get("cash_total_formatted", "$0.00"),
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Summary",
                "Category": "Net Income (Pre-tax)",
                "Pre-Tax": net_income.get("pretax_amount_formatted", "$0.00"),
                "Tax": "",
                "Cash Total": "",
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Summary",
                "Category": "Tax Position",
                "Pre-Tax": "",
                "Tax": net_income.get("tax_position_formatted", "$0.00"),
                "Cash Total": "",
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Summary",
                "Category": "Net Income (Cash)",
                "Pre-Tax": "",
                "Tax": "",
                "Cash Total": net_income.get("cash_amount_formatted", "$0.00"),
                "Percentage": "",
            }
        )
        rows.append(
            {"Section": "", "Category": "", "Pre-Tax": "", "Tax": "", "Cash Total": "", "Percentage": ""}
        )  # Blank row

        # Revenue breakdown with tax columns
        revenue_categories = revenue.get("categories", {})
        if revenue_categories:
            rows.append(
                {
                    "Section": "Revenue Details",
                    "Category": "Category",
                    "Pre-Tax": "Pre-Tax Amount",
                    "Tax": "Tax Collected",
                    "Cash Total": "Cash Total",
                    "Percentage": "% of Revenue",
                }
            )
            for cat_name, cat_data in revenue_categories.items():
                rows.append(
                    {
                        "Section": "Revenue Details",
                        "Category": self._escape_special_characters(cat_name),
                        "Pre-Tax": cat_data.get("total_formatted", "$0.00"),
                        "Tax": cat_data.get("tax_total_formatted", "$0.00"),
                        "Cash Total": cat_data.get("cash_total_formatted", "$0.00"),
                        "Percentage": cat_data.get("percentage_formatted", "0.0%"),
                    }
                )
            rows.append(
                {"Section": "", "Category": "", "Pre-Tax": "", "Tax": "", "Cash Total": "", "Percentage": ""}
            )  # Blank row

        # Expense breakdown with tax columns
        expense_categories = expenses.get("categories", {})
        if expense_categories:
            rows.append(
                {
                    "Section": "Expense Details",
                    "Category": "Category",
                    "Pre-Tax": "Pre-Tax Amount",
                    "Tax": "Tax Paid",
                    "Cash Total": "Cash Total",
                    "Percentage": "% of Expenses",
                }
            )
            for cat_name, cat_data in expense_categories.items():
                rows.append(
                    {
                        "Section": "Expense Details",
                        "Category": self._escape_special_characters(cat_name),
                        "Pre-Tax": cat_data.get("total_formatted", "$0.00"),
                        "Tax": cat_data.get("tax_total_formatted", "$0.00"),
                        "Cash Total": cat_data.get("cash_total_formatted", "$0.00"),
                        "Percentage": cat_data.get("percentage_formatted", "0.0%"),
                    }
                )

        return pd.DataFrame(rows)

    def _build_expense_report_csv(self, report_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Build DataFrame for expense report (cash basis with tax breakdown).

        Args:
            report_data: Expense report data from ReportGenerator

        Returns:
            pandas DataFrame with expense report data
        """
        metadata = report_data["metadata"]
        expenses = report_data.get("expenses", {})

        rows = []

        # Metadata section
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Report Type",
                "Tax Code": "Expense Report (Cash Basis)",
                "Pre-Tax": "",
                "Tax": "",
                "Cash Total": "",
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Date Range",
                "Tax Code": f"{metadata['start_date']} to {metadata['end_date']}",
                "Pre-Tax": "",
                "Tax": "",
                "Cash Total": "",
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Jurisdiction",
                "Tax Code": metadata.get("jurisdiction", self.jurisdiction),
                "Pre-Tax": "",
                "Tax": "",
                "Cash Total": "",
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Category": "Currency",
                "Tax Code": metadata.get("currency", self.currency),
                "Pre-Tax": "",
                "Tax": "",
                "Cash Total": "",
                "Percentage": "",
            }
        )
        rows.append(
            {"Section": "", "Category": "", "Tax Code": "", "Pre-Tax": "", "Tax": "", "Cash Total": "", "Percentage": ""}
        )  # Blank row

        # Summary section with cash-basis breakdown
        rows.append(
            {
                "Section": "Summary",
                "Category": "Total Expenses (Cash)",
                "Tax Code": "",
                "Pre-Tax": expenses.get("total_formatted", "$0.00"),
                "Tax": expenses.get("tax_total_formatted", "$0.00"),
                "Cash Total": expenses.get("cash_total_formatted", "$0.00"),
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Summary",
                "Category": "Number of Categories",
                "Tax Code": "",
                "Pre-Tax": str(expenses.get("category_count", 0)),
                "Tax": "",
                "Cash Total": "",
                "Percentage": "",
            }
        )
        rows.append(
            {
                "Section": "Summary",
                "Category": "Transaction Count",
                "Tax Code": "",
                "Pre-Tax": str(expenses.get("transaction_count", 0)),
                "Tax": "",
                "Cash Total": "",
                "Percentage": "",
            }
        )
        rows.append(
            {"Section": "", "Category": "", "Tax Code": "", "Pre-Tax": "", "Tax": "", "Cash Total": "", "Percentage": ""}
        )  # Blank row

        # Expense breakdown with tax columns
        expense_categories = expenses.get("categories", {})
        if expense_categories:
            rows.append(
                {
                    "Section": "Expense Details",
                    "Category": "Category",
                    "Tax Code": "Tax Code",
                    "Pre-Tax": "Pre-Tax Amount",
                    "Tax": "Tax Paid",
                    "Cash Total": "Cash Total",
                    "Percentage": "% of Expenses",
                }
            )
            for cat_name, cat_data in expense_categories.items():
                rows.append(
                    {
                        "Section": "Expense Details",
                        "Category": self._escape_special_characters(cat_name),
                        "Tax Code": cat_data.get("tax_code", "N/A"),
                        "Pre-Tax": cat_data.get("total_formatted", "$0.00"),
                        "Tax": cat_data.get("tax_total_formatted", "$0.00"),
                        "Cash Total": cat_data.get("cash_total_formatted", "$0.00"),
                        "Percentage": cat_data.get("percentage_formatted", "0.0%"),
                    }
                )

        return pd.DataFrame(rows)

    def _build_tax_summary_csv(self, report_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Build DataFrame for tax summary report.

        Args:
            report_data: Tax summary data from ReportGenerator

        Returns:
            pandas DataFrame with tax summary data
        """
        metadata = report_data["metadata"]
        tax_collected = report_data.get("tax_collected", {})
        tax_paid = report_data.get("tax_paid", {})
        net_position = report_data.get("net_position", {})

        rows = []

        # Metadata section
        rows.append(
            {
                "Section": "Metadata",
                "Date": "Report Type",
                "Description": "Tax Summary",
                "Amount": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Date": "Date Range",
                "Description": f"{metadata['start_date']} to {metadata['end_date']}",
                "Amount": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Date": "Jurisdiction",
                "Description": metadata.get("jurisdiction", self.jurisdiction),
                "Amount": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Date": "Currency",
                "Description": metadata.get("currency", self.currency),
                "Amount": "",
            }
        )
        rows.append(
            {
                "Section": "Metadata",
                "Date": "Disclaimer",
                "Description": "For informational purposes only. Consult a tax professional.",
                "Amount": "",
            }
        )
        rows.append({"Section": "", "Date": "", "Description": "", "Amount": ""})  # Blank row

        # Tax Collected section
        rows.append(
            {
                "Section": "Tax Collected (Output Tax)",
                "Date": "Date",
                "Description": "Description",
                "Amount": "Tax Amount",
            }
        )

        tax_collected_txns = tax_collected.get("transactions", [])
        for txn in tax_collected_txns:
            rows.append(
                {
                    "Section": "Tax Collected (Output Tax)",
                    "Date": txn.get("date", ""),
                    "Description": self._escape_special_characters(txn.get("description", "")),
                    "Amount": txn.get("amount_formatted", "$0.00"),
                }
            )

        rows.append(
            {
                "Section": "Tax Collected (Output Tax)",
                "Date": "TOTAL",
                "Description": f"Total Tax Collected ({tax_collected.get('count', 0)} transactions)",
                "Amount": tax_collected.get("total_formatted", "$0.00"),
            }
        )
        rows.append({"Section": "", "Date": "", "Description": "", "Amount": ""})  # Blank row

        # Tax Paid section
        rows.append(
            {
                "Section": "Tax Paid (Input Tax Credits)",
                "Date": "Date",
                "Description": "Description",
                "Amount": "Tax Amount",
            }
        )

        tax_paid_txns = tax_paid.get("transactions", [])
        for txn in tax_paid_txns:
            rows.append(
                {
                    "Section": "Tax Paid (Input Tax Credits)",
                    "Date": txn.get("date", ""),
                    "Description": self._escape_special_characters(txn.get("description", "")),
                    "Amount": txn.get("amount_formatted", "$0.00"),
                }
            )

        rows.append(
            {
                "Section": "Tax Paid (Input Tax Credits)",
                "Date": "TOTAL",
                "Description": f"Total Tax Paid ({tax_paid.get('count', 0)} transactions)",
                "Amount": tax_paid.get("total_formatted", "$0.00"),
            }
        )
        rows.append({"Section": "", "Date": "", "Description": "", "Amount": ""})  # Blank row

        # Net Position section
        payable = net_position.get("payable", True)
        status = "PAYABLE TO GOVERNMENT" if payable else "REFUNDABLE FROM GOVERNMENT"

        rows.append(
            {
                "Section": "Net Tax Position",
                "Date": "Status",
                "Description": status,
                "Amount": net_position.get("amount_formatted", "$0.00"),
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
