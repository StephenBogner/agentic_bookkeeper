# Task Specification: T-020

**Task Name:** Phase 1 Documentation
**Task ID:** T-020
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 3: Integration & Validation
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** High
**Estimated Effort:** 3 hours
**Dependencies:** T-017, T-018, T-019

---

## OBJECTIVE

Create comprehensive documentation for Phase 1 including architecture diagrams, API documentation, database schema documentation, and developer setup guide.

---

## REQUIREMENTS

### Functional Requirements

- Document all public APIs with complete docstrings
- Create architecture diagram showing component relationships
- Document database schema with field descriptions
- Document LLM provider interface and implementation
- Create developer setup guide for new contributors
- Document testing procedures
- Include code examples
- Document configuration options

### Non-Functional Requirements

- Documentation must be clear and accurate
- Examples must be functional and tested
- Diagrams must reflect actual implementation
- Setup guide must work on fresh environment

---

## ACCEPTANCE CRITERIA

- [ ] All public methods have complete docstrings
- [ ] Architecture diagram created and accurate
- [ ] Database schema documented with examples
- [ ] LLM provider interface documented
- [ ] Developer setup guide is complete
- [ ] Testing procedures documented
- [ ] Configuration options documented
- [ ] Code examples are functional
- [ ] Documentation reviewed for accuracy

---

## EXPECTED DELIVERABLES

**Files to Create:**

- `docs/ARCHITECTURE.md`
- `docs/DATABASE_SCHEMA.md`
- `docs/DEVELOPER_SETUP.md`
- `docs/LLM_PROVIDERS.md`

**Files to Modify:**

- All source files (improve docstrings)

---

## VALIDATION COMMANDS

```bash
# Validate docstrings with pydocstyle
pydocstyle src/agentic_bookkeeper/

# Generate API documentation
pdoc --html --output-dir docs/api src/agentic_bookkeeper

# Test developer setup guide
# Follow guide in fresh virtual environment

# Check for broken links in documentation
markdown-link-check docs/*.md
```text

---

## IMPLEMENTATION NOTES

### ARCHITECTURE.md Template

```markdown
# Agentic Bookkeeper Architecture

## Overview
High-level description of system architecture.

## Component Diagram
```text

┌─────────────────┐
│   GUI (Phase 2)  │
└────────┬─────────┘
         │
┌────────▼─────────────────────────────────┐
│         Core Components                   │
│  ┌──────────────┐  ┌──────────────────┐  │
│  │  Document    │  │   Transaction    │  │
│  │  Processor   │  │   Manager        │  │
│  └──────┬───────┘  └─────────┬────────┘  │
└─────────┼─────────────────────┼───────────┘
          │                     │
┌─────────▼──────┐    ┌────────▼────────┐
│  LLM Providers  │    │    Database     │
│  - OpenAI      │    │    (SQLite)     │
│  - Anthropic   │    │                 │
│  - Google      │    │                 │
└────────────────┘    └─────────────────┘

```text

## Component Descriptions

### Document Processor
Handles document intake, preprocessing, and extraction.
- Input: PDF, JPG, PNG documents
- Output: Structured transaction data
- Dependencies: LLM Providers

### Transaction Manager
Manages transaction CRUD operations and queries.
- Input: Transaction data
- Output: Stored transactions, query results
- Dependencies: Database

### LLM Providers
Abstract interface for multiple AI providers.
- OpenAI (GPT-4 Vision)
- Anthropic (Claude)
- Google (Gemini)
- XAI (Grok)

### Database
SQLite database for transaction storage.
- Tables: transactions, config
- Indexes: date, type, category

## Data Flow

1. Document arrives in watch directory
2. Document Monitor detects file
3. Document Processor extracts data via LLM
4. User reviews extracted data (Phase 2)
5. Transaction Manager stores to database
6. Document archived

## Technology Stack
- Python 3.10+
- SQLite (database)
- PySide6 (GUI - Phase 2)
- OpenAI/Anthropic/Google APIs
- pypdf (PDF processing)
- Pillow (image processing)
- watchdog (file monitoring)
```text

