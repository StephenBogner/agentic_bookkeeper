"""
Unit tests for transaction manager.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

import pytest
from datetime import datetime, timedelta

from agentic_bookkeeper.models.database import Database
from agentic_bookkeeper.models.transaction import Transaction
from agentic_bookkeeper.core.transaction_manager import TransactionManager


@pytest.mark.unit
class TestTransactionManager:
    """Test TransactionManager class."""

    def test_create_transaction(self, database, sample_transaction):
        """Test creating a transaction."""
        tm = TransactionManager(database)
        trans_id = tm.create_transaction(sample_transaction)

        assert trans_id > 0
        assert isinstance(trans_id, int)

    def test_get_transaction(self, database, sample_transaction):
        """Test getting a transaction by ID."""
        tm = TransactionManager(database)
        trans_id = tm.create_transaction(sample_transaction)

        retrieved = tm.get_transaction(trans_id)

        assert retrieved is not None
        assert retrieved.id == trans_id
        assert retrieved.date == sample_transaction.date
        assert retrieved.amount == sample_transaction.amount

    def test_get_nonexistent_transaction(self, database):
        """Test getting a transaction that doesn't exist."""
        tm = TransactionManager(database)
        retrieved = tm.get_transaction(9999)

        assert retrieved is None

    def test_update_transaction(self, database, sample_transaction):
        """Test updating a transaction."""
        tm = TransactionManager(database)
        trans_id = tm.create_transaction(sample_transaction)

        # Get and modify
        trans = tm.get_transaction(trans_id)
        trans.amount = 200.00
        trans.category = "Supplies"

        # Update
        success = tm.update_transaction(trans)
        assert success is True

        # Verify update
        updated = tm.get_transaction(trans_id)
        assert updated.amount == 200.00
        assert updated.category == "Supplies"

    def test_delete_transaction(self, database, sample_transaction):
        """Test deleting a transaction."""
        tm = TransactionManager(database)
        trans_id = tm.create_transaction(sample_transaction)

        # Delete
        success = tm.delete_transaction(trans_id)
        assert success is True

        # Verify deleted
        retrieved = tm.get_transaction(trans_id)
        assert retrieved is None

    def test_delete_nonexistent_transaction(self, database):
        """Test deleting a transaction that doesn't exist."""
        tm = TransactionManager(database)
        success = tm.delete_transaction(9999)

        assert success is False

    def test_query_transactions_by_date_range(self, database, multiple_transactions):
        """Test querying transactions by date range."""
        tm = TransactionManager(database)

        # Create transactions
        for trans in multiple_transactions:
            tm.create_transaction(trans)

        # Query date range
        results = tm.query_transactions(
            start_date="2025-01-15",
            end_date="2025-01-25"
        )

        assert len(results) == 2  # Should get Jan 15 and Jan 20 transactions

    def test_query_transactions_by_type(self, database, multiple_transactions):
        """Test querying transactions by type."""
        tm = TransactionManager(database)

        for trans in multiple_transactions:
            tm.create_transaction(trans)

        # Query expenses only
        expenses = tm.query_transactions(transaction_type='expense')
        assert len(expenses) == 3
        assert all(t.type == 'expense' for t in expenses)

        # Query income only
        income = tm.query_transactions(transaction_type='income')
        assert len(income) == 1
        assert all(t.type == 'income' for t in income)

    def test_query_transactions_by_amount_range(self, database, multiple_transactions):
        """Test querying by amount range."""
        tm = TransactionManager(database)

        for trans in multiple_transactions:
            tm.create_transaction(trans)

        # Query amounts between 100 and 300
        results = tm.query_transactions(min_amount=100, max_amount=300)

        assert len(results) == 2  # Should get 100 and 250 amount transactions

    def test_query_with_limit_and_offset(self, database, multiple_transactions):
        """Test query pagination."""
        tm = TransactionManager(database)

        for trans in multiple_transactions:
            tm.create_transaction(trans)

        # Get first 2
        page1 = tm.query_transactions(limit=2, offset=0, order_by="date ASC")
        assert len(page1) == 2

        # Get next 2
        page2 = tm.query_transactions(limit=2, offset=2, order_by="date ASC")
        assert len(page2) == 2

        # Ensure different results
        assert page1[0].id != page2[0].id

    def test_search_transactions(self, database):
        """Test searching transactions."""
        tm = TransactionManager(database)

        # Create transactions with specific descriptions
        tm.create_transaction(Transaction(
            date="2025-01-01",
            type="expense",
            category="Office",
            description="Office supplies from Staples",
            amount=100.00
        ))

        tm.create_transaction(Transaction(
            date="2025-01-02",
            type="expense",
            category="Office",
            description="Printer paper",
            amount=50.00
        ))

        # Search
        results = tm.search_transactions("supplies")
        assert len(results) >= 1
        assert any("supplies" in (r.description or "").lower() for r in results)

    def test_get_all_transactions(self, database, multiple_transactions):
        """Test getting all transactions."""
        tm = TransactionManager(database)

        for trans in multiple_transactions:
            tm.create_transaction(trans)

        all_trans = tm.get_all_transactions()

        assert len(all_trans) == len(multiple_transactions)

    def test_get_transaction_statistics(self, database, multiple_transactions):
        """Test getting transaction statistics."""
        tm = TransactionManager(database)

        for trans in multiple_transactions:
            tm.create_transaction(trans)

        stats = tm.get_transaction_statistics()

        assert 'income' in stats
        assert 'expense' in stats
        assert 'net' in stats

        # Check income stats
        assert stats['income']['count'] == 1
        assert stats['income']['total'] == 2000.00

        # Check expense stats
        assert stats['expense']['count'] == 3
        assert stats['expense']['total'] == 850.00  # 250 + 100 + 500

        # Check net
        assert stats['net'] == 1150.00  # 2000 - 850

    def test_get_category_summary(self, database, multiple_transactions):
        """Test getting category summary."""
        tm = TransactionManager(database)

        for trans in multiple_transactions:
            tm.create_transaction(trans)

        summary = tm.get_category_summary(transaction_type='expense')

        assert 'Advertising' in summary
        assert 'Office expenses' in summary
        assert 'Travel' in summary

        assert summary['Advertising'] == 250.00
        assert summary['Office expenses'] == 100.00
        assert summary['Travel'] == 500.00

    def test_detect_duplicates(self, database):
        """Test duplicate detection."""
        tm = TransactionManager(database)

        # Create original transaction
        trans1 = Transaction(
            date="2025-01-15",
            type="expense",
            category="Office",
            vendor_customer="Office Depot",
            amount=100.00
        )
        tm.create_transaction(trans1)

        # Create potential duplicate (same amount, vendor, similar date)
        trans2 = Transaction(
            date="2025-01-16",
            type="expense",
            category="Office",
            vendor_customer="Office Depot",
            amount=100.00
        )

        duplicates = tm.detect_duplicates(trans2, time_window_days=7)

        assert len(duplicates) > 0
        assert duplicates[0].vendor_customer == "Office Depot"
        assert abs(duplicates[0].amount - trans2.amount) < 0.01
