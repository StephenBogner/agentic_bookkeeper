"""Professional PDF export using ReportLab for financial reports.

Module: pdf_exporter
Author: Stephen Bogner
Created: 2025-10-29
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from decimal import Decimal
import time

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.enums import TA_CENTER

from ...utils.logger import log_operation_start, log_operation_success, log_operation_failure

logger = logging.getLogger(__name__)


class PDFExporter:
    """
    Export financial reports to professional PDF format using ReportLab.

    This class generates PDF documents with:
    - Professional headers with company information
    - Footers with page numbers and generation timestamp
    - Formatted tables for financial data
    - Multi-page support with consistent styling
    - Tax jurisdiction labeling

    Attributes:
        jurisdiction: Tax jurisdiction ('CRA' or 'IRS')
        currency: Currency code for formatting ('USD' or 'CAD')
    """

    def __init__(self, jurisdiction: str = "IRS", currency: str = "USD"):
        """
        Initialize PDF exporter.

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
        self.styles = getSampleStyleSheet()

        # Create custom styles
        self._create_custom_styles()

        logger.info(
            f"PDF exporter initialized (jurisdiction={jurisdiction}, " f"currency={currency})"
        )

    def _create_custom_styles(self) -> None:
        """Create custom paragraph styles for PDF."""
        # Title style
        self.styles.add(
            ParagraphStyle(
                name="ReportTitle",
                parent=self.styles["Heading1"],
                fontSize=18,
                textColor=colors.HexColor("#1a1a1a"),
                spaceAfter=12,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
            )
        )

        # Subtitle style
        self.styles.add(
            ParagraphStyle(
                name="ReportSubtitle",
                parent=self.styles["Normal"],
                fontSize=12,
                textColor=colors.HexColor("#666666"),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName="Helvetica",
            )
        )

        # Section header style
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#333333"),
                spaceAfter=10,
                spaceBefore=10,
                fontName="Helvetica-Bold",
            )
        )

    def export(self, report_data: Dict[str, Any], output_path: str) -> None:
        """
        Export report data to PDF file.

        Args:
            report_data: Report data dictionary from ReportGenerator
            output_path: Path where PDF file should be saved

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

        start_time = time.time()
        log_operation_start(
            logger, "pdf_export", report_type=report_type, output_path=str(output_file)
        )

        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_file),
                pagesize=letter,
                rightMargin=0.75 * inch,
                leftMargin=0.75 * inch,
                topMargin=1 * inch,
                bottomMargin=0.75 * inch,
            )

            # Build content based on report type
            if report_type == "income_statement":
                story = self._build_income_statement_pdf(report_data)
            elif report_type == "expense_report":
                story = self._build_expense_report_pdf(report_data)
            else:
                raise ValueError(f"Unsupported report type: {report_type}")

            # Add header and footer
            doc.build(
                story,
                onFirstPage=self._add_page_decorations,
                onLaterPages=self._add_page_decorations,
            )

            duration_ms = (time.time() - start_time) * 1000
            file_size_kb = output_file.stat().st_size / 1024
            log_operation_success(
                logger,
                "pdf_export",
                duration_ms=duration_ms,
                report_type=report_type,
                file_size_kb=f"{file_size_kb:.2f}",
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_operation_failure(
                logger, "pdf_export", e, report_type=report_type, duration_ms=duration_ms
            )
            raise

    def _add_page_decorations(self, canvas: Any, doc: Any) -> None:
        """
        Add header and footer to each page.

        Args:
            canvas: ReportLab canvas object
            doc: SimpleDocTemplate document object
        """
        canvas.saveState()

        # Footer - page number and timestamp
        footer_text = f"Page {doc.page} • Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(doc.pagesize[0] / 2, 0.5 * inch, footer_text)

        # Add jurisdiction label in footer
        jurisdiction_text = f"Tax Jurisdiction: {self.jurisdiction}"
        canvas.drawRightString(doc.pagesize[0] - 0.75 * inch, 0.5 * inch, jurisdiction_text)

        canvas.restoreState()

    def _build_income_statement_pdf(self, report_data: Dict[str, Any]) -> List:
        """
        Build PDF content for income statement report.

        Args:
            report_data: Income statement data from ReportGenerator

        Returns:
            List of ReportLab Flowable objects
        """
        story = []
        metadata = report_data["metadata"]
        summary = report_data["summary"]
        details = report_data.get("details", {})

        # Title
        title = Paragraph("Income Statement", self.styles["ReportTitle"])
        story.append(title)

        # Date range
        subtitle = Paragraph(
            f"{metadata['start_date']} to {metadata['end_date']}", self.styles["ReportSubtitle"]
        )
        story.append(subtitle)

        # Summary section
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("Summary", self.styles["SectionHeader"]))

        summary_data = [
            ["Total Revenue", self._format_currency(summary["total_revenue"])],
            ["Total Expenses", self._format_currency(summary["total_expenses"])],
            ["Net Income", self._format_currency(summary["net_income"])],
        ]

        summary_table = Table(summary_data, colWidths=[4 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Helvetica", 11),
                    ("FONT", (0, 2), (-1, 2), "Helvetica-Bold", 12),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("LINEABOVE", (0, 2), (-1, 2), 2, colors.HexColor("#1a1a1a")),
                    ("LINEBELOW", (0, 2), (-1, 2), 2, colors.HexColor("#1a1a1a")),
                ]
            )
        )
        story.append(summary_table)

        # Revenue breakdown
        if "revenue" in details and details["revenue"]:
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph("Revenue by Category", self.styles["SectionHeader"]))

            revenue_data = [["Category", "Amount", "Percentage"]]
            for category in details["revenue"]:
                revenue_data.append(
                    [
                        category["category"],
                        self._format_currency(category["total"]),
                        f"{category['percentage']:.1f}%",
                    ]
                )

            revenue_table = Table(revenue_data, colWidths=[3 * inch, 1.75 * inch, 1.25 * inch])
            revenue_table.setStyle(self._create_detail_table_style())
            story.append(revenue_table)

        # Expense breakdown
        if "expenses" in details and details["expenses"]:
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph("Expenses by Category", self.styles["SectionHeader"]))

            expense_data = [["Category", "Amount", "Percentage"]]
            for category in details["expenses"]:
                expense_data.append(
                    [
                        category["category"],
                        self._format_currency(category["total"]),
                        f"{category['percentage']:.1f}%",
                    ]
                )

            expense_table = Table(expense_data, colWidths=[3 * inch, 1.75 * inch, 1.25 * inch])
            expense_table.setStyle(self._create_detail_table_style())
            story.append(expense_table)

        return story

    def _build_expense_report_pdf(self, report_data: Dict[str, Any]) -> List:
        """
        Build PDF content for expense report.

        Args:
            report_data: Expense report data from ReportGenerator

        Returns:
            List of ReportLab Flowable objects
        """
        story = []
        metadata = report_data["metadata"]
        summary = report_data["summary"]
        details = report_data.get("details", {})

        # Title
        title = Paragraph("Expense Report", self.styles["ReportTitle"])
        story.append(title)

        # Date range
        subtitle = Paragraph(
            f"{metadata['start_date']} to {metadata['end_date']}", self.styles["ReportSubtitle"]
        )
        story.append(subtitle)

        # Summary section
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("Summary", self.styles["SectionHeader"]))

        summary_data = [
            ["Total Expenses", self._format_currency(summary["total_expenses"])],
            ["Number of Categories", str(summary["category_count"])],
            ["Transaction Count", str(summary.get("transaction_count", 0))],
        ]

        summary_table = Table(summary_data, colWidths=[4 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Helvetica", 11),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(summary_table)

        # Expense breakdown with tax codes
        if "expenses" in details and details["expenses"]:
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph("Expenses by Category", self.styles["SectionHeader"]))

            expense_data = [["Category", "Tax Code", "Amount", "%"]]
            for category in details["expenses"]:
                expense_data.append(
                    [
                        category["category"],
                        category.get("tax_code", "N/A"),
                        self._format_currency(category["total"]),
                        f"{category['percentage']:.1f}%",
                    ]
                )

            expense_table = Table(
                expense_data, colWidths=[2.5 * inch, 1.25 * inch, 1.5 * inch, 0.75 * inch]
            )
            expense_table.setStyle(self._create_detail_table_style())
            story.append(expense_table)

        return story

    def _create_detail_table_style(self) -> TableStyle:
        """
        Create standard table style for detail tables.

        Returns:
            TableStyle for detail tables
        """
        return TableStyle(
            [
                # Header row
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4a90e2")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 11),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                # Data rows
                ("FONT", (0, 1), (-1, -1), "Helvetica", 10),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#333333")),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("ALIGN", (0, 1), (0, -1), "LEFT"),
                # Padding
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                # Grid
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                # Alternating rows
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ]
        )

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
