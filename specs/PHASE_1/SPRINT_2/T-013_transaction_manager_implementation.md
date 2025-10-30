# Task Specification: T-013

**Task Name:** Transaction Manager Implementation
**Task ID:** T-013
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 2: LLM Integration & Document Processing
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 4 hours
**Dependencies:** T-003, T-002

---

## OBJECTIVE

Implement the transaction manager that provides CRUD operations, search, filtering, duplicate detection, and statistics for transactions.

---

## REQUIREMENTS

### Functional Requirements

- Create new transactions with validation
- Retrieve transactions by ID
- Update existing transactions
- Delete transactions
- Query transactions with filters (date range, type, category)
- Search transactions by text (vendor, description)
- Detect duplicate transactions
- Calculate transaction statistics (totals, counts, averages)
- Support batch operations
- Maintain transaction audit trail

### Non-Functional Requirements

- Database queries must complete in <50ms average
- Support efficient filtering on 10,000+ transactions
- Transaction operations must be atomic
- Proper error handling for all operations

---

## ACCEPTANCE CRITERIA

- [ ] All CRUD operations work correctly
- [ ] Filtering by date, type, and category works
- [ ] Text search finds relevant transactions
- [ ] Duplicate detection identifies similar transactions
- [ ] Statistics calculations are accurate
- [ ] Batch operations are atomic
- [ ] Error handling is comprehensive
- [ ] Type hints and docstrings complete
- [ ] Unit tests achieve >80% coverage

---

## EXPECTED DELIVERABLES

**Files to Create:**

- `src/agentic_bookkeeper/core/transaction_manager.py`

**Files to Modify:**

- `src/agentic_bookkeeper/core/__init__.py` (export manager)

---

## VALIDATION COMMANDS

```bash
# Test transaction manager
pytest src/agentic_bookkeeper/tests/test_transaction_manager.py -v

# Manual test
python -c "
from src.agentic_bookkeeper.core.transaction_manager import TransactionManager
from src.agentic_bookkeeper.models.database import Database

db = Database('./test.db')
db.initialize_schema()
manager = TransactionManager(db)

# Create transaction
tx = manager.create_transaction(
    date='2025-01-15',
    type='expense',
    category='Office Supplies',
    amount=45.99
)
print(f'Created: {tx}')

# Query transactions
results = manager.query_transactions(type='expense')
print(f'Found {len(results)} expenses')
"
```

---

## IMPLEMENTATION NOTES

### Transaction Manager Class Structure

```python
class TransactionManager:
    """Manage transaction CRUD operations and queries."""

    def __init__(self, database: Database):
        """Initialize manager with database connection."""
        self.db = database

    def create_transaction(self, **kwargs) -> Transaction:
        """Create new transaction."""
        pass

    def get_transaction(self, transaction_id: int) -> Transaction:
        """Get transaction by ID."""
        pass

    def update_transaction(self, transaction_id: int, **kwargs) -> Transaction:
        """Update existing transaction."""
        pass

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete transaction."""
        pass

    def query_transactions(self,
                          start_date: str = None,
                          end_date: str = None,
                          type: str = None,
                          category: str = None,
                          search: str = None) -> List[Transaction]:
        """Query transactions with filters."""
        pass

    def find_duplicates(self, transaction: Transaction) -> List[Transaction]:
        """Find potential duplicate transactions."""
        pass

    def get_statistics(self,
                      start_date: str = None,
                      end_date: str = None) -> dict:
        """Calculate transaction statistics."""
        pass
```

### Duplicate Detection Logic

```python
def find_duplicates(self, transaction: Transaction) -> List[Transaction]:
    """
    Find potential duplicates based on:
    - Same date (within 1 day)
    - Same amount (exact match)
    - Same vendor/customer (fuzzy match)
    - Same type
    """
    pass
```

### Statistics Structure

```python
{
    "total_income": 10000.00,
    "total_expenses": 7500.00,
    "net_income": 2500.00,
    "transaction_count": 150,
    "income_count": 45,
    "expense_count": 105,
    "average_expense": 71.43,
    "categories": {
        "Office Supplies": 1250.00,
        "Travel": 2100.00,
        ...
    }
}
```

---

## NOTES

- Use parameterized SQL queries to prevent injection
- Build WHERE clauses dynamically for flexible filtering
- Consider pagination for large result sets (future)
- Duplicate detection may need tuning based on user feedback
- Statistics should be cached if calculated frequently
- Transaction timestamps enable audit trail
- Consider soft deletes instead of hard deletes (future)

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-014 - Document Monitor Implementation
