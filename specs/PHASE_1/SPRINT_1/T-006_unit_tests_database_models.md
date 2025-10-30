# Task Specification: T-006

**Task Name:** Unit Tests for Database & Models
**Task ID:** T-006
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 1: Project Setup & Database Foundation
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 4 hours
**Dependencies:** T-002, T-003, T-004

---

## OBJECTIVE

Create comprehensive unit tests for the database layer, transaction model, and configuration management to ensure >80% code coverage and validate all functionality with test fixtures for sample data.

**Success Criteria:**
- All tests pass
- Coverage >80% for database and model modules
- Test fixtures provide realistic data
- Edge cases are tested
- Tests are isolated and repeatable

---

## REQUIREMENTS

### Functional Requirements

1. **Database Tests (test_database.py)**
   - Test database initialization
   - Test table creation
   - Test transaction CRUD operations
   - Test config table operations
   - Test backup functionality
   - Test connection management
   - Test error handling

2. **Transaction Model Tests (test_transaction.py)**
   - Test transaction creation with valid data
   - Test transaction validation (date, amount, type)
   - Test serialization (to_dict, from_dict)
   - Test string representations (__str__, __repr__)
   - Test comparison methods
   - Test business logic methods
   - Test edge cases (None values, boundaries)

3. **Configuration Tests (test_config.py)**
   - Test configuration loading
   - Test API key encryption/decryption
   - Test category loading
   - Test configuration validation
   - Test environment variable loading
   - Test database persistence

4. **Test Fixtures**
   - Sample transaction data
   - Sample configuration data
   - Mock API responses
   - Temporary database for testing

### Non-Functional Requirements

- Tests run in <30 seconds total
- Tests are isolated (no shared state)
- Tests use temporary files/databases
- Tests clean up after themselves
- Tests are deterministic (no flaky tests)

---

## DESIGN CONSIDERATIONS

### Test Structure

```python
"""
Module: test_database
Purpose: Unit tests for database module
Author: Stephen Bogner
Created: 2025-10-29
"""

import pytest
import sqlite3
from pathlib import Path
import tempfile
import os

from src.agentic_bookkeeper.models.database import Database


class TestDatabase:
    """Test cases for Database class."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        db = Database(db_path)
        db.initialize_schema()

        yield db

        db.close()
        os.unlink(db_path)

    def test_database_initialization(self, temp_db):
        """Test database creates successfully."""
        assert temp_db is not None
        # Verify tables exist
        cursor = temp_db.connect().cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert 'transactions' in tables
        assert 'config' in tables

    def test_transaction_crud(self, temp_db):
        """Test CRUD operations on transactions table."""
        # Insert
        # Update
        # Read
        # Delete
        pass

    def test_backup(self, temp_db):
        """Test database backup functionality."""
        pass
```

### pytest Configuration

**conftest.py:**
```python
"""
Shared pytest fixtures and configuration.
"""

import pytest
from datetime import datetime, timedelta
from typing import List

from src.agentic_bookkeeper.models.transaction import Transaction


@pytest.fixture
def sample_transaction():
    """Create a sample transaction for testing."""
    return Transaction(
        date='2025-10-29',
        type='expense',
        category='Office Supplies',
        amount=100.50,
        tax_amount=13.07,
        vendor_customer='Office Depot',
        description='Printer paper and toner'
    )


@pytest.fixture
def sample_transactions() -> List[Transaction]:
    """Create multiple sample transactions."""
    transactions = []
    base_date = datetime(2025, 10, 1)

    # Income transactions
    for i in range(5):
        date = (base_date + timedelta(days=i*2)).strftime('%Y-%m-%d')
        transactions.append(Transaction(
            date=date,
            type='income',
            category='Sales',
            amount=500.0 + (i * 100),
            vendor_customer=f'Customer {i+1}',
            description=f'Invoice {i+1}'
        ))

    # Expense transactions
    for i in range(5):
        date = (base_date + timedelta(days=i*2+1)).strftime('%Y-%m-%d')
        transactions.append(Transaction(
            date=date,
            type='expense',
            category='Office Supplies',
            amount=50.0 + (i * 10),
            tax_amount=6.5 + (i * 1.3),
            vendor_customer=f'Vendor {i+1}',
            description=f'Purchase {i+1}'
        ))

    return transactions


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary config directory with category files."""
    config_dir = tmp_path / 'config'
    config_dir.mkdir()

    # Create minimal category files
    cra_cats = {
        'meta': {'jurisdiction': 'CRA'},
        'income_categories': {'SALES': 'Sales'},
        'expense_categories': {'OFFICE': 'Office'}
    }

    irs_cats = {
        'meta': {'jurisdiction': 'IRS'},
        'income_categories': {'GROSS_RECEIPTS': 'Gross receipts'},
        'expense_categories': {'OFFICE_EXPENSE': 'Office expense'}
    }

    import json
    with open(config_dir / 'categories_cra.json', 'w') as f:
        json.dump(cra_cats, f)

    with open(config_dir / 'categories_irs.json', 'w') as f:
        json.dump(irs_cats, f)

    return config_dir
```

---

## ACCEPTANCE CRITERIA

### Must Have
- [ ] test_database.py created with comprehensive tests
- [ ] test_transaction.py created with validation tests
- [ ] test_config.py created with configuration tests
- [ ] conftest.py created with shared fixtures
- [ ] All tests pass
- [ ] Coverage >80% for database.py
- [ ] Coverage >80% for transaction.py
- [ ] Coverage >80% for config.py
- [ ] Tests use fixtures for sample data
- [ ] Tests are isolated and clean up properly

