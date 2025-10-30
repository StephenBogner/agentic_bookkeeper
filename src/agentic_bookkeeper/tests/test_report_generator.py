"""
Test suite for report_generator module.

Author: Stephen Bogner
Created: 2025-10-29
"""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch

from agentic_bookkeeper.core.report_generator import ReportGenerator
from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.models.transaction import Transaction


class TestReportGeneratorInit:
    """Test ReportGenerator initialization."""

    def test_init_valid_defaults(self):
        """Test initialization with valid parameters and defaults."""
        tm = Mock(spec=TransactionManager)
        rg = ReportGenerator(tm)

        assert rg.transaction_manager is tm
        assert rg.jurisdiction == "IRS"
        assert rg.currency == "USD"
        # Check cache initialization
        assert rg._transaction_cache == {}
        assert rg._cache_max_size == 100

    def test_init_valid_cra_cad(self):
        """Test initialization with CRA and CAD."""
        tm = Mock(spec=TransactionManager)
        rg = ReportGenerator(tm, jurisdiction="CRA", currency="CAD")

        assert rg.transaction_manager is tm
        assert rg.jurisdiction == "CRA"
        assert rg.currency == "CAD"

    def test_init_invalid_transaction_manager(self):
        """Test initialization with invalid transaction manager."""
        with pytest.raises(TypeError, match="Expected TransactionManager"):
            ReportGenerator("not a transaction manager")

    def test_init_invalid_jurisdiction(self):
        """Test initialization with invalid jurisdiction."""
        tm = Mock(spec=TransactionManager)
        with pytest.raises(ValueError, match="Invalid jurisdiction"):
            ReportGenerator(tm, jurisdiction="INVALID")

    def test_init_invalid_currency(self):
        """Test initialization with invalid currency."""
        tm = Mock(spec=TransactionManager)
        with pytest.raises(ValueError, match="Invalid currency"):
            ReportGenerator(tm, currency="EUR")


class TestDateParsing:
    """Test date parsing and validation."""

    @pytest.fixture
    def report_generator(self):
        """Create report generator instance."""
        tm = Mock(spec=TransactionManager)
        return ReportGenerator(tm)

    def test_parse_date_valid(self, report_generator):
        """Test parsing valid date string."""
        result = report_generator._parse_date("2025-10-29")
        assert result == date(2025, 10, 29)

    def test_parse_date_invalid_format(self, report_generator):
        """Test parsing invalid date format."""
        with pytest.raises(ValueError, match="Invalid date format"):
            report_generator._parse_date("10/29/2025")

    def test_parse_date_invalid_date(self, report_generator):
        """Test parsing invalid date values."""
        with pytest.raises(ValueError, match="Invalid date format"):
            report_generator._parse_date("2025-13-45")

    def test_validate_date_range_valid(self, report_generator):
        """Test validating valid date range."""
        # Should not raise
        report_generator._validate_date_range("2025-01-01", "2025-12-31")

    def test_validate_date_range_same_date(self, report_generator):
        """Test validating same start and end date."""
        # Should not raise
        report_generator._validate_date_range("2025-10-29", "2025-10-29")

    def test_validate_date_range_reversed(self, report_generator):
        """Test validating reversed date range."""
        with pytest.raises(ValueError, match="Start date .* must be before"):
            report_generator._validate_date_range("2025-12-31", "2025-01-01")


class TestFilterByDateRange:
    """Test date range filtering."""

    @pytest.fixture
    def report_generator(self):
        """Create report generator with mocked transaction manager."""
        tm = Mock(spec=TransactionManager)
        return ReportGenerator(tm), tm

    def test_filter_by_date_range_valid(self, report_generator):
        """Test filtering by valid date range."""
        rg, tm = report_generator

        # Mock query_transactions to return sample data
        mock_transactions = [
            Transaction(date="2025-10-15", type="income", category="Sales", amount=100.0),
            Transaction(date="2025-10-20", type="expense", category="Office", amount=50.0),
        ]
        tm.query_transactions.return_value = mock_transactions

        result = rg.filter_by_date_range("2025-10-01", "2025-10-31")

        assert len(result) == 2
        tm.query_transactions.assert_called_once_with(
            start_date="2025-10-01",
            end_date="2025-10-31",
            transaction_type=None,
            order_by="date ASC",
        )

    def test_filter_by_date_range_with_type(self, report_generator):
        """Test filtering by date range and transaction type."""
        rg, tm = report_generator

        mock_transactions = [
            Transaction(date="2025-10-15", type="income", category="Sales", amount=100.0)
        ]
        tm.query_transactions.return_value = mock_transactions

        result = rg.filter_by_date_range("2025-10-01", "2025-10-31", transaction_type="income")

        assert len(result) == 1
        tm.query_transactions.assert_called_once_with(
            start_date="2025-10-01",
            end_date="2025-10-31",
            transaction_type="income",
            order_by="date ASC",
        )

    def test_filter_by_date_range_invalid_dates(self, report_generator):
        """Test filtering with invalid date range."""
        rg, tm = report_generator

        with pytest.raises(ValueError):
            rg.filter_by_date_range("2025-12-31", "2025-01-01")

    def test_filter_by_date_range_empty_result(self, report_generator):
        """Test filtering returns empty list."""
        rg, tm = report_generator
        tm.query_transactions.return_value = []

        result = rg.filter_by_date_range("2025-10-01", "2025-10-31")

        assert result == []


