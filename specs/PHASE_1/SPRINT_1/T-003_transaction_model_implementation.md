# Task Specification: T-003

**Task Name:** Transaction Model Implementation
**Task ID:** T-003
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 1: Project Setup & Database Foundation
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 3 hours
**Dependencies:** T-002

---

## OBJECTIVE

Implement the Transaction model class with comprehensive data validation, serialization methods, and business logic to represent individual financial transactions in the Agentic Bookkeeper application.

**Success Criteria:**

- Transaction model validates all fields correctly
- Invalid data raises appropriate exceptions
- Serialization/deserialization works correctly
- Type hints are complete and accurate
- CRA/IRS categories are validated

---

## REQUIREMENTS

### Functional Requirements

1. **Transaction Class Definition**
   - Define Transaction dataclass or class with all required fields
   - Implement proper field types matching database schema
   - Add field-level validation (date format, amount >=0, type enum)

2. **Data Validation**
   - Validate date format (ISO 8601: YYYY-MM-DD)
   - Validate amount >= 0 (no negative amounts)
   - Validate tax_amount >= 0
   - Validate type is 'income' or 'expense'
   - Validate category against CRA/IRS category lists
   - Validate required fields are present

3. **Serialization Methods**
   - Implement to_dict() for database storage
   - Implement from_dict() for object creation
   - Implement to_json() for API/export compatibility
   - Implement from_json() for import compatibility

4. **String Representation**
   - Implement **str**() for human-readable output
   - Implement **repr**() for debugging
   - Include key fields in representations

5. **Comparison Methods**
   - Implement **eq**() for equality comparison
   - Implement **lt**(), **le**(), **gt**(), **ge**() for sorting by date
   - Support sorting by different fields

6. **Business Logic Methods**
   - Calculate total with tax: get_total_amount()
   - Check if transaction is income: is_income()
   - Check if transaction is expense: is_expense()
   - Update modified timestamp: update_modified_timestamp()

### Non-Functional Requirements

- Immutability for key fields (id, created_at)
- Clear error messages for validation failures
- Performance: validation <1ms per transaction
- Type safety with comprehensive type hints

---

## DESIGN CONSIDERATIONS

### Class Structure

```python
"""
Module: transaction
Purpose: Transaction model with validation and serialization
Author: Stephen Bogner
Created: 2025-10-29
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
import json

@dataclass
class Transaction:
    """
    Represents a financial transaction (income or expense).

    Attributes:
        id: Unique transaction identifier (None for new transactions)
        date: Transaction date (ISO 8601 format)
        type: Transaction type ('income' or 'expense')
        category: CRA/IRS category code
        vendor_customer: Vendor name (expense) or customer name (income)
        description: Additional transaction details
        amount: Transaction amount (non-negative)
        tax_amount: Tax amount (non-negative, default 0)
        document_filename: Reference to archived document
        created_at: Timestamp when transaction was created
        modified_at: Timestamp when transaction was last modified
    """

    date: str
    type: str
    category: str
    amount: float
    vendor_customer: Optional[str] = None
    description: Optional[str] = None
    tax_amount: float = 0.0
    document_filename: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None

    def __post_init__(self):
        """Validate transaction data after initialization."""
        self.validate()

        # Set timestamps if not provided
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.modified_at is None:
            self.modified_at = datetime.utcnow().isoformat()

    def validate(self) -> None:
        """Validate all transaction fields."""
        pass  # Implementation needed

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary for database storage."""
        pass  # Implementation needed

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create transaction from dictionary."""
        pass  # Implementation needed

    def get_total_amount(self) -> float:
        """Calculate total amount including tax."""
        return self.amount + self.tax_amount

    def is_income(self) -> bool:
        """Check if transaction is income."""
        return self.type == 'income'

    def is_expense(self) -> bool:
        """Check if transaction is expense."""
        return self.type == 'expense'

    def update_modified_timestamp(self) -> None:
        """Update the modified_at timestamp to current time."""
        self.modified_at = datetime.utcnow().isoformat()
```

### Validation Logic

```python
import re
from datetime import datetime

VALID_TYPES = {'income', 'expense'}
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')

def validate_date(date_str: str) -> None:
    """Validate date is in ISO 8601 format."""
    if not DATE_PATTERN.match(date_str):
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")

    # Try parsing to ensure it's a valid date
    try:
        datetime.fromisoformat(date_str)
    except ValueError as e:
        raise ValueError(f"Invalid date: {date_str}. {str(e)}")

def validate_type(transaction_type: str) -> None:
    """Validate transaction type."""
    if transaction_type not in VALID_TYPES:
        raise ValueError(f"Invalid type: {transaction_type}. Must be 'income' or 'expense'")

def validate_amount(amount: float, field_name: str = "amount") -> None:
    """Validate amount is non-negative."""
    if amount < 0:
        raise ValueError(f"{field_name} must be non-negative, got {amount}")
```

---

## ACCEPTANCE CRITERIA

### Must Have

- [ ] Transaction class implemented with all required fields
- [ ] Data validation working for all fields
- [ ] Invalid dates raise ValueError
- [ ] Invalid types raise ValueError
- [ ] Negative amounts raise ValueError
- [ ] to_dict() serialization working
- [ ] from_dict() deserialization working
- [ ] **str**() and **repr**() implemented
- [ ] Comparison methods for sorting implemented
- [ ] Type hints complete and accurate
- [ ] Docstrings following Google style

### Should Have

- [ ] Category validation against CRA/IRS lists
- [ ] JSON serialization (to_json/from_json)
- [ ] Timezone-aware datetime handling
- [ ] Deep validation of all edge cases

