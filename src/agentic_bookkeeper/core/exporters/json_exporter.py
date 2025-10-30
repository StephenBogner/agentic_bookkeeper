"""Professional JSON export with schema versioning and pretty printing.

Module: json_exporter
Author: Stephen Bogner
Created: 2025-10-29
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
from decimal import Decimal
from datetime import datetime

logger = logging.getLogger(__name__)


class JSONExporter:
    """
    Export financial reports to structured JSON format.

    This class generates JSON files with:
    - Structured schema with versioning
    - Comprehensive metadata
    - Human-readable formatting (optional)
    - Valid JSON syntax
    - Tax jurisdiction support

    Attributes:
        jurisdiction: Tax jurisdiction ('CRA' or 'IRS')
        currency: Currency code for formatting ('USD' or 'CAD')
    """

    SCHEMA_VERSION = "1.0"

    def __init__(self, jurisdiction: str = "IRS", currency: str = "USD"):
        """
        Initialize JSON exporter.

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
            f"JSON exporter initialized (jurisdiction={jurisdiction}, " f"currency={currency})"
        )

    def export(self, report_data: Dict[str, Any], output_path: str, pretty: bool = True) -> None:
        """
        Export report data to JSON file.

        Args:
            report_data: Report data dictionary from ReportGenerator
            output_path: Path where JSON file should be saved
            pretty: Whether to pretty-print JSON with indentation (default: True)

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

        logger.info(f"Generating JSON for {report_type} report: {output_path}")

        # Build JSON structure based on report type
        if report_type == "income_statement":
            json_data = self._build_income_statement_json(report_data)
        elif report_type == "expense_report":
            json_data = self._build_expense_report_json(report_data)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")

        # Write to JSON file
        with open(output_path, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(json_data, f, ensure_ascii=False)

        logger.info(f"JSON generated successfully: {output_path}")

    def _build_income_statement_json(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build JSON structure for income statement report.

        Args:
            report_data: Income statement data from ReportGenerator

        Returns:
            Dictionary with structured JSON data
        """
        metadata = report_data["metadata"]
        summary = report_data["summary"]
        details = report_data.get("details", {})

        # Build structured JSON
        json_data = {
            "schema_version": self.SCHEMA_VERSION,
            "report_type": "income_statement",
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "start_date": metadata["start_date"],
                "end_date": metadata["end_date"],
                "jurisdiction": metadata.get("jurisdiction", self.jurisdiction),
                "currency": metadata.get("currency", self.currency),
            },
            "summary": {
                "total_revenue": self._format_currency(summary["total_revenue"]),
                "total_expenses": self._format_currency(summary["total_expenses"]),
                "net_income": self._format_currency(summary["net_income"]),
            },
            "details": {},
        }

        # Add revenue breakdown
        if "revenue" in details and details["revenue"]:
            json_data["details"]["revenue"] = [
                {
                    "category": category["category"],
                    "amount": self._format_currency(category["total"]),
                    "percentage": round(float(category["percentage"]), 1),
                }
                for category in details["revenue"]
            ]

        # Add expense breakdown
        if "expenses" in details and details["expenses"]:
            json_data["details"]["expenses"] = [
                {
                    "category": category["category"],
                    "amount": self._format_currency(category["total"]),
                    "percentage": round(float(category["percentage"]), 1),
                }
                for category in details["expenses"]
            ]

        return json_data

    def _build_expense_report_json(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build JSON structure for expense report.

        Args:
            report_data: Expense report data from ReportGenerator

        Returns:
            Dictionary with structured JSON data
        """
        metadata = report_data["metadata"]
        summary = report_data["summary"]
        details = report_data.get("details", {})

        # Build structured JSON
        json_data = {
            "schema_version": self.SCHEMA_VERSION,
            "report_type": "expense_report",
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "start_date": metadata["start_date"],
                "end_date": metadata["end_date"],
                "jurisdiction": metadata.get("jurisdiction", self.jurisdiction),
                "currency": metadata.get("currency", self.currency),
            },
            "summary": {
                "total_expenses": self._format_currency(summary["total_expenses"]),
                "category_count": summary["category_count"],
                "transaction_count": summary.get("transaction_count", 0),
            },
            "details": {},
        }

        # Add expense breakdown with tax codes
        if "expenses" in details and details["expenses"]:
            json_data["details"]["expenses"] = [
                {
                    "category": category["category"],
                    "tax_code": category.get("tax_code", "N/A"),
                    "amount": self._format_currency(category["total"]),
                    "percentage": round(float(category["percentage"]), 1),
                }
                for category in details["expenses"]
            ]

        return json_data

    def _format_currency(self, amount: Decimal) -> str:
        """
        Format Decimal amount as currency string for JSON.

        Args:
            amount: Decimal amount to format

        Returns:
            Formatted currency string (e.g., "1234.56")
        """
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        # Return as string with 2 decimal places (no currency symbol for JSON)
        return f"{amount:.2f}"