### DATABASE_SCHEMA.md Template

```markdown
# Database Schema

## Overview
SQLite database with two tables: transactions and config.

## Transactions Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing ID |
| date | TEXT | NOT NULL | Transaction date (YYYY-MM-DD) |
| type | TEXT | NOT NULL, CHECK | "income" or "expense" |
| category | TEXT | NOT NULL | Business category (CRA/IRS) |
| vendor_customer | TEXT | NULL | Vendor (expense) or Customer (income) |
| description | TEXT | NULL | Additional details |
| amount | REAL | NOT NULL, CHECK | Amount >= 0 |
| tax_amount | REAL | DEFAULT 0, CHECK | Tax >= 0 |
| document_filename | TEXT | NULL | Archived document reference |
| created_at | TEXT | NOT NULL | Creation timestamp (ISO 8601) |
| modified_at | TEXT | NOT NULL | Last modification timestamp |

### Indexes
- idx_transactions_date (date)
- idx_transactions_type (type)
- idx_transactions_category (category)

## Config Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| key | TEXT | PRIMARY KEY | Configuration key |
| value | TEXT | NOT NULL | Configuration value (JSON) |

## SQL Schema

```sql
CREATE TABLE transactions (
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

CREATE INDEX idx_transactions_date ON transactions(date);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_category ON transactions(category);

CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```text

## Example Queries

```sql
-- Get all expenses in date range
SELECT * FROM transactions
WHERE type = 'expense'
  AND date BETWEEN '2025-01-01' AND '2025-01-31'
ORDER BY date DESC;

-- Calculate total income
SELECT SUM(amount) as total_income
FROM transactions
WHERE type = 'income';

-- Group expenses by category
SELECT category, SUM(amount) as total
FROM transactions
WHERE type = 'expense'
GROUP BY category
ORDER BY total DESC;
```text

```text

### DEVELOPER_SETUP.md Template

```markdown
# Developer Setup Guide

## Prerequisites
- Python 3.10 or higher
- Git
- Virtual environment tool (venv)
- API keys (OpenAI, Anthropic, Google)

## Setup Steps

### 1. Clone Repository
```bash
git clone <repository-url>
cd agentic_bookkeeper_module
```text

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```text

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```text

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```text

### 5. Initialize Database

```bash
python -c "from src.agentic_bookkeeper.models.database import Database; db = Database(); db.initialize_schema()"
```text

### 6. Run Tests

```bash
pytest
```text

### 7. Run Application

```bash
python main.py
```text

## Development Workflow

### Running Tests

```bash
# All tests
pytest

# Specific module
pytest src/agentic_bookkeeper/tests/test_database.py

# With coverage
pytest --cov=src/agentic_bookkeeper
```text

### Code Quality

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```text

### Adding New LLM Provider

1. Create provider class in `src/llm/`
2. Implement LLMProvider interface
3. Add provider to factory
4. Add tests
5. Update documentation

```text

---

## NOTES

- Use Markdown for all documentation
- Include code examples that actually work
- Keep documentation up-to-date with implementation
- Use diagrams for complex concepts
- Document both happy path and error cases
- Include troubleshooting section
- Link related documentation
- Consider using pdoc or Sphinx for API docs generation

### Docstring Style (Google Format)

```python
def process_document(file_path: str, provider: str = 'anthropic') -> dict:
    """Process a financial document and extract transaction data.

    Args:
        file_path: Path to the document file (PDF, JPG, PNG).
        provider: LLM provider to use ('openai', 'anthropic', 'google', 'xai').

    Returns:
        Dictionary containing extracted transaction data with keys:
        - success (bool): Whether extraction succeeded
        - data (dict): Extracted transaction fields
        - errors (list): Any errors encountered

    Raises:
        FileNotFoundError: If file_path does not exist.
        InvalidDocumentError: If document format is unsupported.
        ProcessingError: If extraction fails.

    Example:
        >>> result = process_document('receipt.pdf', 'anthropic')
        >>> print(result['data']['amount'])
        45.99
    """
    pass
```text

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-021 - PySide6 Main Window Setup (Phase 2)
