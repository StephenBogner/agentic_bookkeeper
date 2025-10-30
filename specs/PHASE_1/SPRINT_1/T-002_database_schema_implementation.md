# Task Specification: T-002

**Task Name:** Database Schema Implementation
**Task ID:** T-002
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 1: Project Setup & Database Foundation
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 4 hours
**Dependencies:** T-001

---

## OBJECTIVE

Implement the SQLite database schema with tables for transactions and configuration, including connection management, initialization, and basic CRUD operations.

**Success Criteria:**

- Database creates successfully with correct schema
- Tables have proper constraints and indexes
- Connection manager handles errors gracefully
- Database operations are transactional and safe

---

## REQUIREMENTS

### Functional Requirements

1. **Database Connection Manager**
   - Create SQLite connection with proper configuration
   - Implement connection pooling (if needed)
   - Handle connection errors gracefully
   - Support transactions (commit/rollback)
   - Close connections properly

2. **Transactions Table Schema**
   - All fields from specification implemented
   - Proper data types and constraints
   - Indexes on frequently queried columns
   - Default values where appropriate

3. **Config Table Schema**
   - Key-value store for application settings
   - Support for various data types (stored as TEXT)
   - Unique constraint on keys

4. **Database Initialization**
   - Create database file if doesn't exist
   - Create tables if they don't exist
   - Validate schema on startup
   - Support for database migrations (future-proofing)

5. **Backup Functionality**
   - Function to create database backup
   - Timestamped backup files
   - Verify backup integrity

### Non-Functional Requirements

- Database operations must be thread-safe
- Connection management must prevent leaks
- Schema must support future migrations
- Performance: queries <50ms average

---

## DESIGN CONSIDERATIONS

### Database Schema