class TestCalculateTotals:
    """Test total calculations."""

    @pytest.fixture
    def report_generator(self):
        """Create report generator instance."""
        tm = Mock(spec=TransactionManager)
        return ReportGenerator(tm)

    @pytest.fixture
    def sample_transactions(self):
        """Create sample transactions."""
        return [
            Transaction(date="2025-10-01", type="income", category="Sales", amount=1000.0),
            Transaction(date="2025-10-05", type="income", category="Services", amount=500.0),
            Transaction(date="2025-10-10", type="expense", category="Office", amount=200.0),
            Transaction(date="2025-10-15", type="expense", category="Supplies", amount=150.0),
        ]

    def test_calculate_totals_valid(self, report_generator, sample_transactions):
        """Test calculating totals with valid transactions."""
        result = report_generator.calculate_totals(sample_transactions)

        assert result["income"] == Decimal("1500.00")
        assert result["expenses"] == Decimal("350.00")
        assert result["net"] == Decimal("1150.00")
        assert result["transaction_count"] == 4
        assert result["income_count"] == 2
        assert result["expense_count"] == 2
        assert "$" in result["income_formatted"]
        assert "$" in result["expenses_formatted"]
        assert "$" in result["net_formatted"]

    def test_calculate_totals_empty_list(self, report_generator):
        """Test calculating totals with empty list."""
        result = report_generator.calculate_totals([])

        assert result["income"] == Decimal("0.00")
        assert result["expenses"] == Decimal("0.00")
        assert result["net"] == Decimal("0.00")
        assert result["transaction_count"] == 0
        assert result["income_count"] == 0
        assert result["expense_count"] == 0

    def test_calculate_totals_only_income(self, report_generator):
        """Test calculating totals with only income transactions."""
        transactions = [
            Transaction(date="2025-10-01", type="income", category="Sales", amount=1000.0),
            Transaction(date="2025-10-05", type="income", category="Services", amount=500.0),
        ]

        result = report_generator.calculate_totals(transactions)

        assert result["income"] == Decimal("1500.00")
        assert result["expenses"] == Decimal("0.00")
        assert result["net"] == Decimal("1500.00")
        assert result["income_count"] == 2
        assert result["expense_count"] == 0

    def test_calculate_totals_only_expenses(self, report_generator):
        """Test calculating totals with only expense transactions."""
        transactions = [
            Transaction(date="2025-10-10", type="expense", category="Office", amount=200.0),
            Transaction(date="2025-10-15", type="expense", category="Supplies", amount=150.0),
        ]

        result = report_generator.calculate_totals(transactions)

        assert result["income"] == Decimal("0.00")
        assert result["expenses"] == Decimal("350.00")
        assert result["net"] == Decimal("-350.00")
        assert result["income_count"] == 0
        assert result["expense_count"] == 2

    def test_calculate_totals_negative_net(self, report_generator):
        """Test calculating totals with negative net."""
        transactions = [
            Transaction(date="2025-10-01", type="income", category="Sales", amount=100.0),
            Transaction(date="2025-10-10", type="expense", category="Office", amount=200.0),
        ]

        result = report_generator.calculate_totals(transactions)

        assert result["net"] == Decimal("-100.00")

    def test_calculate_totals_invalid_input_not_list(self, report_generator):
        """Test calculating totals with non-list input."""
        with pytest.raises(TypeError, match="Expected list"):
            report_generator.calculate_totals("not a list")

    def test_calculate_totals_invalid_transaction_type(self, report_generator):
        """Test calculating totals with invalid transaction in list."""
        with pytest.raises(TypeError, match="Expected Transaction object"):
            report_generator.calculate_totals([1, 2, 3])

    def test_calculate_totals_decimal_precision(self, report_generator):
        """Test that calculations maintain 2 decimal precision."""
        transactions = [
            Transaction(date="2025-10-01", type="income", category="Sales", amount=100.33),
            Transaction(date="2025-10-05", type="income", category="Services", amount=200.67),
        ]

        result = report_generator.calculate_totals(transactions)

        assert result["income"] == Decimal("301.00")


class TestGroupByCategory:
    """Test category grouping."""

    @pytest.fixture
    def report_generator(self):
        """Create report generator instance."""
        tm = Mock(spec=TransactionManager)
        return ReportGenerator(tm)

    @pytest.fixture
    def sample_transactions(self):
        """Create sample transactions with multiple categories."""
        return [
            Transaction(date="2025-10-01", type="expense", category="Office", amount=100.0),
            Transaction(date="2025-10-05", type="expense", category="Office", amount=150.0),
            Transaction(date="2025-10-10", type="expense", category="Supplies", amount=50.0),
            Transaction(date="2025-10-15", type="expense", category="Travel", amount=200.0),
        ]

    def test_group_by_category_valid(self, report_generator, sample_transactions):
        """Test grouping by category."""
        result = report_generator.group_by_category(sample_transactions)

        assert len(result) == 3
        assert "Office" in result
        assert "Supplies" in result
        assert "Travel" in result

        assert result["Office"]["total"] == Decimal("250.00")
        assert result["Office"]["count"] == 2
        assert result["Supplies"]["total"] == Decimal("50.00")
        assert result["Supplies"]["count"] == 1
        assert result["Travel"]["total"] == Decimal("200.00")
        assert result["Travel"]["count"] == 1

    def test_group_by_category_with_percentages(self, report_generator, sample_transactions):
        """Test that percentages are calculated correctly."""
        result = report_generator.group_by_category(sample_transactions)

        # Total is 500, so Office (250) should be 50%
        assert result["Office"]["percentage"] == Decimal("50.00")
        assert result["Office"]["percentage_formatted"] == "50.0%"

        # Supplies (50) should be 10%
        assert result["Supplies"]["percentage"] == Decimal("10.00")

        # Travel (200) should be 40%
        assert result["Travel"]["percentage"] == Decimal("40.00")

    def test_group_by_category_empty_list(self, report_generator):
        """Test grouping empty transaction list."""
        result = report_generator.group_by_category([])

        assert result == {}

    def test_group_by_category_single_transaction(self, report_generator):
        """Test grouping single transaction."""
        transactions = [
            Transaction(date="2025-10-01", type="expense", category="Office", amount=100.0)
        ]

        result = report_generator.group_by_category(transactions)

        assert len(result) == 1
        assert result["Office"]["total"] == Decimal("100.00")
        assert result["Office"]["percentage"] == Decimal("100.00")

    def test_group_by_category_with_type_filter(self, report_generator):
        """Test grouping with transaction type filter."""
        transactions = [
            Transaction(date="2025-10-01", type="income", category="Sales", amount=100.0),
            Transaction(date="2025-10-05", type="expense", category="Office", amount=50.0),
            Transaction(date="2025-10-10", type="income", category="Sales", amount=200.0),
        ]

        result = report_generator.group_by_category(transactions, transaction_type="income")

        assert len(result) == 1
        assert "Sales" in result
        assert "Office" not in result
        assert result["Sales"]["total"] == Decimal("300.00")

    def test_group_by_category_invalid_input(self, report_generator):
        """Test grouping with invalid input."""
        with pytest.raises(TypeError, match="Expected list"):
            report_generator.group_by_category("not a list")

    def test_group_by_category_invalid_transaction(self, report_generator):
        """Test grouping with invalid transaction in list."""
        with pytest.raises(TypeError, match="Expected Transaction object"):
            report_generator.group_by_category([1, 2, 3])


