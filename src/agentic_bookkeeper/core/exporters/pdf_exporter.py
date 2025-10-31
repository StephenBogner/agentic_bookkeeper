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
            elif report_type == "tax_summary":
                story = self._build_tax_summary_pdf(report_data)
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
        Build PDF content for income statement report (cash basis).

        Args:
            report_data: Income statement data from ReportGenerator

        Returns:
            List of ReportLab Flowable objects
        """
        story = []
        metadata = report_data["metadata"]
        revenue = report_data.get("revenue", {})
        expenses = report_data.get("expenses", {})
        net_income = report_data.get("net_income", {})

        # Title
        title = Paragraph("Income Statement (Cash Basis)", self.styles["ReportTitle"])
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
            ["Total Revenue (Cash)", revenue.get("cash_total_formatted", "$0.00")],
            ["  Pre-tax Amount", revenue.get("total_formatted", "$0.00")],
            ["  Tax Collected", revenue.get("tax_total_formatted", "$0.00")],
            ["", ""],
            ["Total Expenses (Cash)", expenses.get("cash_total_formatted", "$0.00")],
            ["  Pre-tax Amount", expenses.get("total_formatted", "$0.00")],
            ["  Tax Paid", expenses.get("tax_total_formatted", "$0.00")],
            ["", ""],
            ["Net Income (Cash)", net_income.get("cash_amount_formatted", "$0.00")],
            ["  Pre-tax Net Income", net_income.get("pretax_amount_formatted", "$0.00")],
            ["  Net Tax Position", net_income.get("tax_position_formatted", "$0.00")],
        ]

        summary_table = Table(summary_data, colWidths=[4 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Helvetica", 10),
                    ("FONT", (0, 0), (0, 0), "Helvetica-Bold", 11),
                    ("FONT", (0, 4), (0, 4), "Helvetica-Bold", 11),
                    ("FONT", (0, 8), (0, 8), "Helvetica-Bold", 12),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
                    ("TEXTCOLOR", (0, 1), (0, 2), colors.HexColor("#666666")),
                    ("TEXTCOLOR", (0, 5), (0, 6), colors.HexColor("#666666")),
                    ("TEXTCOLOR", (0, 9), (0, 10), colors.HexColor("#666666")),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LINEABOVE", (0, 8), (-1, 8), 2, colors.HexColor("#1a1a1a")),
                    ("LINEBELOW", (0, 8), (-1, 8), 2, colors.HexColor("#1a1a1a")),
                ]
            )
        )
        story.append(summary_table)

        # Revenue breakdown
        revenue_categories = revenue.get("categories", {})
        if revenue_categories:
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph("Revenue by Category", self.styles["SectionHeader"]))

            revenue_data = [["Category", "Pre-Tax", "Tax", "Cash Total", "%"]]
            for cat_name, cat_data in revenue_categories.items():
                revenue_data.append(
                    [
                        cat_name,
                        cat_data.get("total_formatted", "$0.00"),
                        cat_data.get("tax_total_formatted", "$0.00"),
                        cat_data.get("cash_total_formatted", "$0.00"),
                        cat_data.get("percentage_formatted", "0%"),
                    ]
                )

            revenue_table = Table(revenue_data, colWidths=[2 * inch, 1.25 * inch, 1.25 * inch, 1.25 * inch, 0.75 * inch])
            revenue_table.setStyle(self._create_detail_table_style())
            story.append(revenue_table)

        # Expense breakdown
        expense_categories = expenses.get("categories", {})
        if expense_categories:
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph("Expenses by Category", self.styles["SectionHeader"]))

            expense_data = [["Category", "Pre-Tax", "Tax", "Cash Total", "%"]]
            for cat_name, cat_data in expense_categories.items():
                expense_data.append(
                    [
                        cat_name,
                        cat_data.get("total_formatted", "$0.00"),
                        cat_data.get("tax_total_formatted", "$0.00"),
                        cat_data.get("cash_total_formatted", "$0.00"),
                        cat_data.get("percentage_formatted", "0%"),
                    ]
                )

            expense_table = Table(expense_data, colWidths=[2 * inch, 1.25 * inch, 1.25 * inch, 1.25 * inch, 0.75 * inch])
            expense_table.setStyle(self._create_detail_table_style())
            story.append(expense_table)

        return story

    def _build_expense_report_pdf(self, report_data: Dict[str, Any]) -> List:
        """
        Build PDF content for expense report (cash basis).

        Args:
            report_data: Expense report data from ReportGenerator

        Returns:
            List of ReportLab Flowable objects
        """
        story = []
        metadata = report_data["metadata"]
        expenses = report_data.get("expenses", {})

        # Title
        title = Paragraph("Expense Report (Cash Basis)", self.styles["ReportTitle"])
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
            ["Total Expenses (Cash)", expenses.get("cash_total_formatted", "$0.00")],
            ["  Pre-tax Amount", expenses.get("total_formatted", "$0.00")],
            ["  Tax Paid", expenses.get("tax_total_formatted", "$0.00")],
            ["", ""],
            ["Transaction Count", str(expenses.get("transaction_count", 0))],
        ]

        summary_table = Table(summary_data, colWidths=[4 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Helvetica", 10),
                    ("FONT", (0, 0), (0, 0), "Helvetica-Bold", 11),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333333")),
                    ("TEXTCOLOR", (0, 1), (0, 2), colors.HexColor("#666666")),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(summary_table)

        # Expense breakdown with tax codes
        expense_categories = expenses.get("categories", {})
        if expense_categories:
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph("Expenses by Category", self.styles["SectionHeader"]))

            expense_data = [["Category", "Tax Code", "Pre-Tax", "Tax", "Cash Total", "%"]]
            for cat_name, cat_data in expense_categories.items():
                expense_data.append(
                    [
                        cat_name,
                        cat_data.get("tax_code", "N/A"),
                        cat_data.get("total_formatted", "$0.00"),
                        cat_data.get("tax_total_formatted", "$0.00"),
                        cat_data.get("cash_total_formatted", "$0.00"),
                        cat_data.get("percentage_formatted", "0%"),
                    ]
                )

            expense_table = Table(
                expense_data, colWidths=[1.5 * inch, 0.75 * inch, 1.25 * inch, 1.0 * inch, 1.25 * inch, 0.75 * inch]
            )
            expense_table.setStyle(self._create_detail_table_style())
            story.append(expense_table)

        return story

    def _build_tax_summary_pdf(self, report_data: Dict[str, Any]) -> List:
        """
        Build PDF content for tax summary report.

        Args:
            report_data: Tax summary data from ReportGenerator

        Returns:
            List of ReportLab Flowable objects
        """
        story = []
        metadata = report_data["metadata"]
        tax_collected = report_data.get("tax_collected", {})
        tax_paid = report_data.get("tax_paid", {})
        net_position = report_data.get("net_position", {})

        # Title
        title = Paragraph("Tax Summary Report", self.styles["ReportTitle"])
        story.append(title)

        # Date range
        subtitle = Paragraph(
            f"{metadata['start_date']} to {metadata['end_date']}", self.styles["ReportSubtitle"]
        )
        story.append(subtitle)

        # Disclaimer
        disclaimer = Paragraph(
            "<i>This report is for informational purposes only. "
            "Consult with a tax professional for actual filing.</i>",
            self.styles["Normal"]
        )
        story.append(disclaimer)
        story.append(Spacer(1, 0.2 * inch))

        # Tax Collected Section
        story.append(Paragraph("Tax Collected (Output Tax)", self.styles["SectionHeader"]))

        tax_collected_txns = tax_collected.get("transactions", [])
        if tax_collected_txns:
            collected_data = [["Date", "Description", "Amount"]]
            for txn in tax_collected_txns:
                desc = txn.get("description", "")[:40]  # Truncate long descriptions
                collected_data.append([
                    txn.get("date", ""),
                    desc,
                    txn.get("amount_formatted", "$0.00")
                ])

            collected_table = Table(collected_data, colWidths=[1.25 * inch, 3.5 * inch, 1.75 * inch])
            collected_table.setStyle(self._create_detail_table_style())
            story.append(collected_table)
        else:
            story.append(Paragraph("<i>No tax collected during this period</i>", self.styles["Normal"]))

        story.append(Spacer(1, 0.1 * inch))

        # Total tax collected
        total_collected_data = [
            ["Total Tax Collected:", tax_collected.get("total_formatted", "$0.00")]
        ]
        total_collected_table = Table(total_collected_data, colWidths=[4 * inch, 2 * inch])
        total_collected_table.setStyle(
            TableStyle([
                ("FONT", (0, 0), (-1, -1), "Helvetica-Bold", 12),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("LINEABOVE", (0, 0), (-1, 0), 1, colors.HexColor("#333333")),
            ])
        )
        story.append(total_collected_table)

        # Tax Paid Section
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("Tax Paid (Input Tax Credits)", self.styles["SectionHeader"]))

        tax_paid_txns = tax_paid.get("transactions", [])
        if tax_paid_txns:
            paid_data = [["Date", "Description", "Amount"]]
            for txn in tax_paid_txns:
                desc = txn.get("description", "")[:40]  # Truncate long descriptions
                paid_data.append([
                    txn.get("date", ""),
                    desc,
                    txn.get("amount_formatted", "$0.00")
                ])

            paid_table = Table(paid_data, colWidths=[1.25 * inch, 3.5 * inch, 1.75 * inch])
            paid_table.setStyle(self._create_detail_table_style())
            story.append(paid_table)
        else:
            story.append(Paragraph("<i>No tax paid during this period</i>", self.styles["Normal"]))

        story.append(Spacer(1, 0.1 * inch))

        # Total tax paid
        total_paid_data = [
            ["Total Tax Paid:", tax_paid.get("total_formatted", "$0.00")]
        ]
        total_paid_table = Table(total_paid_data, colWidths=[4 * inch, 2 * inch])
        total_paid_table.setStyle(
            TableStyle([
                ("FONT", (0, 0), (-1, -1), "Helvetica-Bold", 12),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("LINEABOVE", (0, 0), (-1, 0), 1, colors.HexColor("#333333")),
            ])
        )
        story.append(total_paid_table)

        # Net Tax Position Section
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("Net Tax Position", self.styles["SectionHeader"]))

        payable = net_position.get("payable", True)
        status = "PAYABLE TO GOVERNMENT" if payable else "REFUNDABLE FROM GOVERNMENT"
        status_color = colors.HexColor("#d9534f") if payable else colors.HexColor("#5cb85c")

        net_data = [
            ["Net Amount " + status + ":", net_position.get("amount_formatted", "$0.00")]
        ]
        net_table = Table(net_data, colWidths=[4 * inch, 2 * inch])
        net_table.setStyle(
            TableStyle([
                ("FONT", (0, 0), (-1, -1), "Helvetica-Bold", 14),
                ("TEXTCOLOR", (0, 0), (-1, -1), status_color),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LINEABOVE", (0, 0), (-1, 0), 2, colors.HexColor("#1a1a1a")),
                ("LINEBELOW", (0, 0), (-1, 0), 2, colors.HexColor("#1a1a1a")),
            ])
        )
        story.append(net_table)

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
