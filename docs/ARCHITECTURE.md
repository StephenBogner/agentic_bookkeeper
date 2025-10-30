# Architecture Documentation

**Project:** Agentic Bookkeeper
**Version:** 0.1.0
**Last Updated:** 2025-10-29
**Status:** Phase 4 - Testing & Documentation

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Database Design](#database-design)
6. [Technology Stack](#technology-stack)
7. [Design Patterns](#design-patterns)
8. [Extension Points](#extension-points)
9. [Security Architecture](#security-architecture)
10. [Performance Considerations](#performance-considerations)

---

## System Overview

### Purpose

Agentic Bookkeeper is an intelligent bookkeeping automation system that leverages LLM (Large Language Model) technology to automatically process receipts, invoices, and financial documents. The system extracts transaction data using AI vision capabilities and provides comprehensive reporting and export features suitable for tax filing.

### Key Features

- **Automated Document Processing**: PDF and image processing using LLM vision APIs
- **Multi-LLM Provider Support**: OpenAI, Anthropic, XAI, Google
- **Tax Jurisdiction Support**: CRA (Canada) and IRS (United States)
- **Professional GUI**: PySide6-based desktop application
- **Comprehensive Reporting**: Income statements and expense reports
- **Multi-Format Export**: PDF, CSV, JSON export capabilities
- **Secure Storage**: Encrypted API key storage with SQLite database

### Target Users

- Small business owners
- Freelancers and independent contractors
- Self-employed individuals
- Anyone needing automated bookkeeping for tax filing

---

## Architecture Principles

### Design Philosophy

1. **Object-Oriented Design**: One class per file, maximum 500 lines per file
2. **Modularity**: Clear separation of concerns across components
3. **Testability**: High test coverage (>80%) with isolated unit tests
4. **Extensibility**: Easy to add new LLM providers, export formats, and reports
5. **Cross-Platform**: Works on Windows and Linux
6. **Type Safety**: Full type hints on all function signatures
7. **Observability**: Comprehensive logging with log sanitization

### Code Quality Standards

- **Style Guide**: PEP 8 compliance
- **Formatter**: black (100 character line length)
- **Linter**: flake8
- **Type Checker**: mypy
- **Test Framework**: pytest with >80% coverage
- **Documentation**: Google-style docstrings

---

## Component Architecture

### High-Level Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            PySide6 GUI Application                     │ │
│  │  (Main Window, Dashboard, Transactions, Reports)       │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                   Business Logic Layer                       │
│  ┌──────────────┐  ┌────────────────┐  ┌─────────────────┐ │
│  │  Document    │  │  Transaction   │  │     Report      │ │
│  │  Processor   │  │   Manager      │  │   Generator     │ │
│  └──────────────┘  └────────────────┘  └─────────────────┘ │
│  ┌──────────────┐                      ┌─────────────────┐ │
│  │  Document    │                      │    Exporters    │ │
│  │  Monitor     │                      │ (PDF,CSV,JSON)  │ │
│  └──────────────┘                      └─────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                   Integration Layer                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          LLM Provider Abstraction                     │  │
│  │  (OpenAI, Anthropic, XAI, Google)                    │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                    Data Layer                                │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │    SQLite      │  │  Transaction   │  │    Config    │  │
│  │   Database     │  │     Model      │  │  Management  │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```text

### Component Breakdown

#### 1. User Interface Layer (`src/agentic_bookkeeper/gui/`)

**Purpose**: Provides PySide6-based desktop GUI for user interaction.

**Components**:

- `main_window.py`: Main application window with tabbed interface
- `dashboard_widget.py`: Overview dashboard with statistics and monitoring controls
- `transactions_widget.py`: Transaction list with filtering and search
- `transaction_edit_dialog.py`: Edit existing transactions
- `transaction_add_dialog.py`: Add new transactions manually
- `document_review_dialog.py`: Review and accept/reject processed documents
- `settings_dialog.py`: Application settings (API keys, directories, jurisdiction)
- `reports_widget.py`: Report generation and export interface

**Design Pattern**: Model-View-Controller (MVC) with Qt signals/slots

**Key Features**:

- Tabbed interface for different functions
- Real-time statistics and monitoring
- Document folder monitoring controls
- CRUD operations for transactions
- Report generation with preview
- Multi-format export

#### 2. Business Logic Layer (`src/agentic_bookkeeper/core/`)

**Purpose**: Core business logic for document processing, transaction management, and reporting.

**Components**:

**Document Processing**:

- `document_processor.py`: Processes PDF and image documents using LLM vision APIs
  - Extracts: date, vendor, amount, category, description
  - Validates extracted data
  - Creates transactions from documents

**Transaction Management**:

- `transaction_manager.py`: CRUD operations for transactions
  - Create, read, update, delete transactions
  - Filter by type, category, date range
  - Search by vendor, description
  - Calculate aggregates and statistics

**Monitoring**:

- `document_monitor.py`: Watches directory for new documents
  - File system monitoring with watchdog library
  - Automatic processing of new documents
  - Duplicate detection
  - Error handling and retry logic

**Reporting**:

- `report_generator.py`: Generates financial reports
  - Income statements (revenue, expenses, net income)
  - Expense reports (category breakdown with tax codes)
  - Date range filtering
  - Category aggregation with percentages
  - Tax jurisdiction support (CRA/IRS)

**Export** (`core/exporters/`):

- `pdf_exporter.py`: Professional PDF export using ReportLab
- `csv_exporter.py`: Excel-compatible CSV export using pandas
- `json_exporter.py`: Structured JSON export with schema versioning

#### 3. Integration Layer (`src/agentic_bookkeeper/llm/`)

**Purpose**: Abstract LLM provider integration for flexibility and vendor independence.

**Components**:

- `llm_provider.py`: Abstract base class defining provider interface
- `openai_provider.py`: OpenAI GPT-4 Vision implementation
- `anthropic_provider.py`: Anthropic Claude Vision implementation
- `xai_provider.py`: XAI Grok Vision implementation
- `google_provider.py`: Google Gemini Vision implementation

**Design Pattern**: Strategy Pattern (pluggable providers)

**Key Features**:

- Unified interface for all providers
- Automatic JSON parsing from LLM responses
- Error handling and retry logic
- Provider-specific configuration
- Cost optimization (provider selection)

#### 4. Data Layer (`src/agentic_bookkeeper/models/`)

**Purpose**: Data persistence and models.

**Components**:

- `database.py`: SQLite database connection manager
  - WAL mode for concurrent access
  - Connection pooling (single connection, thread-safe)
  - Backup functionality
  - Schema initialization
- `transaction.py`: Transaction data model
  - Type-safe transaction representation
  - Validation logic
  - To/from database conversion

#### 5. Utilities (`src/agentic_bookkeeper/utils/`)

**Purpose**: Cross-cutting concerns and utilities.

**Components**:

- `config.py`: Configuration management
  - API key encryption/decryption
  - Settings persistence
  - Environment variable loading
- `logger.py`: Logging setup
  - Sensitive data filtering
  - File and console handlers
  - Structured logging

---

## Data Flow

### Document Processing Flow

```text
1. User drops document in watch folder
   │
   ├─> Document Monitor detects new file
   │
   ├─> Document Processor reads file (PDF/image)
   │
   ├─> Document sent to LLM Provider (with vision)
   │
   ├─> LLM extracts transaction data (JSON)
   │
   ├─> Transaction Manager validates data
   │
   ├─> Transaction stored in SQLite database
   │
   ├─> GUI shows Document Review Dialog
   │
   └─> User accepts/rejects or edits transaction
```text

### Report Generation Flow

```text
1. User selects report type and date range
   │
   ├─> Report Generator queries Transaction Manager
   │
   ├─> Transactions filtered by date range
   │
   ├─> Data aggregated by category
   │
   ├─> Totals and percentages calculated
   │
   ├─> Tax codes added (based on jurisdiction)
   │
   ├─> Report formatted as dictionary
   │
   ├─> GUI displays preview
   │
   └─> User selects export format
       │
       ├─> PDF Exporter: generates PDF file
       ├─> CSV Exporter: generates CSV file
       └─> JSON Exporter: generates JSON file
```text

### Configuration Flow

```text
1. First run: No config file exists
   │
   ├─> Config Manager creates default config
   │
   ├─> GUI prompts for API keys
   │
   ├─> Keys encrypted with PBKDF2-HMAC-SHA256
   │
   ├─> Encrypted keys stored in config file
   │
   └─> User sets other preferences (jurisdiction, currency)

2. Subsequent runs: Config file exists
   │
   ├─> Config Manager loads config
   │
   ├─> API keys decrypted as needed
   │
   └─> Application initialized with settings
```text

---

## Database Design

### Technology

- **Database**: SQLite 3
- **Mode**: WAL (Write-Ahead Logging) for better concurrency
- **Location**: `~/.agentic_bookkeeper/bookkeeper.db` (user home directory)
- **Timeout**: 30 seconds to prevent deadlocks

### Schema

#### Transactions Table

```sql
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    vendor TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    description TEXT,
    document_path TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```text

**Indexes**:

```sql
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_transactions_vendor ON transactions(vendor);
```text

**Field Descriptions**:

- `id`: Auto-incrementing primary key
- `date`: Transaction date (ISO format: YYYY-MM-DD)
- `vendor`: Vendor/payer name
- `amount`: Transaction amount (stored as float, used as Decimal in code)
- `category`: Transaction category (Advertising, Office Supplies, etc.)
- `type`: Transaction type (income or expense)
- `description`: Optional description/notes
- `document_path`: Path to source document (if from document processing)
- `created_at`: Record creation timestamp (ISO format)
- `updated_at`: Record update timestamp (ISO format)

### Data Access Patterns

**Common Queries**:

1. Get all transactions: `SELECT * FROM transactions ORDER BY date DESC`
2. Filter by type: `SELECT * FROM transactions WHERE type = ? ORDER BY date DESC`
3. Filter by date range: `SELECT * FROM transactions WHERE date BETWEEN ? AND ? ORDER BY date`
4. Filter by category: `SELECT * FROM transactions WHERE category = ? ORDER BY date DESC`
5. Search: `SELECT * FROM transactions WHERE vendor LIKE ? OR description LIKE ? ORDER BY date DESC`
6. Aggregate by category: `SELECT category, SUM(amount) FROM transactions WHERE type = ? GROUP BY category`

**Performance**:

- Single transaction query: ~2-5ms
- Filtered queries: ~10-20ms
- Aggregations (1000 transactions): ~50-100ms
- All transactions (1000 records): ~200-250ms

---

## Technology Stack

### Core Technologies

**Language**: Python 3.8+

**GUI Framework**:

- PySide6 6.5.0+ (Qt6 Python bindings)
- Cross-platform desktop UI

**Database**:

- SQLite 3 (embedded, file-based)
- WAL mode for concurrency

**LLM Integration**:

- OpenAI Python SDK (GPT-4 Vision)
- Anthropic Python SDK (Claude Vision)
- XAI API (Grok Vision)
- Google Generative AI SDK (Gemini Vision)

**Document Processing**:

- pypdf 4.0.0+ (PDF reading, replacing deprecated PyPDF2)
- Pillow (PIL) 10.0.0+ (image processing)
- Base64 encoding for LLM vision APIs

**Reporting & Export**:

- ReportLab 4.0.0+ (PDF generation)
- pandas 2.0.0+ (CSV export and data manipulation)
- json (standard library, JSON export)

**File System Monitoring**:

- watchdog 3.0.0+ (cross-platform file system events)

**Security**:

- cryptography 41.0.0+ (Fernet symmetric encryption, PBKDF2)

**Configuration**:

- python-dotenv 1.0.0+ (environment variable loading)
- JSON configuration files

**Testing**:

- pytest 7.4.0+ (test framework)
- pytest-cov 4.1.0+ (coverage reporting)
- pytest-qt 4.2.0+ (Qt testing)
- pytest-mock 3.11.0+ (mocking)

**Code Quality**:

- black 23.7.0+ (code formatting)
- flake8 6.1.0+ (linting)
- mypy 1.5.0+ (type checking)

### Dependencies

See `requirements.txt` and `requirements-dev.txt` for complete dependency list with pinned versions.

---

## Design Patterns

### 1. Strategy Pattern (LLM Providers)

**Purpose**: Allow runtime selection of LLM provider without changing client code.

**Implementation**:

```python
# Abstract base class
class LLMProvider(ABC):
    @abstractmethod
    def extract_transaction(self, image_data: bytes, image_format: str) -> dict:
        pass

# Concrete implementations
class OpenAIProvider(LLMProvider):
    def extract_transaction(self, image_data: bytes, image_format: str) -> dict:
        # OpenAI-specific implementation
        pass

# Usage
provider = OpenAIProvider(api_key)  # or AnthropicProvider, XAIProvider, GoogleProvider
result = provider.extract_transaction(image_data, "png")
```text

**Benefits**:

- Easy to add new providers
- Client code doesn't depend on specific provider
- Providers are independently testable

### 2. Repository Pattern (Data Access)

**Purpose**: Abstract database access to decouple business logic from data storage.

**Implementation**:

```python
class TransactionManager:
    def __init__(self, db_path: str):
        self.db = Database(db_path)

    def get_all_transactions(self) -> List[Transaction]:
        # Database access hidden behind manager
        pass

    def add_transaction(self, transaction: Transaction) -> int:
        # Validation and business logic
        pass
```text

**Benefits**:

- Business logic isolated from database details
- Easy to test with mock database
- Single point for data access logic

### 3. Model-View-Controller (GUI)

**Purpose**: Separate UI presentation from business logic.

**Implementation**:

```python
# Model
class TransactionManager:
    # Business logic and data access
    pass

# View
class TransactionsWidget(QWidget):
    # UI presentation
    pass

# Controller (implicit in Qt signals/slots)
class MainWindow(QMainWindow):
    def __init__(self):
        self.transaction_manager = TransactionManager()  # Model
        self.transactions_widget = TransactionsWidget(self.transaction_manager)  # View
        # Signals/slots connect view to model
```text

**Benefits**:

- UI can change without affecting business logic
- Business logic testable without GUI
- Multiple views can use same model

### 4. Singleton Pattern (Database Connection)

**Purpose**: Ensure single database connection throughout application lifecycle.

**Implementation**:

```python
class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self.conn
```text

**Benefits**:

- Prevents connection pool exhaustion
- Consistent state across application
- Proper resource management

### 5. Observer Pattern (File System Monitoring)

**Purpose**: React to file system events asynchronously.

**Implementation**:

```python
class DocumentMonitor:
    def __init__(self, watch_folder: str, processor: DocumentProcessor):
        self.observer = Observer()
        self.handler = DocumentHandler(processor)
        self.observer.schedule(self.handler, watch_folder, recursive=False)

    def start(self):
        self.observer.start()

class DocumentHandler(FileSystemEventHandler):
    def on_created(self, event):
        # React to new file
        self.processor.process_document(event.src_path)
```text

**Benefits**:

- Decoupled file detection from processing
- Asynchronous processing
- Easy to add new event handlers

---

## Extension Points

### 1. Adding New LLM Providers

**Steps**:

1. Create new file: `src/agentic_bookkeeper/llm/newprovider_provider.py`
2. Inherit from `LLMProvider` abstract base class
3. Implement `extract_transaction(image_data, image_format)` method
4. Return standardized JSON format: `{date, vendor, amount, category, type, description}`
5. Add to provider selection in settings dialog

**Example**:

```python
from agentic_bookkeeper.llm.llm_provider import LLMProvider

class NewProviderProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Initialize provider SDK

    def extract_transaction(self, image_data: bytes, image_format: str) -> dict:
        # Convert image to base64
        # Call provider vision API
        # Parse JSON response
        # Return standardized format
        return {
            "date": "2025-10-29",
            "vendor": "Example Corp",
            "amount": 150.00,
            "category": "Office Supplies",
            "type": "expense",
            "description": "Office supplies purchase"
        }
```text

### 2. Adding New Export Formats

**Steps**:

1. Create new file: `src/agentic_bookkeeper/core/exporters/newformat_exporter.py`
2. Implement similar interface to existing exporters (PDF, CSV, JSON)
3. Accept `report_data` dictionary from ReportGenerator
4. Export to new format
5. Add format to Reports Widget selector

**Example**:

```python
class NewFormatExporter:
    def __init__(self, jurisdiction: str = "CRA", currency: str = "CAD"):
        self.jurisdiction = jurisdiction
        self.currency = currency

    def export(self, report_data: dict, output_path: str) -> bool:
        # Convert report_data to new format
        # Write to output_path
        # Return success/failure
        pass
```text

### 3. Adding New Report Templates

**Steps**:

1. Add new method to `ReportGenerator` class
2. Follow existing pattern: filter → aggregate → format
3. Return standardized report dictionary
4. Add report type to Reports Widget selector

**Example**:

```python
def generate_balance_sheet(self, as_of_date: str) -> dict:
    # Filter transactions up to as_of_date
    # Calculate assets, liabilities, equity
    # Format as report dictionary
    return {
        "report_type": "Balance Sheet",
        "as_of_date": as_of_date,
        "assets": { ... },
        "liabilities": { ... },
        "equity": { ... },
        "metadata": { ... }
    }
```text

### 4. Adding New Tax Jurisdictions

**Steps**:

1. Add jurisdiction to configuration options
2. Add tax code mapping in `ReportGenerator._add_tax_codes_to_categories()`
3. Update jurisdiction label in exporters
4. Add to Settings Dialog jurisdiction selector

**Example**:

```python
# In ReportGenerator
TAX_CODES = {
    "NEW_JURISDICTION": {
        "Advertising": "T1234",
        "Office Supplies": "T5678",
        # ... more categories
    }
}
```text

### 5. Customizing GUI Widgets

**Steps**:

1. Inherit from existing widget class or create new QWidget subclass
2. Follow PySide6 patterns (signals, slots, layouts)
3. Use dependency injection for business logic (TransactionManager, etc.)
4. Add to MainWindow tabs if needed

**Example**:

```python
from PySide6.QtWidgets import QWidget
from agentic_bookkeeper.core.transaction_manager import TransactionManager

class CustomWidget(QWidget):
    def __init__(self, transaction_manager: TransactionManager):
        super().__init__()
        self.transaction_manager = transaction_manager
        self._init_ui()
```text

---

## Security Architecture

### API Key Security

**Encryption**:

- Algorithm: Fernet (symmetric encryption, AES-128-CBC)
- Key derivation: PBKDF2-HMAC-SHA256 (100,000 iterations)
- Password: Machine ID + static salt
- Storage: Encrypted keys in JSON config file

**Best Practices**:

- API keys never stored in plaintext
- Keys encrypted at rest
- Keys decrypted only when needed
- No keys in logs (sanitized by SensitiveDataFilter)

### SQL Injection Prevention

**Protection**:

- 100% parameterized queries (no string concatenation)
- SQLite parameter binding (?, ?, ?)
- Input validation on all user inputs

**Example**:

```python
# Safe (parameterized)
cursor.execute("SELECT * FROM transactions WHERE vendor = ?", (vendor,))

# Unsafe (NEVER DO THIS)
# cursor.execute(f"SELECT * FROM transactions WHERE vendor = '{vendor}'")
```text

### File System Security

**Protection**:

- Path normalization with `pathlib.Path`
- Sandboxing to specific directories
- No execution of uploaded files
- Duplicate detection prevents re-processing

### Logging Security

**Protection**:

- `SensitiveDataFilter` removes API keys from logs
- Pattern matching: `api[_-]?key`, `token`, etc.
- Replacement: `[REDACTED]`
- Applied to all log handlers

---

## Performance Considerations

### Document Processing

**Performance Targets**:

- PDF processing: <30 seconds per document
- Image processing: <30 seconds per document
- Batch processing: 10 documents in <5 minutes

**Optimizations**:

- Efficient PDF parsing with pypdf (vs deprecated PyPDF2)
- Image compression before sending to LLM
- Async processing capability (future enhancement)

### Database Queries

**Performance Targets**:

- Single transaction query: <50ms
- Filtered query: <50ms
- All transactions (1000 records): <250ms
- Category aggregation: <250ms

**Optimizations**:

- Indexes on date, type, category, vendor
- WAL mode for concurrent reads
- Connection reuse (no connection pooling overhead)

### Report Generation

**Performance Targets**:

- Income statement (1000 transactions): <5 seconds
- Expense report (1000 transactions): <5 seconds
- PDF export: <2 seconds
- CSV export: <1 second
- JSON export: <1 second

**Optimizations**:

- Efficient aggregation with pandas
- Decimal precision for monetary calculations
- Streaming for large reports (future enhancement)

### Memory Usage

**Targets**:

- Baseline: <200MB
- Document processing: <200MB
- Report generation: <200MB
- No memory leaks

**Optimizations**:

- File streaming for large PDFs
- Pagination for large result sets (GUI)
- Garbage collection friendly (no circular references)

---

## Deployment Architecture

### Desktop Application

**Platforms**:

- Windows 10/11 (x64)
- Linux (Ubuntu 20.04+, other distros)

**Distribution**:

- PyInstaller executable (Windows)
- Python package (Linux)
- pip installable (all platforms)

**Installation Locations**:

- Application: System-dependent (Program Files, /usr/local/bin, etc.)
- Database: `~/.agentic_bookkeeper/bookkeeper.db`
- Config: `~/.agentic_bookkeeper/config.json`
- Logs: `~/.agentic_bookkeeper/logs/`
- Watch folder: `~/Documents/bookkeeper_inbox/` (configurable)

### Future: Cloud Deployment (Not in MVP)

**Potential Architecture**:

- Web frontend (React/Vue)
- REST API backend (FastAPI/Flask)
- PostgreSQL database
- Cloud storage for documents (S3)
- Background job queue (Celery)
- LLM API calls via backend

---

## Conclusion

The Agentic Bookkeeper architecture is designed for:

- **Modularity**: Clear separation of concerns
- **Extensibility**: Easy to add providers, exporters, reports
- **Testability**: High test coverage with isolated components
- **Performance**: Efficient database queries and report generation
- **Security**: Encrypted API keys, SQL injection prevention, log sanitization
- **Cross-Platform**: Works on Windows and Linux

For more information, see:

- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Development Guide](DEVELOPMENT.md) - Development environment setup
- [Contributing Guide](CONTRIBUTING.md) - Contribution guidelines

---

**End of Architecture Documentation**
