"""
Unit tests for transaction model.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

import pytest
from datetime import datetime
from agentic_bookkeeper.models.transaction import (
    Transaction,
    validate_category,
    get_categories_for_jurisdiction,
    CRA_CATEGORIES,
    IRS_CATEGORIES
)


@pytest.mark.unit
class TestTransaction:
    """Test Transaction model."""

    def test_valid_transaction_creation(self, sample_transaction):
        """Test creating a valid transaction."""
        assert sample_transaction.date == "2025-01-15"
        assert sample_transaction.type == "expense"
        assert sample_transaction.amount == 125.50
        assert sample_transaction.tax_amount == 16.32

    def test_invalid_date_format(self):
        """Test that invalid date format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid date format"):
            Transaction(
                date="01/15/2025",  # Wrong format
                type="expense",
                category="Office expenses",
                amount=100.00
            )

    def test_invalid_type(self):
        """Test that invalid type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid transaction type"):
            Transaction(
                date="2025-01-15",
                type="invalid_type",
                category="Office expenses",
                amount=100.00
            )

    def test_negative_amount(self):
        """Test that negative amount raises ValueError."""
        with pytest.raises(ValueError, match="Amount must be >= 0"):
            Transaction(
                date="2025-01-15",
                type="expense",
                category="Office expenses",
                amount=-100.00
            )

    def test_negative_tax_amount(self):
        """Test that negative tax amount raises ValueError."""
        with pytest.raises(ValueError, match="Tax amount must be >= 0"):
            Transaction(
                date="2025-01-15",
                type="expense",
                category="Office expenses",
                amount=100.00,
                tax_amount=-10.00
            )

    def test_amount_rounding(self):
        """Test that amounts are rounded to 2 decimal places."""
        trans = Transaction(
            date="2025-01-15",
            type="expense",
            category="Office expenses",
            amount=100.999,
            tax_amount=13.005
        )
        assert trans.amount == 101.00
        assert trans.tax_amount == 13.01

    def test_to_dict(self, sample_transaction):
        """Test converting transaction to dictionary."""
        data = sample_transaction.to_dict()

        assert data['date'] == "2025-01-15"
        assert data['type'] == "expense"
        assert data['amount'] == 125.50
        assert 'created_at' in data
        assert 'modified_at' in data

    def test_from_dict(self):
        """Test creating transaction from dictionary."""
        data = {
            'date': '2025-01-15',
            'type': 'expense',
            'category': 'Office expenses',
            'amount': 125.50,
            'tax_amount': 16.32,
            'vendor_customer': 'Test Vendor'
        }

        trans = Transaction.from_dict(data)
        assert trans.date == "2025-01-15"
        assert trans.type == "expense"
        assert trans.amount == 125.50

    def test_transaction_equality(self):
        """Test transaction equality comparison."""
        trans1 = Transaction(
            date="2025-01-15",
            type="expense",
            category="Office expenses",
            amount=100.00
        )

        trans2 = Transaction(
            date="2025-01-15",
            type="expense",
            category="Office expenses",
            amount=100.00
        )

        assert trans1 == trans2

    def test_transaction_sorting(self):
        """Test transaction sorting by date."""
        trans1 = Transaction(date="2025-01-15", type="expense", category="Office", amount=100.00)
        trans2 = Transaction(date="2025-01-20", type="expense", category="Office", amount=100.00)
        trans3 = Transaction(date="2025-01-10", type="expense", category="Office", amount=100.00)

        transactions = [trans1, trans2, trans3]
        sorted_trans = sorted(transactions)

        assert sorted_trans[0].date == "2025-01-10"
        assert sorted_trans[1].date == "2025-01-15"
        assert sorted_trans[2].date == "2025-01-20"

    def test_is_income(self, sample_income_transaction):
        """Test is_income method."""
        assert sample_income_transaction.is_income() is True
        assert sample_income_transaction.is_expense() is False

    def test_is_expense(self, sample_transaction):
        """Test is_expense method."""
        assert sample_transaction.is_expense() is True
        assert sample_transaction.is_income() is False

    def test_get_total_with_tax(self, sample_transaction):
        """Test getting total with tax."""
        total = sample_transaction.get_total_with_tax()
        assert total == 141.82  # 125.50 + 16.32

    def test_update_modified_timestamp(self, sample_transaction):
        """Test updating modified timestamp."""
        original_time = sample_transaction.modified_at
        # Small delay
        import time
        time.sleep(0.01)

        sample_transaction.update_modified_timestamp()
        assert sample_transaction.modified_at != original_time


@pytest.mark.unit
class TestCategories:
    """Test category validation functions."""

    def test_validate_cra_category(self):
        """Test CRA category validation."""
        assert validate_category("Advertising", "CRA") is True
        assert validate_category("Invalid Category", "CRA") is False

    def test_validate_irs_category(self):
        """Test IRS category validation."""
        assert validate_category("Advertising", "IRS") is True
        assert validate_category("Invalid Category", "IRS") is False

    def test_invalid_jurisdiction(self):
        """Test invalid jurisdiction raises error."""
        with pytest.raises(ValueError, match="Invalid jurisdiction"):
            validate_category("Advertising", "INVALID")

    def test_get_cra_categories(self):
        """Test getting CRA categories."""
        categories = get_categories_for_jurisdiction("CRA")
        assert len(categories) > 0
        assert "Advertising" in categories

    def test_get_irs_categories(self):
        """Test getting IRS categories."""
        categories = get_categories_for_jurisdiction("IRS")
        assert len(categories) > 0
        assert "Advertising" in categories
