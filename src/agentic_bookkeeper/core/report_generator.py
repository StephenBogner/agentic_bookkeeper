"""Core report generation engine with filtering, aggregation, and calculations.

Module: report_generator
Author: Stephen Bogner
Created: 2025-10-29
"""

import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
import hashlib
import time

from ..models.transaction import Transaction
from ..core.transaction_manager import TransactionManager
from ..utils.logger import log_operation_start, log_operation_success, log_operation_failure

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generate financial reports from transaction data.

    This class provides core report generation functionality including:
    - Date range filtering
    - Data aggregation (sum, group by category)
    - Calculation utilities (totals, subtotals, percentages)
    - Currency formatting
    - Report metadata generation
    - Tax jurisdiction support (CRA/IRS)

    Attributes:
        transaction_manager: TransactionManager instance for data access
        jurisdiction: Tax jurisdiction ('CRA' or 'IRS')
        currency: Currency code for formatting (default: 'USD')
    """

    def __init__(
        self,
        transaction_manager: TransactionManager,
        jurisdiction: str = "IRS",
        currency: str = "USD",
    ) -> None:
        """
        Initialize report generator.

        Args:
            transaction_manager: TransactionManager instance
            jurisdiction: Tax jurisdiction ('CRA' or 'IRS')
            currency: Currency code ('USD' or 'CAD')

        Raises:
            ValueError: If jurisdiction is invalid
            TypeError: If transaction_manager is not TransactionManager instance
        """
        if not isinstance(transaction_manager, TransactionManager):
            raise TypeError(f"Expected TransactionManager, got {type(transaction_manager)}")

        if jurisdiction not in ("CRA", "IRS"):
            raise ValueError(f"Invalid jurisdiction: {jurisdiction}. Must be 'CRA' or 'IRS'")

        if currency not in ("USD", "CAD"):
            raise ValueError(f"Invalid currency: {currency}. Must be 'USD' or 'CAD'")

        self.transaction_manager = transaction_manager
        self.jurisdiction = jurisdiction
        self.currency = currency
        # Cache for filtered transactions to avoid redundant queries
        self._transaction_cache: Dict[str, List[Transaction]] = {}
        self._cache_max_size = 100  # Max entries in cache

        logger.info(
            f"Report generator initialized (jurisdiction={jurisdiction}, " f"currency={currency})"
        )

    def generate_report(
        self, report_type: str, start_date: str, end_date: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate a financial report for a date range.

        Args:
            report_type: Type of report ('income_statement', 'expense_report')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            **kwargs: Additional report-specific parameters

        Returns:
            Dictionary containing report data with structure:
            {
                'metadata': {...},
                'summary': {...},
                'details': {...}
            }

        Raises:
            ValueError: If dates are invalid or report_type is unknown
        """
        start_time = time.time()
        log_operation_start(
            logger,
            "report_generation",
            report_type=report_type,
            date_range=f"{start_date} to {end_date}",
            jurisdiction=self.jurisdiction,
        )

        try:
            # Validate date range
            self._validate_date_range(start_date, end_date)

            # Get filtered transactions
            transactions = self.filter_by_date_range(start_date=start_date, end_date=end_date)

            # Generate metadata
            metadata = self.generate_metadata(
                start_date=start_date, end_date=end_date, transaction_count=len(transactions)
            )

            # Calculate totals and aggregations
            totals = self.calculate_totals(transactions)
            category_breakdown = self.group_by_category(transactions)

            # Build report structure
            report = {
                "metadata": metadata,
                "summary": totals,
                "category_breakdown": category_breakdown,
                "transactions": [t.to_dict() for t in transactions],
            }

            duration_ms = (time.time() - start_time) * 1000
            log_operation_success(
                logger,
                "report_generation",
                duration_ms=duration_ms,
                report_type=report_type,
                transaction_count=len(transactions),
                net_amount=f"${totals.get('net', 0):.2f}",
            )

            return report

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_operation_failure(
                logger, "report_generation", e, report_type=report_type, duration_ms=duration_ms
            )
            raise

    def filter_by_date_range(
        self, start_date: str, end_date: str, transaction_type: Optional[str] = None
    ) -> List[Transaction]:
        """
        Filter transactions by date range with caching.

        Uses an in-memory cache to avoid redundant database queries for
        the same date range. Cache is automatically managed (LRU eviction).

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            transaction_type: Optional type filter ('income' or 'expense')

        Returns:
            List of filtered transactions

        Raises:
            ValueError: If dates are invalid
        """
        self._validate_date_range(start_date, end_date)

        # Generate cache key from query parameters
        cache_key = f"{start_date}|{end_date}|{transaction_type or 'all'}"

        # Check cache first
        if cache_key in self._transaction_cache:
            logger.debug(f"Cache hit for date range query: {cache_key}")
            return self._transaction_cache[cache_key]

        logger.debug(
            f"Cache miss, filtering transactions: {start_date} to {end_date}, "
            f"type={transaction_type}"
        )

        # Use TransactionManager query method
        transactions = self.transaction_manager.query_transactions(
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type,
            order_by="date ASC",
        )

        # Cache the result (with size limit)
        if len(self._transaction_cache) >= self._cache_max_size:
            # Remove oldest entry (FIFO eviction)
            oldest_key = next(iter(self._transaction_cache))
            del self._transaction_cache[oldest_key]
            logger.debug(f"Cache full, evicted: {oldest_key}")

        self._transaction_cache[cache_key] = transactions

        logger.debug(f"Found {len(transactions)} transactions in date range (cached)")
        return transactions

    def calculate_totals(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Calculate total income, expenses, and net from transactions.

        Args:
            transactions: List of Transaction objects

        Returns:
            Dictionary with structure:
            {
                'income': Decimal total income,
                'expenses': Decimal total expenses,
                'net': Decimal net (income - expenses),
                'income_formatted': str formatted income,
                'expenses_formatted': str formatted expenses,
                'net_formatted': str formatted net,
                'transaction_count': int count,
                'income_count': int income transaction count,
                'expense_count': int expense transaction count
            }
        """
        if not isinstance(transactions, list):
            raise TypeError(f"Expected list, got {type(transactions)}")

        income_total = Decimal("0.00")
        expense_total = Decimal("0.00")
        income_count = 0
        expense_count = 0

        for transaction in transactions:
            if not isinstance(transaction, Transaction):
                raise TypeError(f"Expected Transaction object, got {type(transaction)}")

            amount = Decimal(str(transaction.amount))

            if transaction.is_income():
                income_total += amount
                income_count += 1
            elif transaction.is_expense():
                expense_total += amount
                expense_count += 1

        net = income_total - expense_total

        logger.debug(
            f"Totals calculated: income=${income_total}, " f"expenses=${expense_total}, net=${net}"
        )

        return {
            "income": income_total,
            "expenses": expense_total,
            "net": net,
            "income_formatted": self.format_currency(income_total),
            "expenses_formatted": self.format_currency(expense_total),
            "net_formatted": self.format_currency(net),
            "transaction_count": len(transactions),
            "income_count": income_count,
            "expense_count": expense_count,
        }

    def group_by_category(
        self, transactions: List[Transaction], transaction_type: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Group transactions by category and calculate totals.

        Args:
            transactions: List of Transaction objects
            transaction_type: Optional filter ('income' or 'expense')

        Returns:
            Dictionary mapping category to totals:
            {
                'category_name': {
                    'total': Decimal amount,
                    'total_formatted': str formatted amount,
                    'count': int transaction count,
                    'percentage': Decimal percentage of total,
                    'percentage_formatted': str formatted percentage
                }
            }
        """
        if not isinstance(transactions, list):
            raise TypeError(f"Expected list, got {type(transactions)}")

        # Filter by type if specified
        if transaction_type:
            transactions = [t for t in transactions if t.type == transaction_type]

        # Group by category (including tax amounts)
        category_totals: Dict[str, Decimal] = {}
        category_tax_totals: Dict[str, Decimal] = {}
        category_counts: Dict[str, int] = {}

        for transaction in transactions:
            if not isinstance(transaction, Transaction):
                raise TypeError(f"Expected Transaction object, got {type(transaction)}")

            category = transaction.category
            amount = Decimal(str(transaction.amount))
            tax_amount = Decimal(str(transaction.tax_amount))

            if category not in category_totals:
                category_totals[category] = Decimal("0.00")
                category_tax_totals[category] = Decimal("0.00")
                category_counts[category] = 0

            category_totals[category] += amount
            category_tax_totals[category] += tax_amount
            category_counts[category] += 1

        # Calculate grand total for percentages (pre-tax for percentage calculation)
        grand_total = sum(category_totals.values(), Decimal("0.00"))

        # Calculate percentages
        percentages = self._calculate_percentages(category_totals, grand_total)

        # Build result (including tax and cash totals)
        result = {}
        for category in sorted(category_totals.keys()):
            cash_total = category_totals[category] + category_tax_totals[category]
            result[category] = {
                "total": category_totals[category],
                "total_formatted": self.format_currency(category_totals[category]),
                "tax_total": category_tax_totals[category],
                "tax_total_formatted": self.format_currency(category_tax_totals[category]),
                "cash_total": cash_total,
                "cash_total_formatted": self.format_currency(cash_total),
                "count": category_counts[category],
                "percentage": percentages[category],
                "percentage_formatted": f"{percentages[category]:.1f}%",
            }

        logger.debug(f"Grouped {len(transactions)} transactions into {len(result)} categories")
        return result

    def format_currency(self, amount: Decimal, currency: Optional[str] = None) -> str:
        """
        Format a Decimal amount as currency string.

        Args:
            amount: Decimal amount to format
            currency: Currency code ('USD' or 'CAD'), defaults to self.currency

        Returns:
            Formatted currency string (e.g., "$1,234.56", "-$500.00")

        Raises:
            TypeError: If amount is not Decimal
            ValueError: If currency is invalid
        """
        if not isinstance(amount, Decimal):
            # Check if it's convertible before attempting conversion
            if not isinstance(amount, (int, float, str)):
                raise TypeError(
                    f"Amount must be Decimal or convertible to Decimal, got {type(amount)}"
                )
            try:
                amount = Decimal(str(amount))
            except Exception as e:
                raise TypeError(f"Amount must be Decimal or convertible to Decimal: {e}")

        if currency is None:
            currency = self.currency

        if currency not in ("USD", "CAD"):
            raise ValueError(f"Invalid currency: {currency}. Must be 'USD' or 'CAD'")

        # Round to 2 decimal places
        amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Handle negative amounts
        is_negative = amount < 0
        abs_amount = abs(amount)

        # Format with thousands separator
        formatted = f"{abs_amount:,.2f}"

        # Add currency symbol
        if currency == "USD":
            symbol = "$"
        else:  # CAD
            symbol = "$"

        # Add negative sign if needed
        if is_negative:
            return f"-{symbol}{formatted}"
        else:
            return f"{symbol}{formatted}"

    def generate_metadata(
        self, start_date: str, end_date: str, transaction_count: int
    ) -> Dict[str, Any]:
        """
        Generate report metadata.

        Args:
            start_date: Report start date (YYYY-MM-DD)
            end_date: Report end date (YYYY-MM-DD)
            transaction_count: Number of transactions in report

        Returns:
            Dictionary with metadata:
            {
                'generated_at': ISO timestamp,
                'start_date': start date,
                'end_date': end date,
                'transaction_count': count,
                'jurisdiction': tax jurisdiction,
                'currency': currency code,
                'fiscal_year': fiscal year if applicable
            }
        """
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "start_date": start_date,
            "end_date": end_date,
            "transaction_count": transaction_count,
            "jurisdiction": self.jurisdiction,
            "currency": self.currency,
        }

        # Add fiscal year if date range is within a fiscal year
        try:
            start = self._parse_date(start_date)
            end = self._parse_date(end_date)

            start_fy = self._get_fiscal_year(start, self.jurisdiction)
            end_fy = self._get_fiscal_year(end, self.jurisdiction)

            if start_fy == end_fy:
                metadata["fiscal_year"] = start_fy
        except Exception as e:
            logger.warning(f"Could not determine fiscal year: {e}")

        logger.debug(f"Generated metadata: {metadata}")
        return metadata

    def _parse_date(self, date_str: str) -> date:
        """
        Parse date string to date object.

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            date object

        Raises:
            ValueError: If date format is invalid
        """
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD. Error: {e}")

    def _validate_date_range(self, start_date: str, end_date: str) -> None:
        """
        Validate that date range is valid.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Raises:
            ValueError: If dates are invalid or start > end
        """
        start = self._parse_date(start_date)
        end = self._parse_date(end_date)

        if start > end:
            raise ValueError(
                f"Start date ({start_date}) must be before or equal to " f"end date ({end_date})"
            )

    def _calculate_percentages(
        self, values: Dict[str, Decimal], total: Decimal
    ) -> Dict[str, Decimal]:
        """
        Calculate percentages for each value relative to total.

        Args:
            values: Dictionary of values
            total: Total to calculate percentages against

        Returns:
            Dictionary mapping keys to percentage values
        """
        if total == 0:
            # Avoid division by zero
            return {key: Decimal("0.00") for key in values}

        percentages = {}
        for key, value in values.items():
            percentage = (value / total * Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            percentages[key] = percentage

        return percentages

    def _get_fiscal_year(self, date_obj: date, jurisdiction: str) -> str:
        """
        Get fiscal year for a date based on tax jurisdiction.

        Args:
            date_obj: Date object
            jurisdiction: Tax jurisdiction ('CRA' or 'IRS')

        Returns:
            Fiscal year string (e.g., 'FY2024')

        Notes:
            - CRA: Fiscal year can vary, but typically calendar year
            - IRS: Fiscal year typically calendar year (Jan 1 - Dec 31)
            For simplicity, both use calendar year
        """
        # For both CRA and IRS, use calendar year
        # In practice, businesses can choose different fiscal year ends
        return f"FY{date_obj.year}"

    def generate_income_statement(
        self, start_date: str, end_date: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate an income statement report.

        An income statement shows revenue, expenses by category, and net income
        for a specified period. This is a standard financial statement suitable
        for tax filing and business analysis.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            **kwargs: Additional options (reserved for future use)

        Returns:
            Dictionary with income statement structure:
            {
                'report_type': 'income_statement',
                'metadata': {...},
                'revenue': {
                    'total': Decimal,
                    'total_formatted': str,
                    'categories': {...}
                },
                'expenses': {
                    'total': Decimal,
                    'total_formatted': str,
                    'categories': {...}
                },
                'net_income': {
                    'amount': Decimal,
                    'amount_formatted': str
                }
            }

        Raises:
            ValueError: If dates are invalid

        Example:
            >>> rg = ReportGenerator(transaction_manager)
            >>> report = rg.generate_income_statement('2025-01-01', '2025-12-31')
            >>> print(report['net_income']['amount_formatted'])
            '$15,000.00'
        """
        logger.info(f"Generating income statement: {start_date} to {end_date}")

        # Validate date range
        self._validate_date_range(start_date, end_date)

        # Get all transactions for the period
        all_transactions = self.filter_by_date_range(start_date=start_date, end_date=end_date)

        # Separate income and expense transactions
        income_transactions = [t for t in all_transactions if t.is_income()]
        expense_transactions = [t for t in all_transactions if t.is_expense()]

        # Calculate revenue section (cash basis - includes tax)
        revenue_total = sum((Decimal(str(t.amount)) for t in income_transactions), Decimal("0.00"))
        revenue_tax_total = sum((Decimal(str(t.tax_amount)) for t in income_transactions), Decimal("0.00"))
        revenue_cash_total = revenue_total + revenue_tax_total
        revenue_by_category = self.group_by_category(income_transactions, transaction_type="income")

        # Calculate expense section (cash basis - includes tax)
        expense_total = sum((Decimal(str(t.amount)) for t in expense_transactions), Decimal("0.00"))
        expense_tax_total = sum((Decimal(str(t.tax_amount)) for t in expense_transactions), Decimal("0.00"))
        expense_cash_total = expense_total + expense_tax_total
        expenses_by_category = self.group_by_category(
            expense_transactions, transaction_type="expense"
        )

        # Calculate net income (multiple views)
        net_income_pretax = revenue_total - expense_total
        net_income_cash = revenue_cash_total - expense_cash_total
        net_tax_position = revenue_tax_total - expense_tax_total

        # Generate metadata
        metadata = self.generate_metadata(
            start_date=start_date, end_date=end_date, transaction_count=len(all_transactions)
        )
        metadata["report_type"] = "income_statement"

        # Build the income statement (cash basis)
        income_statement = {
            "report_type": "income_statement",
            "metadata": metadata,
            "revenue": {
                "total": revenue_total,
                "total_formatted": self.format_currency(revenue_total),
                "tax_total": revenue_tax_total,
                "tax_total_formatted": self.format_currency(revenue_tax_total),
                "cash_total": revenue_cash_total,
                "cash_total_formatted": self.format_currency(revenue_cash_total),
                "transaction_count": len(income_transactions),
                "categories": revenue_by_category,
            },
            "expenses": {
                "total": expense_total,
                "total_formatted": self.format_currency(expense_total),
                "tax_total": expense_tax_total,
                "tax_total_formatted": self.format_currency(expense_tax_total),
                "cash_total": expense_cash_total,
                "cash_total_formatted": self.format_currency(expense_cash_total),
                "transaction_count": len(expense_transactions),
                "categories": expenses_by_category,
            },
            "net_income": {
                "pretax_amount": net_income_pretax,
                "pretax_amount_formatted": self.format_currency(net_income_pretax),
                "cash_amount": net_income_cash,
                "cash_amount_formatted": self.format_currency(net_income_cash),
                "tax_position": net_tax_position,
                "tax_position_formatted": self.format_currency(net_tax_position),
                "is_profit": net_income_cash >= 0,
                # Legacy fields for backward compatibility
                "amount": net_income_cash,
                "amount_formatted": self.format_currency(net_income_cash),
            },
        }

        logger.info(
            f"Income statement generated: Revenue={revenue_cash_total} "
            f"(pre-tax: {revenue_total}, tax: {revenue_tax_total}), "
            f"Expenses={expense_cash_total} (pre-tax: {expense_total}, tax: {expense_tax_total}), "
            f"Net={net_income_cash}"
        )

        return income_statement

    def generate_expense_report(
        self, start_date: str, end_date: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate an expense report grouped by category.

        An expense report shows all expenses organized by tax category with
        totals and percentages. This report is suitable for tax filing and
        includes jurisdiction-specific category codes.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            **kwargs: Additional options (reserved for future use)

        Returns:
            Dictionary with expense report structure:
            {
                'report_type': 'expense_report',
                'metadata': {...},
                'expenses': {
                    'total': Decimal,
                    'total_formatted': str,
                    'transaction_count': int,
                    'categories': {
                        'category_name': {
                            'total': Decimal,
                            'total_formatted': str,
                            'count': int,
                            'percentage': Decimal,
                            'percentage_formatted': str,
                            'tax_code': str (jurisdiction-specific)
                        }
                    }
                }
            }

        Raises:
            ValueError: If dates are invalid

        Example:
            >>> rg = ReportGenerator(transaction_manager)
            >>> report = rg.generate_expense_report('2025-01-01', '2025-12-31')
            >>> print(report['expenses']['total_formatted'])
            '$45,000.00'
        """
        logger.info(f"Generating expense report: {start_date} to {end_date}")

        # Validate date range
        self._validate_date_range(start_date, end_date)

        # Get all transactions for the period
        all_transactions = self.filter_by_date_range(start_date=start_date, end_date=end_date)

        # Filter only expense transactions
        expense_transactions = [t for t in all_transactions if t.is_expense()]

        # Calculate expense total (cash basis - includes tax)
        expense_total = sum((Decimal(str(t.amount)) for t in expense_transactions), Decimal("0.00"))
        expense_tax_total = sum((Decimal(str(t.tax_amount)) for t in expense_transactions), Decimal("0.00"))
        expense_cash_total = expense_total + expense_tax_total

        # Group by category with percentages
        expenses_by_category = self.group_by_category(
            expense_transactions, transaction_type="expense"
        )

        # Add tax codes to categories based on jurisdiction
        expenses_with_tax_codes = self._add_tax_codes_to_categories(expenses_by_category)

        # Generate metadata
        metadata = self.generate_metadata(
            start_date=start_date, end_date=end_date, transaction_count=len(expense_transactions)
        )
        metadata["report_type"] = "expense_report"

        # Build the expense report (cash basis)
        expense_report = {
            "report_type": "expense_report",
            "metadata": metadata,
            "expenses": {
                "total": expense_total,
                "total_formatted": self.format_currency(expense_total),
                "tax_total": expense_tax_total,
                "tax_total_formatted": self.format_currency(expense_tax_total),
                "cash_total": expense_cash_total,
                "cash_total_formatted": self.format_currency(expense_cash_total),
                "transaction_count": len(expense_transactions),
                "categories": expenses_with_tax_codes,
            },
        }

        logger.info(
            f"Expense report generated: {len(expense_transactions)} expenses, "
            f"Total={expense_cash_total} (pre-tax: {expense_total}, tax: {expense_tax_total}), "
            f"Categories={len(expenses_with_tax_codes)}"
        )

        return expense_report

    def _add_tax_codes_to_categories(
        self, categories: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Add jurisdiction-specific tax codes to expense categories.

        Args:
            categories: Dictionary of categories with totals/percentages

        Returns:
            Same dictionary with 'tax_code' field added to each category

        Notes:
            Tax codes are mapped based on self.jurisdiction (CRA or IRS).
            Categories not matching standard codes get a generic code.
        """
        # CRA tax category codes (from CRA T2125 form)
        cra_codes = {
            "Advertising": "8521",
            "Business tax, fees, licenses": "8760",
            "Insurance": "9804",
            "Interest and bank charges": "8710",
            "Meals and entertainment (50% deductible)": "8523",
            "Motor vehicle expenses": "9281",
            "Office expenses": "8810",
            "Supplies": "8811",
            "Legal and professional fees": "8862",
            "Rent": "9220",
            "Salaries and wages": "9060",
            "Telephone and utilities": "9247",
            "Travel": "9200",
            "Other expenses": "9270",
        }

        # IRS tax category codes (from Schedule C)
        irs_codes = {
            "Advertising": "8",
            "Car and truck expenses": "9",
            "Commissions and fees": "10",
            "Contract labor": "11",
            "Depletion": "12",
            "Depreciation": "13",
            "Employee benefit programs": "14",
            "Insurance": "15",
            "Interest (mortgage/other)": "16a/16b",
            "Legal and professional services": "17",
            "Office expense": "18",
            "Office expenses": "18",  # Common variant
            "Pension and profit-sharing plans": "19",
            "Rent or lease": "20a/20b",
            "Repairs and maintenance": "21",
            "Supplies": "22",
            "Taxes and licenses": "23",
            "Travel": "24a/24b",  # Common variant
            "Travel and meals": "24a/24b",
            "Utilities": "25",
            "Wages": "26",
            "Other expenses": "27a",
        }

        # Select codes based on jurisdiction
        tax_codes = cra_codes if self.jurisdiction == "CRA" else irs_codes

        # Add tax codes to categories
        result = {}
        for category, data in categories.items():
            result[category] = data.copy()
            result[category]["tax_code"] = tax_codes.get(category, "OTHER")

        return result

    def generate_tax_summary(
        self, start_date: str, end_date: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate a tax summary report showing taxes collected and paid.

        This report helps users prepare their GST/HST return or tax filing by
        showing all tax amounts collected from customers (output tax) and paid
        to vendors (input tax credits).

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            **kwargs: Additional options (reserved for future use)

        Returns:
            Dictionary with tax summary structure:
            {
                'report_type': 'tax_summary',
                'metadata': {...},
                'tax_collected': {
                    'transactions': [...],
                    'total': Decimal,
                    'total_formatted': str,
                    'count': int
                },
                'tax_paid': {
                    'transactions': [...],
                    'total': Decimal,
                    'total_formatted': str,
                    'count': int
                },
                'net_position': {
                    'amount': Decimal,
                    'amount_formatted': str,
                    'payable': bool
                }
            }

        Raises:
            ValueError: If dates are invalid

        Example:
            >>> rg = ReportGenerator(transaction_manager)
            >>> report = rg.generate_tax_summary('2025-01-01', '2025-03-31')
            >>> print(report['net_position']['amount_formatted'])
            '$1,495.00'

        Notes:
            - This is an informational summary only
            - Consult with tax professional for actual filing
            - Keep original receipts/invoices for audit
        """
        logger.info(f"Generating tax summary: {start_date} to {end_date}")

        # Validate date range
        self._validate_date_range(start_date, end_date)

        # Get all transactions for the period
        all_transactions = self.filter_by_date_range(start_date=start_date, end_date=end_date)

        # Separate income and expense transactions
        income_transactions = [t for t in all_transactions if t.is_income()]
        expense_transactions = [t for t in all_transactions if t.is_expense()]

        # Calculate tax collected (on income)
        tax_collected_total = sum(
            (Decimal(str(t.tax_amount)) for t in income_transactions),
            Decimal("0.00")
        )

        # Build detailed list of tax collected (only include transactions with tax > 0)
        tax_collected_details = [
            {
                "date": t.date,
                "description": t.description or t.category,
                "vendor_customer": t.vendor_customer or "",
                "category": t.category,
                "amount": Decimal(str(t.tax_amount)),
                "amount_formatted": self.format_currency(Decimal(str(t.tax_amount))),
                "document": t.document_filename or "",
            }
            for t in income_transactions if t.tax_amount > 0
        ]

        # Calculate tax paid (on expenses)
        tax_paid_total = sum(
            (Decimal(str(t.tax_amount)) for t in expense_transactions),
            Decimal("0.00")
        )

        # Build detailed list of tax paid (only include transactions with tax > 0)
        tax_paid_details = [
            {
                "date": t.date,
                "description": t.description or t.category,
                "vendor_customer": t.vendor_customer or "",
                "category": t.category,
                "amount": Decimal(str(t.tax_amount)),
                "amount_formatted": self.format_currency(Decimal(str(t.tax_amount))),
                "document": t.document_filename or "",
            }
            for t in expense_transactions if t.tax_amount > 0
        ]

        # Calculate net position
        net_position = tax_collected_total - tax_paid_total

        # Count total transactions with tax
        total_tax_transactions = len(tax_collected_details) + len(tax_paid_details)

        # Generate metadata
        metadata = self.generate_metadata(
            start_date=start_date,
            end_date=end_date,
            transaction_count=total_tax_transactions
        )
        metadata["report_type"] = "tax_summary"
        metadata["jurisdiction"] = self.jurisdiction

        # Build tax summary
        tax_summary = {
            "report_type": "tax_summary",
            "metadata": metadata,
            "tax_collected": {
                "transactions": tax_collected_details,
                "total": tax_collected_total,
                "total_formatted": self.format_currency(tax_collected_total),
                "count": len(tax_collected_details),
            },
            "tax_paid": {
                "transactions": tax_paid_details,
                "total": tax_paid_total,
                "total_formatted": self.format_currency(tax_paid_total),
                "count": len(tax_paid_details),
            },
            "net_position": {
                "amount": net_position,
                "amount_formatted": self.format_currency(net_position),
                "payable": net_position > 0,  # True = owe money, False = refund due
            }
        }

        logger.info(
            f"Tax summary generated: Collected={tax_collected_total}, "
            f"Paid={tax_paid_total}, Net={'payable' if net_position > 0 else 'refundable'}={abs(net_position)}"
        )

        return tax_summary

    def clear_cache(self) -> None:
        """
        Clear the transaction cache.

        Should be called after CRUD operations on transactions to ensure
        fresh data on next query.
        """
        cache_size = len(self._transaction_cache)
        self._transaction_cache.clear()
        if cache_size > 0:
            logger.info(f"Transaction cache cleared ({cache_size} entries removed)")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for performance monitoring.

        Returns:
            Dictionary with cache metrics:
            {
                'size': current number of cached entries,
                'max_size': maximum cache size,
                'utilization': percentage of cache used
            }
        """
        size = len(self._transaction_cache)
        return {
            "size": size,
            "max_size": self._cache_max_size,
            "utilization": (size / self._cache_max_size * 100) if self._cache_max_size > 0 else 0,
        }