class TestFormatCurrency:
    """Test currency formatting."""

    @pytest.fixture
    def report_generator_usd(self):
        """Create report generator with USD."""
        tm = Mock(spec=TransactionManager)
        return ReportGenerator(tm, currency="USD")

    @pytest.fixture
    def report_generator_cad(self):
        """Create report generator with CAD."""
        tm = Mock(spec=TransactionManager)
        return ReportGenerator(tm, jurisdiction="CRA", currency="CAD")

    def test_format_currency_positive_usd(self, report_generator_usd):
        """Test formatting positive USD amount."""
        result = report_generator_usd.format_currency(Decimal("1234.56"))
        assert result == "$1,234.56"

    def test_format_currency_negative_usd(self, report_generator_usd):
        """Test formatting negative USD amount."""
        result = report_generator_usd.format_currency(Decimal("-500.00"))
        assert result == "-$500.00"

    def test_format_currency_zero(self, report_generator_usd):
        """Test formatting zero amount."""
        result = report_generator_usd.format_currency(Decimal("0.00"))
        assert result == "$0.00"

    def test_format_currency_large_amount(self, report_generator_usd):
        """Test formatting large amount with thousands separator."""
        result = report_generator_usd.format_currency(Decimal("1234567.89"))
        assert result == "$1,234,567.89"

    def test_format_currency_cad(self, report_generator_cad):
        """Test formatting CAD amount."""
        result = report_generator_cad.format_currency(Decimal("100.00"))
        assert result == "$100.00"

    def test_format_currency_explicit_currency(self, report_generator_usd):
        """Test formatting with explicit currency override."""
        result = report_generator_usd.format_currency(Decimal("100.00"), currency="CAD")
        assert result == "$100.00"

    def test_format_currency_rounding(self, report_generator_usd):
        """Test that amounts are rounded to 2 decimal places."""
        result = report_generator_usd.format_currency(Decimal("100.999"))
        assert result == "$101.00"

    def test_format_currency_invalid_amount_type(self, report_generator_usd):
        """Test formatting with invalid amount type."""
        with pytest.raises(TypeError, match="must be Decimal"):
            report_generator_usd.format_currency("not a decimal")

    def test_format_currency_invalid_currency(self, report_generator_usd):
        """Test formatting with invalid currency."""
        with pytest.raises(ValueError, match="Invalid currency"):
            report_generator_usd.format_currency(Decimal("100.00"), currency="EUR")

    def test_format_currency_float_conversion(self, report_generator_usd):
        """Test that float/int can be converted to Decimal."""
        result = report_generator_usd.format_currency(100.50)
        assert result == "$100.50"


class TestGenerateMetadata:
    """Test metadata generation."""

    @pytest.fixture
    def report_generator(self):
        """Create report generator instance."""
        tm = Mock(spec=TransactionManager)
        return ReportGenerator(tm, jurisdiction="IRS", currency="USD")

    def test_generate_metadata_valid(self, report_generator):
        """Test generating metadata with valid inputs."""
        result = report_generator.generate_metadata(
            start_date="2025-01-01", end_date="2025-12-31", transaction_count=100
        )

        assert "generated_at" in result
        assert result["start_date"] == "2025-01-01"
        assert result["end_date"] == "2025-12-31"
        assert result["transaction_count"] == 100
        assert result["jurisdiction"] == "IRS"
        assert result["currency"] == "USD"
        assert result["fiscal_year"] == "FY2025"

    def test_generate_metadata_different_fiscal_years(self, report_generator):
        """Test metadata when date range spans multiple fiscal years."""
        result = report_generator.generate_metadata(
            start_date="2024-01-01", end_date="2025-12-31", transaction_count=50
        )

        # Should not include fiscal_year when spanning multiple years
        assert "fiscal_year" not in result or result["fiscal_year"] in ["FY2024", "FY2025"]

    def test_generate_metadata_timestamp_format(self, report_generator):
        """Test that timestamp is in ISO format."""
        result = report_generator.generate_metadata(
            start_date="2025-01-01", end_date="2025-12-31", transaction_count=0
        )

        # Should be able to parse as datetime
        datetime.fromisoformat(result["generated_at"])


class TestCalculatePercentages:
    """Test percentage calculations."""

    @pytest.fixture
    def report_generator(self):
        """Create report generator instance."""
        tm = Mock(spec=TransactionManager)
        return ReportGenerator(tm)

    def test_calculate_percentages_valid(self, report_generator):
        """Test calculating percentages."""
        values = {"A": Decimal("50.00"), "B": Decimal("30.00"), "C": Decimal("20.00")}
        total = Decimal("100.00")

        result = report_generator._calculate_percentages(values, total)

        assert result["A"] == Decimal("50.00")
        assert result["B"] == Decimal("30.00")
        assert result["C"] == Decimal("20.00")

    def test_calculate_percentages_zero_total(self, report_generator):
        """Test calculating percentages with zero total."""
        values = {"A": Decimal("0.00"), "B": Decimal("0.00")}
        total = Decimal("0.00")

        result = report_generator._calculate_percentages(values, total)

        assert result["A"] == Decimal("0.00")
        assert result["B"] == Decimal("0.00")

    def test_calculate_percentages_rounding(self, report_generator):
        """Test that percentages are rounded to 2 decimal places."""
        values = {"A": Decimal("33.33"), "B": Decimal("33.33"), "C": Decimal("33.34")}
        total = Decimal("100.00")

        result = report_generator._calculate_percentages(values, total)

        # Should be rounded properly
        assert result["A"] == Decimal("33.33")
        assert result["B"] == Decimal("33.33")
        assert result["C"] == Decimal("33.34")