```sql
-- Transactions table
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,                         -- ISO 8601 format (YYYY-MM-DD)
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    category TEXT NOT NULL,                     -- CRA/IRS category
    vendor_customer TEXT,                       -- Vendor (expense) or Customer (income)
    description TEXT,                           -- Additional details
    amount REAL NOT NULL CHECK(amount >= 0),    -- Transaction amount
    tax_amount REAL DEFAULT 0 CHECK(tax_amount >= 0),
    document_filename TEXT,                     -- Reference to archived document
    created_at TEXT NOT NULL,                   -- ISO 8601 datetime
    modified_at TEXT NOT NULL                   -- ISO 8601 datetime
);

-- Indexes for performance
CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_category ON transactions(category);

-- Config table
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

### Connection Manager Pattern

```python
class Database:
    """SQLite database connection manager."""

    def __init__(self, db_path: str):
        """Initialize database connection."""
        pass

    def connect(self) -> sqlite3.Connection:
        """Get database connection."""
        pass

    def initialize_schema(self) -> None:
        """Create tables if they don't exist."""
        pass

    def execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query with parameters."""
        pass

    def execute_transaction(self, queries: list) -> None:
        """Execute multiple queries in a transaction."""
        pass

    def backup(self, backup_path: str) -> None:
        """Create database backup."""
        pass

    def close(self) -> None:
        """Close database connection."""
        pass
```

---

## ACCEPTANCE CRITERIA

### Must Have

- [ ] Database class implemented in src/models/database.py
- [ ] Transactions table created with all fields
- [ ] Config table created with key-value structure
- [ ] All indexes created on transactions table
- [ ] Database initializes successfully on first run
- [ ] Connection manager handles errors gracefully
- [ ] Backup function creates valid backup files
- [ ] Type hints and docstrings complete

### Should Have

- [ ] Transaction support (commit/rollback)
- [ ] Connection context manager (with statement)
- [ ] Schema validation on startup
- [ ] Database path configuration from environment

### Nice to Have

- [ ] Migration framework foundation
- [ ] Query logging for debugging
- [ ] Connection pooling
- [ ] Read-only mode support

---

## CONTEXT REQUIRED

### Information Needed

- Database file location (from .env or default)
- Project coding standards (from CLAUDE.md)
- Maximum file size limit (500 lines from CLAUDE.md)

### Artifacts from Previous Tasks

- T-001: Project structure and configuration
- Virtual environment setup
- Dependencies installed (sqlite3 is built-in)

---

## EXPECTED DELIVERABLES

### Files to Create

- `src/agentic_bookkeeper/models/database.py` - Database connection manager
- `src/agentic_bookkeeper/models/__init__.py` - Update with database export

### Files to Modify

- None initially (new module)

---

## VALIDATION COMMANDS

```bash
# Test database creation
python -c "
from src.agentic_bookkeeper.models.database import Database
db = Database('./test_db.sqlite')
db.initialize_schema()
print('Database created successfully')
"

# Verify schema with sqlite3 command
sqlite3 ./test_db.sqlite ".schema"

# Check indexes
sqlite3 ./test_db.sqlite ".indexes transactions"

# Test backup functionality
python -c "
from src.agentic_bookkeeper.models.database import Database
db = Database('./test_db.sqlite')
db.backup('./test_db.backup')
print('Backup created successfully')
"

# Cleanup test files
rm -f ./test_db.sqlite ./test_db.backup
```

---

## IMPLEMENTATION NOTES

### File Structure

```python
"""
Module: database
Purpose: SQLite database connection and schema management
Author: Stephen Bogner
Created: 2025-10-29
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Database:
    """SQLite database connection manager for Agentic Bookkeeper."""

    # Schema definition constants
    SCHEMA_VERSION = 1

    TRANSACTIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
        category TEXT NOT NULL,
        vendor_customer TEXT,
        description TEXT,
        amount REAL NOT NULL CHECK(amount >= 0),
        tax_amount REAL DEFAULT 0 CHECK(tax_amount >= 0),
        document_filename TEXT,
        created_at TEXT NOT NULL,
        modified_at TEXT NOT NULL
    );
    """

    INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);",
        "CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);",
        "CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);"
    ]

    CONFIG_TABLE = """
    CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """
```

### Key Implementation Details

1. **Error Handling**
   - Catch sqlite3.Error exceptions
   - Log errors with context
   - Provide meaningful error messages
   - Rollback transactions on error

2. **Connection Management**
   - Use context managers for safety
   - Set pragmas for performance (WAL mode, foreign keys)
   - Configure row factory for dict-like access
   - Close connections properly

3. **Schema Initialization**
   - Check if tables exist before creating
   - Create all tables and indexes
   - Store schema version in config table
   - Validate schema integrity

4. **Transaction Support**
   - BEGIN/COMMIT/ROLLBACK support
   - Atomic multi-query operations
   - Proper isolation levels

### SQLite Configuration

```python
# Recommended pragmas
PRAGMA journal_mode=WAL;        # Write-ahead logging for better concurrency
PRAGMA synchronous=NORMAL;      # Balance safety and performance
PRAGMA foreign_keys=ON;         # Enable foreign key constraints
PRAGMA temp_store=MEMORY;       # Use memory for temp tables
```

---

## NOTES

### Important Considerations

- SQLite is serverless and file-based (perfect for desktop app)
- All dates stored as TEXT in ISO 8601 format for consistency
- Amounts stored as REAL (floating point) - acceptable for bookkeeping
- Check constraints prevent invalid data (negative amounts, invalid types)
- Indexes improve query performance on large datasets

### Potential Issues

- **Issue:** Float precision for monetary amounts
  - **Solution:** Document rounding behavior, consider Decimal in Python layer

- **Issue:** Concurrent access from multiple threads
  - **Solution:** Use connection per thread or proper locking

- **Issue:** Database file corruption
  - **Solution:** Regular backups, WAL mode for durability

- **Issue:** Large database size
  - **Solution:** Implement vacuum, archive old transactions

### Database File Location

Default: `~/.agentic_bookkeeper/bookkeeper.db`

```python
import os
from pathlib import Path

def get_default_db_path() -> Path:
    """Get default database path."""
    home = Path.home()
    app_dir = home / '.agentic_bookkeeper'
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir / 'bookkeeper.db'
```

---

## COMPLETION CHECKLIST

- [ ] Database class implemented with all methods
- [ ] Schema SQL statements defined as constants
- [ ] Connection management working (connect/close)
- [ ] initialize_schema() creates all tables and indexes
- [ ] Backup functionality implemented and tested
- [ ] Error handling comprehensive with logging
- [ ] Type hints complete for all methods
- [ ] Docstrings follow Google style
- [ ] Manual testing completed successfully
- [ ] CONTEXT.md updated with database patterns

---

## REVISION HISTORY

| Version | Date       | Author | Changes                         |
|---------|------------|--------|---------------------------------|
| 1.0     | 2025-10-29 | Claude | Initial task specification      |

---

**Next Task:** T-003 - Transaction Model Implementation
