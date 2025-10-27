"""
Pytest configuration and fixtures for Agentic Bookkeeper tests.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_bookkeeper.models.database import Database
from agentic_bookkeeper.models.transaction import Transaction


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def test_db_path(temp_dir):
    """Provide a temporary database path."""
    return temp_dir / "test_bookkeeper.db"


@pytest.fixture
def database(test_db_path):
    """Create a test database instance."""
    db = Database(str(test_db_path))
    db.initialize_schema()
    yield db
    db.close()


@pytest.fixture
def sample_transaction():
    """Create a sample transaction for testing."""
    return Transaction(
        date="2025-01-15",
        type="expense",
        category="Office expenses",
        vendor_customer="Office Depot",
        description="Printer paper and ink",
        amount=125.50,
        tax_amount=16.32,
        document_filename="receipt_20250115.pdf"
    )


@pytest.fixture
def sample_income_transaction():
    """Create a sample income transaction."""
    return Transaction(
        date="2025-01-20",
        type="income",
        category="Consulting Services",
        vendor_customer="ABC Corp",
        description="Software consulting - January 2025",
        amount=5000.00,
        tax_amount=650.00,
        document_filename="invoice_20250120.pdf"
    )


@pytest.fixture
def multiple_transactions():
    """Create multiple sample transactions for testing."""
    return [
        Transaction(
            date="2025-01-10",
            type="expense",
            category="Advertising",
            vendor_customer="Google Ads",
            amount=250.00,
            tax_amount=32.50
        ),
        Transaction(
            date="2025-01-15",
            type="expense",
            category="Office expenses",
            amount=100.00,
            tax_amount=13.00
        ),
        Transaction(
            date="2025-01-20",
            type="income",
            category="Consulting",
            amount=2000.00,
            tax_amount=260.00
        ),
        Transaction(
            date="2025-01-25",
            type="expense",
            category="Travel",
            amount=500.00,
            tax_amount=65.00
        ),
    ]