class TestGetFiscalYear:
    """Test fiscal year calculation."""

    @pytest.fixture
    def report_generator(self):
        """Create report generator instance."""
        tm = Mock(spec=TransactionManager)
        return ReportGenerator(tm)

    def test_get_fiscal_year_irs(self, report_generator):
        """Test fiscal year for IRS."""
        test_date = date(2025, 6, 15)
        result = report_generator._get_fiscal_year(test_date, "IRS")
        assert result == "FY2025"

    def test_get_fiscal_year_cra(self, report_generator):
        """Test fiscal year for CRA."""
        test_date = date(2025, 6, 15)
        result = report_generator._get_fiscal_year(test_date, "CRA")
        assert result == "FY2025"

    def test_get_fiscal_year_different_years(self, report_generator):
        """Test fiscal year for different years."""
        test_date_2024 = date(2024, 1, 1)
        test_date_2025 = date(2025, 12, 31)

        result_2024 = report_generator._get_fiscal_year(test_date_2024, "IRS")
        result_2025 = report_generator._get_fiscal_year(test_date_2025, "IRS")

        assert result_2024 == "FY2024"
        assert result_2025 == "FY2025"


class TestGenerateReport:
    """Test full report generation."""

    @pytest.fixture
    def report_generator(self):
        """Create report generator with mocked transaction manager."""
        tm = Mock(spec=TransactionManager)
        return ReportGenerator(tm), tm

    @pytest.fixture
    def sample_transactions(self):
        """Create sample transactions."""
        return [
            Transaction(date="2025-10-01", type="income", category="Sales", amount=1000.0),
            Transaction(date="2025-10-10", type="expense", category="Office", amount=200.0),
            Transaction(date="2025-10-15", type="expense", category="Supplies", amount=150.0),
        ]

    def test_generate_report_valid(self, report_generator, sample_transactions):
        """Test generating complete report."""
        rg, tm = report_generator
        tm.query_transactions.return_value = sample_transactions

        result = rg.generate_report(
            report_type="income_statement", start_date="2025-10-01", end_date="2025-10-31"
        )

        # Check structure
        assert "metadata" in result
        assert "summary" in result
        assert "category_breakdown" in result
        assert "transactions" in result

        # Check metadata
        assert result["metadata"]["start_date"] == "2025-10-01"
        assert result["metadata"]["end_date"] == "2025-10-31"
        assert result["metadata"]["transaction_count"] == 3

        # Check summary
        assert result["summary"]["income"] == Decimal("1000.00")
        assert result["summary"]["expenses"] == Decimal("350.00")
        assert result["summary"]["net"] == Decimal("650.00")

        # Check category breakdown
        assert "Office" in result["category_breakdown"]
        assert "Supplies" in result["category_breakdown"]

        # Check transactions
        assert len(result["transactions"]) == 3

    def test_generate_report_invalid_date_range(self, report_generator):
        """Test generating report with invalid date range."""
        rg, tm = report_generator

        with pytest.raises(ValueError):
            rg.generate_report(
                report_type="income_statement", start_date="2025-12-31", end_date="2025-01-01"
            )

    def test_generate_report_empty_transactions(self, report_generator):
        """Test generating report with no transactions."""
        rg, tm = report_generator
        tm.query_transactions.return_value = []

        result = rg.generate_report(
            report_type="income_statement", start_date="2025-10-01", end_date="2025-10-31"
        )

        assert result["metadata"]["transaction_count"] == 0
        assert result["summary"]["income"] == Decimal("0.00")
        assert result["summary"]["expenses"] == Decimal("0.00")
        assert result["summary"]["net"] == Decimal("0.00")
        assert result["category_breakdown"] == {}


class TestPerformance:
    """Test performance requirements."""

    @pytest.fixture
    def report_generator(self):
        """Create report generator with mocked transaction manager."""
        tm = Mock(spec=TransactionManager)
        return ReportGenerator(tm), tm

    @pytest.fixture
    def many_transactions(self):
        """Create 1000 sample transactions."""
        transactions = []
        for i in range(1000):
            transactions.append(
                Transaction(
                    date=f"2025-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                    type="income" if i % 2 == 0 else "expense",
                    category=f"Category{i % 10}",
                    amount=100.0 + (i % 100),
                )
            )
        return transactions

    def test_performance_1000_transactions(self, report_generator, many_transactions):
        """Test that report generation completes in <5 seconds for 1000 transactions."""
        rg, tm = report_generator
        tm.query_transactions.return_value = many_transactions

        import time

        start = time.time()

        result = rg.generate_report(
            report_type="income_statement", start_date="2025-01-01", end_date="2025-12-31"
        )

        duration = time.time() - start

        # Should complete in under 5 seconds
        assert duration < 5.0
        assert result["metadata"]["transaction_count"] == 1000

    def test_performance_totals_calculation(self, report_generator, many_transactions):
        """Test that totals calculation is fast."""
        rg, tm = report_generator

        import time

        start = time.time()

        result = rg.calculate_totals(many_transactions)

        duration = time.time() - start

        # Should complete very quickly (< 0.5 seconds)
        assert duration < 0.5
        assert result["transaction_count"] == 1000

    def test_performance_category_grouping(self, report_generator, many_transactions):
        """Test that category grouping is fast."""
        rg, tm = report_generator

        import time

        start = time.time()

        result = rg.group_by_category(many_transactions)

        duration = time.time() - start

        # Should complete very quickly (< 0.5 seconds)
        assert duration < 0.5
        assert len(result) == 10  # 10 unique categories