### Should Have
- [ ] Edge case testing (empty data, None values)
- [ ] Error condition testing
- [ ] Parametrized tests for multiple scenarios
- [ ] Performance benchmarks

### Nice to Have
- [ ] Integration tests between components
- [ ] Property-based testing with hypothesis
- [ ] Mutation testing
- [ ] Test documentation

---

## CONTEXT REQUIRED

### Information Needed
- pytest best practices
- Coverage targets (80%)
- Test fixture patterns

### Artifacts from Previous Tasks
- T-002: Database module
- T-003: Transaction model
- T-004: Configuration management

---

## EXPECTED DELIVERABLES

### Files to Create
- `src/agentic_bookkeeper/tests/test_database.py` - Database tests
- `src/agentic_bookkeeper/tests/test_transaction.py` - Transaction model tests
- `src/agentic_bookkeeper/tests/test_config.py` - Configuration tests
- `src/agentic_bookkeeper/tests/conftest.py` - Shared fixtures

### Files to Modify
- None (new test files)

---

## VALIDATION COMMANDS

```bash
# Run all tests
pytest src/agentic_bookkeeper/tests/ -v

# Run with coverage
pytest src/agentic_bookkeeper/tests/ --cov=src/agentic_bookkeeper/models --cov=src/agentic_bookkeeper/utils --cov-report=html

# Run specific test file
pytest src/agentic_bookkeeper/tests/test_database.py -v

# Run with detailed output
pytest src/agentic_bookkeeper/tests/ -vv --tb=short

# Check coverage percentage
pytest --cov=src/agentic_bookkeeper/models --cov=src/agentic_bookkeeper/utils --cov-report=term-missing

# Run tests in parallel (if pytest-xdist installed)
pytest src/agentic_bookkeeper/tests/ -n auto
```

---

## IMPLEMENTATION NOTES

### Test Categories

1. **Happy Path Tests**
   - Valid data scenarios
   - Expected behavior
   - Common use cases

2. **Validation Tests**
   - Invalid dates
   - Negative amounts
   - Wrong types
   - Missing required fields

3. **Edge Cases**
   - Empty strings
   - None values
   - Boundary values
   - Zero amounts

4. **Error Handling**
   - Database connection errors
   - File not found
   - Invalid JSON
   - Decryption failures

### Example Test Cases

```python
def test_transaction_valid_creation(sample_transaction):
    """Test creating transaction with valid data."""
    assert sample_transaction.date == '2025-10-29'
    assert sample_transaction.amount == 100.50
    assert sample_transaction.type == 'expense'


def test_transaction_invalid_date():
    """Test transaction with invalid date raises error."""
    with pytest.raises(ValueError, match='Invalid date'):
        Transaction(
            date='2025-13-45',  # Invalid date
            type='expense',
            category='Office',
            amount=100.0
        )


def test_transaction_negative_amount():
    """Test negative amount raises error."""
    with pytest.raises(ValueError, match='non-negative'):
        Transaction(
            date='2025-10-29',
            type='expense',
            category='Office',
            amount=-100.0
        )


def test_transaction_serialization(sample_transaction):
    """Test to_dict and from_dict."""
    data = sample_transaction.to_dict()
    assert isinstance(data, dict)
    assert data['amount'] == 100.50

    reconstructed = Transaction.from_dict(data)
    assert reconstructed.amount == sample_transaction.amount
    assert reconstructed.date == sample_transaction.date


@pytest.mark.parametrize('amount,tax,expected', [
    (100.0, 0.0, 100.0),
    (100.0, 13.0, 113.0),
    (50.50, 6.57, 57.07),
])
def test_transaction_total_calculation(amount, tax, expected):
    """Test total amount calculation with various inputs."""
    t = Transaction(
        date='2025-10-29',
        type='expense',
        category='Office',
        amount=amount,
        tax_amount=tax
    )
    assert t.get_total_amount() == pytest.approx(expected)
```

---

## NOTES

### Important Considerations

- Use temporary files/databases for isolation
- Clean up resources in fixtures (yield pattern)
- Use pytest.raises for exception testing
- Parametrize tests for multiple scenarios
- Mock external dependencies (file system, network)
- Test both success and failure paths

### Potential Issues

- **Issue:** Tests depend on each other (shared state)
  - **Solution:** Use fixtures for isolation

- **Issue:** Tests fail randomly (timing issues)
  - **Solution:** Avoid time-dependent tests, use freezegun if needed

- **Issue:** Database files left behind
  - **Solution:** Use tempfile and cleanup in fixtures

- **Issue:** Coverage below 80%
  - **Solution:** Add tests for uncovered branches

---

## COMPLETION CHECKLIST

- [ ] All test files created
- [ ] conftest.py with fixtures created
- [ ] Database tests cover CRUD operations
- [ ] Transaction tests cover validation
- [ ] Configuration tests cover encryption
- [ ] All tests pass
- [ ] Coverage report generated
- [ ] Coverage >80% achieved
- [ ] Edge cases tested
- [ ] Error handling tested
- [ ] Tests run in <30 seconds
- [ ] No test dependencies or ordering issues

---

## REVISION HISTORY

| Version | Date       | Author | Changes                         |
|---------|------------|--------|---------------------------------|
| 1.0     | 2025-10-29 | Claude | Initial task specification      |

---

**Next Task:** T-007 - LLM Provider Abstraction (Sprint 2 begins)