### Nice to Have

- [ ] Currency formatting methods
- [ ] Transaction cloning method
- [ ] Audit trail for changes
- [ ] Support for attachments beyond filename

---

## CONTEXT REQUIRED

### Information Needed

- Database schema from T-002
- CRA/IRS category lists (will be in config/)
- Date format standards (ISO 8601)
- Python dataclass patterns

### Artifacts from Previous Tasks

- T-001: Project structure
- T-002: Database schema definition

---

## EXPECTED DELIVERABLES

### Files to Create

- `src/agentic_bookkeeper/models/transaction.py` - Transaction model class

### Files to Modify

- `src/agentic_bookkeeper/models/__init__.py` - Export Transaction class

---

## VALIDATION COMMANDS

```bash
# Test transaction creation
python -c "
from src.agentic_bookkeeper.models.transaction import Transaction
t = Transaction(
    date='2025-10-29',
    type='expense',
    category='Office Supplies',
    amount=100.50,
    vendor_customer='Office Depot',
    description='Printer paper'
)
print('Transaction created:', t)
print('Total with tax:', t.get_total_amount())
"

# Test validation
python -c "
from src.agentic_bookkeeper.models.transaction import Transaction
try:
    t = Transaction(
        date='invalid-date',
        type='expense',
        category='Office Supplies',
        amount=100.50
    )
except ValueError as e:
    print('Validation working:', e)
"

# Test serialization
python -c "
from src.agentic_bookkeeper.models.transaction import Transaction
t = Transaction(
    date='2025-10-29',
    type='income',
    category='Sales',
    amount=500.00
)
data = t.to_dict()
print('Serialized:', data)
t2 = Transaction.from_dict(data)
print('Deserialized:', t2)
print('Equal:', t == t2)
"
```

---

## IMPLEMENTATION NOTES

### Step-by-Step Execution

1. **Create Transaction Class**
   - Use @dataclass decorator for simplicity
   - Define all fields with proper types
   - Add **post_init** for validation

2. **Implement Validation**
   - Create validation helper functions
   - Call validation in **post_init**
   - Raise ValueError with clear messages

3. **Implement Serialization**
   - to_dict(): Use dataclasses.asdict() with modifications
   - from_dict(): Use constructor with **kwargs
   - Handle None values properly

4. **Implement String Methods**
   - **str**(): User-friendly format
   - **repr**(): Developer format with all fields

5. **Implement Comparison Methods**
   - Use functools.total_ordering decorator
   - Define **eq** and **lt**
   - Sort by date primarily

6. **Add Business Logic**
   - Simple methods for common operations
   - Keep logic in model where appropriate

### Code Examples

```python
# Validation in __post_init__
def __post_init__(self):
    """Validate transaction data after initialization."""
    validate_date(self.date)
    validate_type(self.type)
    validate_amount(self.amount, "amount")
    validate_amount(self.tax_amount, "tax_amount")

    if not self.category:
        raise ValueError("category is required")

    # Set timestamps
    if self.created_at is None:
        self.created_at = datetime.utcnow().isoformat()
    if self.modified_at is None:
        self.modified_at = datetime.utcnow().isoformat()

# Serialization
def to_dict(self) -> Dict[str, Any]:
    """Convert transaction to dictionary."""
    return {
        'id': self.id,
        'date': self.date,
        'type': self.type,
        'category': self.category,
        'vendor_customer': self.vendor_customer,
        'description': self.description,
        'amount': self.amount,
        'tax_amount': self.tax_amount,
        'document_filename': self.document_filename,
        'created_at': self.created_at,
        'modified_at': self.modified_at
    }

@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
    """Create transaction from dictionary."""
    return cls(**data)

# String representation
def __str__(self) -> str:
    """Human-readable string representation."""
    return (f"{self.date} - {self.type.capitalize()}: "
            f"${self.amount:.2f} - {self.category} "
            f"({self.vendor_customer or 'N/A'})")

def __repr__(self) -> str:
    """Developer string representation."""
    return (f"Transaction(id={self.id}, date='{self.date}', "
            f"type='{self.type}', amount={self.amount})")
```

---

## NOTES

### Important Considerations

- Using float for amounts is acceptable for typical bookkeeping
- For critical financial applications, consider Decimal type
- Timestamps stored in UTC as ISO 8601 strings
- Validation happens at object creation (fail-fast principle)
- Dataclass provides automatic **init**, **eq**, **hash**

### Potential Issues

- **Issue:** Float precision errors in amount calculations
  - **Solution:** Document rounding behavior, consider Decimal if needed

- **Issue:** Timezone handling in timestamps
  - **Solution:** Store all times in UTC, convert for display

- **Issue:** Category validation requires loading category lists
  - **Solution:** Defer category validation to service layer or load lazily

- **Issue:** Dataclass frozen=True vs mutability
  - **Solution:** Allow mutability for modified_at updates, document carefully

---

## COMPLETION CHECKLIST

- [ ] Transaction class created with all fields
- [ ] Validation implemented and tested
- [ ] Serialization methods working (to_dict/from_dict)
- [ ] String methods implemented (**str**/**repr**)
- [ ] Comparison methods implemented for sorting
- [ ] Business logic methods implemented
- [ ] Type hints complete
- [ ] Docstrings complete
- [ ] Manual testing passed all validation commands
- [ ] Edge cases tested (None values, boundaries, invalid inputs)

---

## REVISION HISTORY

| Version | Date       | Author | Changes                         |
|---------|------------|--------|---------------------------------|
| 1.0     | 2025-10-29 | Claude | Initial task specification      |

---

**Next Task:** T-004 - Configuration Management