class TestIncomeStatement:
    """Test income statement generation."""

    @pytest.fixture
    def report_generator(self):
        """Create report generator with mocked transaction manager."""
        tm = Mock(spec=TransactionManager)
        return ReportGenerator(tm), tm

    @pytest.fixture
    def mixed_transactions(self):
        """Create sample transactions with income and expenses."""
        return [
            Transaction(date="2025-10-01", type="income", category="Sales", amount=5000.0),
            Transaction(date="2025-10-05", type="income", category="Services", amount=3000.0),
            Transaction(date="2025-10-10", type="expense", category="Office", amount=500.0),
            Transaction(date="2025-10-15", type="expense", category="Supplies", amount=300.0),
            Transaction(date="2025-10-20", type="expense", category="Travel", amount=1200.0),
        ]

    def test_income_statement_valid(self, report_generator, mixed_transactions):
        """Test generating valid income statement."""
        rg, tm = report_generator
        tm.query_transactions.return_value = mixed_transactions

        result = rg.generate_income_statement("2025-10-01", "2025-10-31")

        # Check report structure
        assert result["report_type"] == "income_statement"
        assert "metadata" in result
        assert "revenue" in result
        assert "expenses" in result
        assert "net_income" in result

        # Check metadata
        assert result["metadata"]["report_type"] == "income_statement"
        assert result["metadata"]["start_date"] == "2025-10-01"
        assert result["metadata"]["end_date"] == "2025-10-31"
        assert result["metadata"]["transaction_count"] == 5

        # Check revenue
        assert result["revenue"]["total"] == Decimal("8000.00")
        assert result["revenue"]["total_formatted"] == "$8,000.00"
        assert result["revenue"]["transaction_count"] == 2
        assert "Sales" in result["revenue"]["categories"]
        assert "Services" in result["revenue"]["categories"]

        # Check expenses
        assert result["expenses"]["total"] == Decimal("2000.00")
        assert result["expenses"]["total_formatted"] == "$2,000.00"
        assert result["expenses"]["transaction_count"] == 3
        assert "Office" in result["expenses"]["categories"]
        assert "Supplies" in result["expenses"]["categories"]
        assert "Travel" in result["expenses"]["categories"]

        # Check net income
        assert result["net_income"]["amount"] == Decimal("6000.00")
        assert result["net_income"]["amount_formatted"] == "$6,000.00"
        assert result["net_income"]["is_profit"] is True

    def test_income_statement_only_income(self, report_generator):
        """Test income statement with only income transactions."""
        rg, tm = report_generator
        transactions = [
            Transaction(date="2025-10-01", type="income", category="Sales", amount=1000.0),
            Transaction(date="2025-10-05", type="income", category="Services", amount=500.0),
        ]
        tm.query_transactions.return_value = transactions

        result = rg.generate_income_statement("2025-10-01", "2025-10-31")

        assert result["revenue"]["total"] == Decimal("1500.00")
        assert result["expenses"]["total"] == Decimal("0.00")
        assert result["net_income"]["amount"] == Decimal("1500.00")
        assert result["net_income"]["is_profit"] is True

    def test_income_statement_only_expenses(self, report_generator):
        """Test income statement with only expense transactions."""
        rg, tm = report_generator
        transactions = [
            Transaction(date="2025-10-01", type="expense", category="Office", amount=500.0),
            Transaction(date="2025-10-05", type="expense", category="Supplies", amount=300.0),
        ]
        tm.query_transactions.return_value = transactions

        result = rg.generate_income_statement("2025-10-01", "2025-10-31")

        assert result["revenue"]["total"] == Decimal("0.00")
        assert result["expenses"]["total"] == Decimal("800.00")
        assert result["net_income"]["amount"] == Decimal("-800.00")
        assert result["net_income"]["is_profit"] is False

    def test_income_statement_negative_net_income(self, report_generator):
        """Test income statement with expenses greater than revenue."""
        rg, tm = report_generator
        transactions = [
            Transaction(date="2025-10-01", type="income", category="Sales", amount=1000.0),
            Transaction(date="2025-10-10", type="expense", category="Office", amount=2000.0),
        ]
        tm.query_transactions.return_value = transactions

        result = rg.generate_income_statement("2025-10-01", "2025-10-31")

        assert result["net_income"]["amount"] == Decimal("-1000.00")
        assert result["net_income"]["is_profit"] is False
        assert result["net_income"]["amount_formatted"] == "-$1,000.00"

    def test_income_statement_empty_transactions(self, report_generator):
        """Test income statement with no transactions."""
        rg, tm = report_generator
        tm.query_transactions.return_value = []

        result = rg.generate_income_statement("2025-10-01", "2025-10-31")

        assert result["revenue"]["total"] == Decimal("0.00")
        assert result["expenses"]["total"] == Decimal("0.00")
        assert result["net_income"]["amount"] == Decimal("0.00")
        assert result["net_income"]["is_profit"] is True
        assert result["metadata"]["transaction_count"] == 0

    def test_income_statement_category_breakdown(self, report_generator):
        """Test that categories are properly broken down with percentages."""
        rg, tm = report_generator
        transactions = [
            Transaction(date="2025-10-01", type="expense", category="Office", amount=500.0),
            Transaction(date="2025-10-05", type="expense", category="Office", amount=500.0),
            Transaction(date="2025-10-10", type="expense", category="Supplies", amount=1000.0),
        ]
        tm.query_transactions.return_value = transactions

        result = rg.generate_income_statement("2025-10-01", "2025-10-31")

        # Check category breakdown
        office = result["expenses"]["categories"]["Office"]
        supplies = result["expenses"]["categories"]["Supplies"]

        assert office["total"] == Decimal("1000.00")
        assert office["count"] == 2
        assert office["percentage"] == Decimal("50.00")

        assert supplies["total"] == Decimal("1000.00")
        assert supplies["count"] == 1
        assert supplies["percentage"] == Decimal("50.00")

    def test_income_statement_multiple_income_categories(self, report_generator):
        """Test income statement with multiple income categories."""
        rg, tm = report_generator
        transactions = [
            Transaction(date="2025-10-01", type="income", category="Sales", amount=3000.0),
            Transaction(date="2025-10-05", type="income", category="Services", amount=2000.0),
            Transaction(date="2025-10-10", type="income", category="Interest", amount=100.0),
        ]
        tm.query_transactions.return_value = transactions

        result = rg.generate_income_statement("2025-10-01", "2025-10-31")

        assert len(result["revenue"]["categories"]) == 3
        assert result["revenue"]["categories"]["Sales"]["total"] == Decimal("3000.00")
        assert result["revenue"]["categories"]["Services"]["total"] == Decimal("2000.00")
        assert result["revenue"]["categories"]["Interest"]["total"] == Decimal("100.00")

    def test_income_statement_invalid_date_range(self, report_generator):
        """Test income statement with invalid date range."""
        rg, tm = report_generator

        with pytest.raises(ValueError):
            rg.generate_income_statement("2025-12-31", "2025-01-01")

    def test_income_statement_professional_formatting(self, report_generator, mixed_transactions):
        """Test that income statement has professional formatting."""
        rg, tm = report_generator
        tm.query_transactions.return_value = mixed_transactions

        result = rg.generate_income_statement("2025-10-01", "2025-10-31")

        # Check all currency values are formatted
        assert "$" in result["revenue"]["total_formatted"]
        assert "$" in result["expenses"]["total_formatted"]
        assert "$" in result["net_income"]["amount_formatted"]

        # Check all category values are formatted
        for category in result["revenue"]["categories"].values():
            assert "$" in category["total_formatted"]

        for category in result["expenses"]["categories"].values():
            assert "$" in category["total_formatted"]

    def test_income_statement_suitable_for_tax_filing(self, report_generator, mixed_transactions):
        """Test that income statement contains all info needed for tax filing."""
        rg, tm = report_generator
        tm.query_transactions.return_value = mixed_transactions

        result = rg.generate_income_statement("2025-10-01", "2025-10-31")

        # Must have metadata for tax purposes
        assert "jurisdiction" in result["metadata"]
        assert result["metadata"]["jurisdiction"] in ("CRA", "IRS")
        assert "start_date" in result["metadata"]
        assert "end_date" in result["metadata"]
        assert "generated_at" in result["metadata"]

        # Must have complete financial breakdown
        assert "revenue" in result
        assert "expenses" in result
        assert "net_income" in result

        # Categories must be itemized for tax deductions
        assert "categories" in result["revenue"]
        assert "categories" in result["expenses"]

    def test_income_statement_fiscal_year(self, report_generator, mixed_transactions):
        """Test that fiscal year is included when appropriate."""
        rg, tm = report_generator
        tm.query_transactions.return_value = mixed_transactions

        # Date range within same fiscal year
        result = rg.generate_income_statement("2025-01-01", "2025-12-31")

        assert "fiscal_year" in result["metadata"]
        assert result["metadata"]["fiscal_year"] == "FY2025"

    def test_income_statement_transaction_counts(self, report_generator, mixed_transactions):
        """Test that transaction counts are accurate."""
        rg, tm = report_generator
        tm.query_transactions.return_value = mixed_transactions

        result = rg.generate_income_statement("2025-10-01", "2025-10-31")

        assert result["revenue"]["transaction_count"] == 2
        assert result["expenses"]["transaction_count"] == 3
        assert result["metadata"]["transaction_count"] == 5


class TestExpenseReport:
    """Test expense report generation."""

    @pytest.fixture
    def report_generator_irs(self):
        """Create report generator with IRS jurisdiction."""
        tm = Mock(spec=TransactionManager)
        return ReportGenerator(tm, jurisdiction="IRS", currency="USD"), tm

    @pytest.fixture
    def report_generator_cra(self):
        """Create report generator with CRA jurisdiction."""
        tm = Mock(spec=TransactionManager)
        return ReportGenerator(tm, jurisdiction="CRA", currency="CAD"), tm

    @pytest.fixture
    def expense_transactions(self):
        """Create sample expense transactions."""
        return [
            Transaction(
                date="2025-10-01", type="expense", category="Office expenses", amount=500.0
            ),
            Transaction(date="2025-10-05", type="expense", category="Supplies", amount=300.0),
            Transaction(date="2025-10-10", type="expense", category="Travel", amount=1200.0),
            Transaction(
                date="2025-10-15", type="expense", category="Office expenses", amount=500.0
            ),
        ]

    def test_expense_report_valid(self, report_generator_irs, expense_transactions):
        """Test generating valid expense report."""
        rg, tm = report_generator_irs
        tm.query_transactions.return_value = expense_transactions

        result = rg.generate_expense_report("2025-10-01", "2025-10-31")

        # Check report structure
        assert result["report_type"] == "expense_report"
        assert "metadata" in result
        assert "expenses" in result

        # Check metadata
        assert result["metadata"]["report_type"] == "expense_report"
        assert result["metadata"]["start_date"] == "2025-10-01"
        assert result["metadata"]["end_date"] == "2025-10-31"
        assert result["metadata"]["transaction_count"] == 4

        # Check expenses
        assert result["expenses"]["total"] == Decimal("2500.00")
        assert result["expenses"]["total_formatted"] == "$2,500.00"
        assert result["expenses"]["transaction_count"] == 4

        # Check categories
        assert "Office expenses" in result["expenses"]["categories"]
        assert "Supplies" in result["expenses"]["categories"]
        assert "Travel" in result["expenses"]["categories"]

    def test_expense_report_grouping(self, report_generator_irs, expense_transactions):
        """Test that expenses are properly grouped by category."""
        rg, tm = report_generator_irs
        tm.query_transactions.return_value = expense_transactions

        result = rg.generate_expense_report("2025-10-01", "2025-10-31")

        categories = result["expenses"]["categories"]

        # Check Office expenses (two transactions)
        assert categories["Office expenses"]["total"] == Decimal("1000.00")
        assert categories["Office expenses"]["count"] == 2
        assert categories["Office expenses"]["percentage"] == Decimal("40.00")

        # Check Supplies (one transaction)
        assert categories["Supplies"]["total"] == Decimal("300.00")
        assert categories["Supplies"]["count"] == 1
        assert categories["Supplies"]["percentage"] == Decimal("12.00")

        # Check Travel (one transaction)
        assert categories["Travel"]["total"] == Decimal("1200.00")
        assert categories["Travel"]["count"] == 1
        assert categories["Travel"]["percentage"] == Decimal("48.00")

    def test_expense_report_tax_codes_irs(self, report_generator_irs, expense_transactions):
        """Test that IRS tax codes are included."""
        rg, tm = report_generator_irs
        tm.query_transactions.return_value = expense_transactions

        result = rg.generate_expense_report("2025-10-01", "2025-10-31")

        categories = result["expenses"]["categories"]

        # Check IRS tax codes
        assert categories["Office expenses"]["tax_code"] == "18"
        assert categories["Supplies"]["tax_code"] == "22"
        assert categories["Travel"]["tax_code"] == "24a/24b"

    def test_expense_report_tax_codes_cra(self, report_generator_cra):
        """Test that CRA tax codes are included."""
        rg, tm = report_generator_cra
        transactions = [
            Transaction(
                date="2025-10-01", type="expense", category="Office expenses", amount=500.0
            ),
            Transaction(date="2025-10-05", type="expense", category="Advertising", amount=300.0),
        ]
        tm.query_transactions.return_value = transactions

        result = rg.generate_expense_report("2025-10-01", "2025-10-31")

        categories = result["expenses"]["categories"]

        # Check CRA tax codes
        assert categories["Office expenses"]["tax_code"] == "8810"
        assert categories["Advertising"]["tax_code"] == "8521"

    def test_expense_report_unknown_category(self, report_generator_irs):
        """Test handling of unknown category."""
        rg, tm = report_generator_irs
        transactions = [
            Transaction(
                date="2025-10-01", type="expense", category="Unknown Category", amount=100.0
            )
        ]
        tm.query_transactions.return_value = transactions

        result = rg.generate_expense_report("2025-10-01", "2025-10-31")

        # Unknown categories get "OTHER" tax code
        assert result["expenses"]["categories"]["Unknown Category"]["tax_code"] == "OTHER"

    def test_expense_report_empty(self, report_generator_irs):
        """Test expense report with no expenses."""
        rg, tm = report_generator_irs
        tm.query_transactions.return_value = []

        result = rg.generate_expense_report("2025-10-01", "2025-10-31")

        assert result["expenses"]["total"] == Decimal("0.00")
        assert result["expenses"]["transaction_count"] == 0
        assert result["expenses"]["categories"] == {}

    def test_expense_report_filters_income(self, report_generator_irs):
        """Test that expense report excludes income transactions."""
        rg, tm = report_generator_irs
        transactions = [
            Transaction(date="2025-10-01", type="income", category="Sales", amount=1000.0),
            Transaction(
                date="2025-10-05", type="expense", category="Office expenses", amount=500.0
            ),
        ]
        tm.query_transactions.return_value = transactions

        result = rg.generate_expense_report("2025-10-01", "2025-10-31")

        # Only expense transaction should be included
        assert result["expenses"]["total"] == Decimal("500.00")
        assert result["expenses"]["transaction_count"] == 1
        assert "Sales" not in result["expenses"]["categories"]
        assert "Office expenses" in result["expenses"]["categories"]

    def test_expense_report_percentages_sum_to_100(
        self, report_generator_irs, expense_transactions
    ):
        """Test that percentages sum to approximately 100%."""
        rg, tm = report_generator_irs
        tm.query_transactions.return_value = expense_transactions

        result = rg.generate_expense_report("2025-10-01", "2025-10-31")

        # Sum all percentages
        total_percentage = sum(
            cat["percentage"] for cat in result["expenses"]["categories"].values()
        )

        # Should be exactly 100 (or very close due to rounding)
        assert abs(total_percentage - Decimal("100.00")) < Decimal("0.01")

    def test_expense_report_invalid_date_range(self, report_generator_irs):
        """Test expense report with invalid date range."""
        rg, tm = report_generator_irs

        with pytest.raises(ValueError):
            rg.generate_expense_report("2025-12-31", "2025-01-01")

    def test_expense_report_suitable_for_tax_filing(
        self, report_generator_irs, expense_transactions
    ):
        """Test that expense report contains all info needed for tax filing."""
        rg, tm = report_generator_irs
        tm.query_transactions.return_value = expense_transactions

        result = rg.generate_expense_report("2025-10-01", "2025-10-31")

        # Must have metadata for tax purposes
        assert "jurisdiction" in result["metadata"]
        assert result["metadata"]["jurisdiction"] == "IRS"
        assert "start_date" in result["metadata"]
        assert "end_date" in result["metadata"]
        assert "generated_at" in result["metadata"]

        # Must have complete financial breakdown
        assert "expenses" in result
        assert "total" in result["expenses"]
        assert "categories" in result["expenses"]

        # All categories must have tax codes
        for category in result["expenses"]["categories"].values():
            assert "tax_code" in category
            assert category["tax_code"] is not None

    def test_expense_report_formatting(self, report_generator_irs, expense_transactions):
        """Test that expense report has professional formatting."""
        rg, tm = report_generator_irs
        tm.query_transactions.return_value = expense_transactions

        result = rg.generate_expense_report("2025-10-01", "2025-10-31")

        # Check currency formatting
        assert "$" in result["expenses"]["total_formatted"]

        # Check all categories have formatted values
        for category in result["expenses"]["categories"].values():
            assert "$" in category["total_formatted"]
            assert "%" in category["percentage_formatted"]


class TestReportGeneratorCaching:
    """Test ReportGenerator caching functionality."""

    @pytest.fixture
    def report_generator_with_cache(self):
        """Create report generator with mocked transaction manager."""
        tm = Mock(spec=TransactionManager)
        rg = ReportGenerator(tm, jurisdiction="IRS", currency="USD")
        return rg, tm

    def test_cache_hit_on_repeated_query(self, report_generator_with_cache):
        """Test that repeated queries use cache."""
        rg, tm = report_generator_with_cache

        # Create mock transactions
        transactions = [
            Transaction(
                date="2025-10-01",
                type="income",
                category="Consulting",
                vendor_customer="Client A",
                description="Services",
                amount=1000.0,
            )
        ]
        tm.query_transactions.return_value = transactions

        # First query - should hit database
        result1 = rg.filter_by_date_range("2025-10-01", "2025-10-31")
        assert tm.query_transactions.call_count == 1
        assert result1 == transactions

        # Second query with same parameters - should hit cache
        result2 = rg.filter_by_date_range("2025-10-01", "2025-10-31")
        assert tm.query_transactions.call_count == 1  # Not called again
        assert result2 == transactions

    def test_cache_miss_on_different_dates(self, report_generator_with_cache):
        """Test that different date ranges don't hit cache."""
        rg, tm = report_generator_with_cache

        transactions1 = [
            Transaction(
                date="2025-10-01",
                type="income",
                category="Consulting",
                vendor_customer="Client A",
                description="Services",
                amount=1000.0,
            )
        ]
        transactions2 = [
            Transaction(
                date="2025-11-01",
                type="income",
                category="Consulting",
                vendor_customer="Client B",
                description="Services",
                amount=2000.0,
            )
        ]

        tm.query_transactions.side_effect = [transactions1, transactions2]

        # First query
        result1 = rg.filter_by_date_range("2025-10-01", "2025-10-31")
        assert tm.query_transactions.call_count == 1

        # Second query with different dates
        result2 = rg.filter_by_date_range("2025-11-01", "2025-11-30")
        assert tm.query_transactions.call_count == 2  # Called again

    def test_cache_respects_transaction_type(self, report_generator_with_cache):
        """Test that cache keys include transaction type."""
        rg, tm = report_generator_with_cache

        transactions_all = [
            Transaction(
                date="2025-10-01",
                type="income",
                category="Consulting",
                vendor_customer="Client A",
                description="Services",
                amount=1000.0,
            )
        ]
        transactions_income = [transactions_all[0]]

        tm.query_transactions.side_effect = [transactions_all, transactions_income]

        # Query without type filter
        result1 = rg.filter_by_date_range("2025-10-01", "2025-10-31")
        assert tm.query_transactions.call_count == 1

        # Query with type filter - different cache key
        result2 = rg.filter_by_date_range("2025-10-01", "2025-10-31", transaction_type="income")
        assert tm.query_transactions.call_count == 2  # Called again

    def test_cache_clear(self, report_generator_with_cache):
        """Test that cache can be cleared."""
        rg, tm = report_generator_with_cache

        transactions = [
            Transaction(
                date="2025-10-01",
                type="income",
                category="Consulting",
                vendor_customer="Client A",
                description="Services",
                amount=1000.0,
            )
        ]
        tm.query_transactions.return_value = transactions

        # Populate cache
        rg.filter_by_date_range("2025-10-01", "2025-10-31")
        assert len(rg._transaction_cache) == 1

        # Clear cache
        rg.clear_cache()
        assert len(rg._transaction_cache) == 0

        # Next query should hit database again
        rg.filter_by_date_range("2025-10-01", "2025-10-31")
        assert tm.query_transactions.call_count == 2

    def test_cache_max_size_eviction(self, report_generator_with_cache):
        """Test that cache evicts old entries when full."""
        rg, tm = report_generator_with_cache

        # Set small cache size for testing
        rg._cache_max_size = 3

        transactions = [
            Transaction(
                date="2025-10-01",
                type="income",
                category="Consulting",
                vendor_customer="Client A",
                description="Services",
                amount=1000.0,
            )
        ]
        tm.query_transactions.return_value = transactions

        # Fill cache to max
        rg.filter_by_date_range("2025-01-01", "2025-01-31")
        rg.filter_by_date_range("2025-02-01", "2025-02-28")
        rg.filter_by_date_range("2025-03-01", "2025-03-31")
        assert len(rg._transaction_cache) == 3

        # Add one more - should evict oldest
        rg.filter_by_date_range("2025-04-01", "2025-04-30")
        assert len(rg._transaction_cache) == 3  # Still 3

        # First entry should be evicted, so re-query should hit database
        rg.filter_by_date_range("2025-01-01", "2025-01-31")
        # Should have been called 5 times total (4 unique + 1 repeat that was evicted)
        assert tm.query_transactions.call_count == 5

    def test_get_cache_stats(self, report_generator_with_cache):
        """Test cache statistics."""
        rg, tm = report_generator_with_cache

        # Empty cache
        stats = rg.get_cache_stats()
        assert stats["size"] == 0
        assert stats["max_size"] == 100
        assert stats["utilization"] == 0

        # Add some entries
        transactions = [
            Transaction(
                date="2025-10-01",
                type="income",
                category="Consulting",
                vendor_customer="Client A",
                description="Services",
                amount=1000.0,
            )
        ]
        tm.query_transactions.return_value = transactions

        rg.filter_by_date_range("2025-10-01", "2025-10-31")
        rg.filter_by_date_range("2025-11-01", "2025-11-30")

        stats = rg.get_cache_stats()
        assert stats["size"] == 2
        assert stats["max_size"] == 100
        assert stats["utilization"] == 2.0  # 2/100 * 100
