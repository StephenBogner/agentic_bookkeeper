# API Reference

**Project:** Agentic Bookkeeper
**Version:** 0.1.0
**Last Updated:** 2025-10-29

---

## Table of Contents

1. [Overview](#overview)
2. [Core Modules](#core-modules)
   - [DocumentProcessor](#documentprocessor)
   - [DocumentMonitor](#documentmonitor)
   - [TransactionManager](#transactionmanager)
   - [ReportGenerator](#reportgenerator)
3. [Exporters](#exporters)
   - [PDFExporter](#pdfexporter)
   - [CSVExporter](#csvexporter)
   - [JSONExporter](#jsonexporter)
4. [LLM Providers](#llm-providers)
   - [LLMProvider (Abstract)](#llmprovider-abstract)
   - [OpenAIProvider](#openaiprovider)
   - [AnthropicProvider](#anthropicprovider)
   - [XAIProvider](#xaiprovider)
   - [GoogleProvider](#googleprovider)
5. [Models](#models)
   - [Transaction](#transaction)
   - [Database](#database)
6. [Utilities](#utilities)
   - [Config](#config)
   - [Logger](#logger)
7. [Code Examples](#code-examples)

---

## Overview

This document provides comprehensive API documentation for all public modules in the Agentic Bookkeeper system. The API is organized into core modules, exporters, LLM providers, models, and utilities.

### Conventions

- **Type Hints**: All functions use Python type hints
- **Docstrings**: Google-style docstrings for all classes and methods
- **Error Handling**: Specific exceptions documented for each method
- **Return Values**: Clearly specified return types and values

---

## Core Modules

### DocumentProcessor

**Module**: `agentic_bookkeeper.core.document_processor`

Processes financial documents (PDFs and images) and extracts transaction data using LLM vision APIs.

#### Class: `DocumentProcessor`

```python
class DocumentProcessor:
    """
    Process financial documents and extract transaction data.

    Handles document type detection, preprocessing, and LLM extraction.
    """
```

##### Constructor

```python
def __init__(self, llm_provider: LLMProvider, categories: List[str])
```

**Parameters**:
- `llm_provider` (LLMProvider): LLM provider instance for extraction
- `categories` (List[str]): List of valid tax categories

**Example**:
```python
from agentic_bookkeeper.core.document_processor import DocumentProcessor
from agentic_bookkeeper.llm.openai_provider import OpenAIProvider

provider = OpenAIProvider(api_key="your-api-key")
categories = ["Advertising", "Office Supplies", "Travel"]
processor = DocumentProcessor(provider, categories)
```

##### Methods

###### `process_document(document_path: str, validate: bool = True) -> Optional[Transaction]`

Process a document and extract transaction data.

**Parameters**:
- `document_path` (str): Path to document file (PDF or image)
- `validate` (bool, optional): Whether to validate extracted data. Defaults to True.

**Returns**:
- `Optional[Transaction]`: Transaction object or None if extraction fails

**Raises**:
- `FileNotFoundError`: If document doesn't exist
- `ValueError`: If document format is unsupported

**Supported Formats**: `.pdf`, `.png`, `.jpg`, `.jpeg`

**Example**:
```python
transaction = processor.process_document("/path/to/receipt.pdf")
if transaction:
    print(f"Extracted: {transaction.vendor}, ${transaction.amount}")
```

###### `is_supported_format(file_path: str) -> bool`

Check if file format is supported.

**Parameters**:
- `file_path` (str): Path to file

**Returns**:
- `bool`: True if format is supported

**Example**:
```python
if processor.is_supported_format("receipt.pdf"):
    transaction = processor.process_document("receipt.pdf")
```

---

### DocumentMonitor

**Module**: `agentic_bookkeeper.core.document_monitor`

Monitors a directory for new documents and automatically processes them.

#### Class: `DocumentMonitor`

```python
class DocumentMonitor:
    """
    Monitor a directory for new financial documents.

    Uses watchdog to detect file system events and process new documents.
    """
```

##### Constructor

```python
def __init__(self, watch_folder: str, processor: DocumentProcessor,
             transaction_manager: TransactionManager)
```

**Parameters**:
- `watch_folder` (str): Directory to monitor
- `processor` (DocumentProcessor): Document processor instance
- `transaction_manager` (TransactionManager): Transaction manager for storing results

**Example**:
```python
from agentic_bookkeeper.core.document_monitor import DocumentMonitor

monitor = DocumentMonitor(
    watch_folder="/home/user/bookkeeper_inbox",
    processor=processor,
    transaction_manager=transaction_manager
)
```

##### Methods

###### `start() -> None`

Start monitoring the watch folder.

**Example**:
```python
monitor.start()
print("Monitoring started. Waiting for documents...")
```

###### `stop() -> None`

Stop monitoring the watch folder.

**Example**:
```python
monitor.stop()
print("Monitoring stopped.")
```

###### `is_running() -> bool`

Check if monitor is currently running.

**Returns**:
- `bool`: True if monitoring is active

**Example**:
```python
if monitor.is_running():
    print("Monitor is active")
```

---

### TransactionManager

**Module**: `agentic_bookkeeper.core.transaction_manager`

Manages CRUD operations for transactions in the database.

#### Class: `TransactionManager`

```python
class TransactionManager:
    """
    Manager for transaction database operations.

    Handles create, read, update, delete, and query operations.
    """
```

##### Constructor

```python
def __init__(self, database: Database)
```

**Parameters**:
- `database` (Database): Database instance

**Example**:
```python
from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.models.database import Database

db = Database("~/.agentic_bookkeeper/bookkeeper.db")
manager = TransactionManager(db)
```

##### Methods

###### `create_transaction(transaction: Transaction) -> int`

Create a new transaction.

**Parameters**:
- `transaction` (Transaction): Transaction object to create

**Returns**:
- `int`: ID of created transaction

**Raises**:
- `ValueError`: If transaction data is invalid
- `Exception`: If database operation fails

**Example**:
```python
from agentic_bookkeeper.models.transaction import Transaction
from datetime import date

transaction = Transaction(
    date=date.today(),
    vendor="Office Depot",
    amount=150.00,
    category="Office Supplies",
    type="expense",
    description="Printer paper and toner"
)
transaction_id = manager.create_transaction(transaction)
print(f"Created transaction ID: {transaction_id}")
```

###### `get_transaction(transaction_id: int) -> Optional[Transaction]`

Get a transaction by ID.

**Parameters**:
- `transaction_id` (int): Transaction ID

**Returns**:
- `Optional[Transaction]`: Transaction object or None if not found

**Example**:
```python
transaction = manager.get_transaction(123)
if transaction:
    print(f"Found: {transaction.vendor}, ${transaction.amount}")
```

###### `get_all_transactions() -> List[Transaction]`

Get all transactions, ordered by date (descending).

**Returns**:
- `List[Transaction]`: List of all transactions

**Example**:
```python
transactions = manager.get_all_transactions()
print(f"Total transactions: {len(transactions)}")
```

###### `update_transaction(transaction: Transaction) -> bool`

Update an existing transaction.

**Parameters**:
- `transaction` (Transaction): Transaction object with updated data (must have ID)

**Returns**:
- `bool`: True if update successful

**Raises**:
- `ValueError`: If transaction has no ID
- `Exception`: If database operation fails

**Example**:
```python
transaction = manager.get_transaction(123)
transaction.amount = 175.00
transaction.description = "Updated description"
manager.update_transaction(transaction)
```

###### `delete_transaction(transaction_id: int) -> bool`

Delete a transaction by ID.

**Parameters**:
- `transaction_id` (int): Transaction ID

**Returns**:
- `bool`: True if deletion successful

**Example**:
```python
manager.delete_transaction(123)
print("Transaction deleted")
```

###### `filter_by_type(transaction_type: str) -> List[Transaction]`

Filter transactions by type.

**Parameters**:
- `transaction_type` (str): "income" or "expense"

**Returns**:
- `List[Transaction]`: Filtered transactions

**Example**:
```python
expenses = manager.filter_by_type("expense")
print(f"Total expenses: {len(expenses)}")
```

###### `filter_by_category(category: str) -> List[Transaction]`

Filter transactions by category.

**Parameters**:
- `category` (str): Category name

**Returns**:
- `List[Transaction]`: Filtered transactions

**Example**:
```python
travel = manager.filter_by_category("Travel")
total = sum(t.amount for t in travel)
print(f"Total travel expenses: ${total:.2f}")
```

###### `filter_by_date_range(start_date: str, end_date: str) -> List[Transaction]`

Filter transactions by date range.

**Parameters**:
- `start_date` (str): Start date (ISO format: YYYY-MM-DD)
- `end_date` (str): End date (ISO format: YYYY-MM-DD)

**Returns**:
- `List[Transaction]`: Filtered transactions

**Example**:
```python
transactions = manager.filter_by_date_range("2025-01-01", "2025-12-31")
print(f"Transactions in 2025: {len(transactions)}")
```

###### `search_transactions(query: str) -> List[Transaction]`

Search transactions by vendor or description.

**Parameters**:
- `query` (str): Search query (case-insensitive)

**Returns**:
- `List[Transaction]`: Matching transactions

**Example**:
```python
results = manager.search_transactions("office")
for t in results:
    print(f"{t.vendor}: ${t.amount}")
```

###### `get_statistics() -> Dict[str, Any]`

Get summary statistics for all transactions.

**Returns**:
- `Dict[str, Any]`: Dictionary with statistics:
  - `total_transactions` (int): Total count
  - `total_income` (float): Sum of income
  - `total_expenses` (float): Sum of expenses
  - `net_income` (float): Income minus expenses
  - `categories` (Dict[str, float]): Total per category

**Example**:
```python
stats = manager.get_statistics()
print(f"Net income: ${stats['net_income']:.2f}")
print(f"Categories: {stats['categories']}")
```

---

### ReportGenerator

**Module**: `agentic_bookkeeper.core.report_generator`

Generates financial reports from transaction data.

#### Class: `ReportGenerator`

```python
class ReportGenerator:
    """
    Generate financial reports from transactions.

    Supports income statements, expense reports, and custom reports.
    """
```

##### Constructor

```python
def __init__(self, transaction_manager: TransactionManager,
             jurisdiction: str = "CRA", currency: str = "CAD")
```

**Parameters**:
- `transaction_manager` (TransactionManager): Transaction manager instance
- `jurisdiction` (str, optional): Tax jurisdiction ("CRA" or "IRS"). Defaults to "CRA".
- `currency` (str, optional): Currency code ("CAD", "USD"). Defaults to "CAD".

**Example**:
```python
from agentic_bookkeeper.core.report_generator import ReportGenerator

generator = ReportGenerator(
    transaction_manager=manager,
    jurisdiction="CRA",
    currency="CAD"
)
```

##### Methods

###### `generate_income_statement(start_date: str, end_date: str) -> Dict[str, Any]`

Generate income statement for date range.

**Parameters**:
- `start_date` (str): Start date (ISO format: YYYY-MM-DD)
- `end_date` (str): End date (ISO format: YYYY-MM-DD)

**Returns**:
- `Dict[str, Any]`: Income statement dictionary with:
  - `report_type` (str): "Income Statement"
  - `start_date` (str): Report start date
  - `end_date` (str): Report end date
  - `total_income` (Decimal): Total income
  - `total_expenses` (Decimal): Total expenses
  - `net_income` (Decimal): Net income
  - `income_by_category` (Dict[str, Decimal]): Income breakdown
  - `expenses_by_category` (Dict[str, Decimal]): Expense breakdown
  - `metadata` (Dict): Report metadata (jurisdiction, currency, generated_at)

**Example**:
```python
report = generator.generate_income_statement("2025-01-01", "2025-12-31")
print(f"Net Income: {report['net_income']}")
print(f"Total Expenses: {report['total_expenses']}")
```

###### `generate_expense_report(start_date: str, end_date: str) -> Dict[str, Any]`

Generate expense report with tax codes.

**Parameters**:
- `start_date` (str): Start date (ISO format: YYYY-MM-DD)
- `end_date` (str): End date (ISO format: YYYY-MM-DD)

**Returns**:
- `Dict[str, Any]`: Expense report dictionary with:
  - `report_type` (str): "Expense Report"
  - `start_date` (str): Report start date
  - `end_date` (str): Report end date
  - `total_expenses` (Decimal): Total expenses
  - `expenses_by_category` (List[Dict]): Categories with amounts, percentages, and tax codes
  - `metadata` (Dict): Report metadata

**Example**:
```python
report = generator.generate_expense_report("2025-01-01", "2025-12-31")
for category in report['expenses_by_category']:
    print(f"{category['name']}: ${category['amount']} ({category['percentage']}%) - Code: {category['tax_code']}")
```

---

## Exporters

### PDFExporter

**Module**: `agentic_bookkeeper.core.exporters.pdf_exporter`

Exports reports to professional PDF format using ReportLab.

#### Class: `PDFExporter`

```python
class PDFExporter:
    """Export reports to PDF format."""
```

##### Constructor

```python
def __init__(self, jurisdiction: str = "CRA", currency: str = "CAD")
```

**Parameters**:
- `jurisdiction` (str, optional): Tax jurisdiction. Defaults to "CRA".
- `currency` (str, optional): Currency code. Defaults to "CAD".

##### Methods

###### `export(report_data: Dict[str, Any], output_path: str) -> bool`

Export report to PDF file.

**Parameters**:
- `report_data` (Dict): Report dictionary from ReportGenerator
- `output_path` (str): Path for output PDF file

**Returns**:
- `bool`: True if export successful

**Example**:
```python
from agentic_bookkeeper.core.exporters.pdf_exporter import PDFExporter

exporter = PDFExporter(jurisdiction="CRA", currency="CAD")
report = generator.generate_income_statement("2025-01-01", "2025-12-31")
exporter.export(report, "/path/to/income_statement.pdf")
```

---

### CSVExporter

**Module**: `agentic_bookkeeper.core.exporters.csv_exporter`

Exports reports to Excel-compatible CSV format using pandas.

#### Class: `CSVExporter`

```python
class CSVExporter:
    """Export reports to CSV format."""
```

##### Constructor

```python
def __init__(self, jurisdiction: str = "CRA", currency: str = "CAD")
```

**Parameters**:
- `jurisdiction` (str, optional): Tax jurisdiction. Defaults to "CRA".
- `currency` (str, optional): Currency code. Defaults to "CAD".

##### Methods

###### `export(report_data: Dict[str, Any], output_path: str) -> bool`

Export report to CSV file.

**Parameters**:
- `report_data` (Dict): Report dictionary from ReportGenerator
- `output_path` (str): Path for output CSV file

**Returns**:
- `bool`: True if export successful

**Features**:
- UTF-8 BOM encoding for Excel compatibility
- Currency formatting with thousands separator
- Percentage formatting
- Excel formula injection prevention

**Example**:
```python
from agentic_bookkeeper.core.exporters.csv_exporter import CSVExporter

exporter = CSVExporter(jurisdiction="IRS", currency="USD")
report = generator.generate_expense_report("2025-01-01", "2025-12-31")
exporter.export(report, "/path/to/expenses.csv")
```

---

### JSONExporter

**Module**: `agentic_bookkeeper.core.exporters.json_exporter`

Exports reports to structured JSON format with schema versioning.

#### Class: `JSONExporter`

```python
class JSONExporter:
    """Export reports to JSON format."""
```

##### Constructor

```python
def __init__(self, jurisdiction: str = "CRA", currency: str = "CAD")
```

**Parameters**:
- `jurisdiction` (str, optional): Tax jurisdiction. Defaults to "CRA".
- `currency` (str, optional): Currency code. Defaults to "CAD".

##### Methods

###### `export(report_data: Dict[str, Any], output_path: str, pretty: bool = True) -> bool`

Export report to JSON file.

**Parameters**:
- `report_data` (Dict): Report dictionary from ReportGenerator
- `output_path` (str): Path for output JSON file
- `pretty` (bool, optional): Pretty-print JSON. Defaults to True.

**Returns**:
- `bool`: True if export successful

**Features**:
- Schema versioning (version 1.0)
- Pretty printing (human-readable)
- Numeric values without currency symbols
- Comprehensive metadata

**Example**:
```python
from agentic_bookkeeper.core.exporters.json_exporter import JSONExporter

exporter = JSONExporter(jurisdiction="CRA", currency="CAD")
report = generator.generate_income_statement("2025-01-01", "2025-12-31")
exporter.export(report, "/path/to/report.json", pretty=True)
```

---

## LLM Providers

### LLMProvider (Abstract)

**Module**: `agentic_bookkeeper.llm.llm_provider`

Abstract base class for all LLM provider implementations.

#### Class: `LLMProvider`

```python
class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
```

##### Constructor

```python
def __init__(self, api_key: str, max_retries: int = 3, timeout: int = 30)
```

**Parameters**:
- `api_key` (str): API key for the provider
- `max_retries` (int, optional): Maximum retry attempts. Defaults to 3.
- `timeout` (int, optional): Timeout in seconds. Defaults to 30.

##### Abstract Methods

###### `provider_name() -> str` (property)

Get the name of the provider.

###### `extract_transaction(document_path: str, categories: List[str]) -> ExtractionResult`

Extract transaction data from a document.

**Parameters**:
- `document_path` (str): Path to document (PDF or image)
- `categories` (List[str]): List of valid tax categories

**Returns**:
- `ExtractionResult`: Result object with:
  - `success` (bool): Whether extraction succeeded
  - `transaction_data` (Optional[Dict]): Extracted data if successful
  - `confidence` (float): Confidence score (0.0 to 1.0)
  - `error_message` (Optional[str]): Error message if failed
  - `provider` (str): Provider name
  - `processing_time` (float): Time taken in seconds

---

### OpenAIProvider

**Module**: `agentic_bookkeeper.llm.openai_provider`

OpenAI GPT-4 Vision implementation.

#### Class: `OpenAIProvider`

```python
class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4 Vision provider."""
```

##### Constructor

```python
def __init__(self, api_key: str, model: str = "gpt-4-vision-preview",
             max_retries: int = 3, timeout: int = 30)
```

**Parameters**:
- `api_key` (str): OpenAI API key
- `model` (str, optional): Model name. Defaults to "gpt-4-vision-preview".
- `max_retries` (int, optional): Maximum retry attempts. Defaults to 3.
- `timeout` (int, optional): Timeout in seconds. Defaults to 30.

**Example**:
```python
from agentic_bookkeeper.llm.openai_provider import OpenAIProvider

provider = OpenAIProvider(
    api_key="sk-...",
    model="gpt-4-vision-preview"
)
```

---

### AnthropicProvider

**Module**: `agentic_bookkeeper.llm.anthropic_provider`

Anthropic Claude Vision implementation.

#### Class: `AnthropicProvider`

```python
class AnthropicProvider(LLMProvider):
    """Anthropic Claude Vision provider."""
```

##### Constructor

```python
def __init__(self, api_key: str, model: str = "claude-3-opus-20240229",
             max_retries: int = 3, timeout: int = 30)
```

**Parameters**:
- `api_key` (str): Anthropic API key
- `model` (str, optional): Model name. Defaults to "claude-3-opus-20240229".
- `max_retries` (int, optional): Maximum retry attempts. Defaults to 3.
- `timeout` (int, optional): Timeout in seconds. Defaults to 30.

**Example**:
```python
from agentic_bookkeeper.llm.anthropic_provider import AnthropicProvider

provider = AnthropicProvider(
    api_key="sk-ant-...",
    model="claude-3-opus-20240229"
)
```

---

### XAIProvider

**Module**: `agentic_bookkeeper.llm.xai_provider`

XAI Grok Vision implementation.

#### Class: `XAIProvider`

```python
class XAIProvider(LLMProvider):
    """XAI Grok Vision provider."""
```

##### Constructor

```python
def __init__(self, api_key: str, model: str = "grok-vision-beta",
             max_retries: int = 3, timeout: int = 30)
```

**Parameters**:
- `api_key` (str): XAI API key
- `model` (str, optional): Model name. Defaults to "grok-vision-beta".
- `max_retries` (int, optional): Maximum retry attempts. Defaults to 3.
- `timeout` (int, optional): Timeout in seconds. Defaults to 30.

**Example**:
```python
from agentic_bookkeeper.llm.xai_provider import XAIProvider

provider = XAIProvider(
    api_key="xai-...",
    model="grok-vision-beta"
)
```

---

### GoogleProvider

**Module**: `agentic_bookkeeper.llm.google_provider`

Google Gemini Vision implementation.

#### Class: `GoogleProvider`

```python
class GoogleProvider(LLMProvider):
    """Google Gemini Vision provider."""
```

##### Constructor

```python
def __init__(self, api_key: str, model: str = "gemini-pro-vision",
             max_retries: int = 3, timeout: int = 30)
```

**Parameters**:
- `api_key` (str): Google API key
- `model` (str, optional): Model name. Defaults to "gemini-pro-vision".
- `max_retries` (int, optional): Maximum retry attempts. Defaults to 3.
- `timeout` (int, optional): Timeout in seconds. Defaults to 30.

**Example**:
```python
from agentic_bookkeeper.llm.google_provider import GoogleProvider

provider = GoogleProvider(
    api_key="AIza...",
    model="gemini-pro-vision"
)
```

---

## Models

### Transaction

**Module**: `agentic_bookkeeper.models.transaction`

Transaction data model.

#### Class: `Transaction`

```python
@dataclass
class Transaction:
    """Financial transaction data model."""
```

##### Attributes

- `id` (Optional[int]): Transaction ID (None for new transactions)
- `date` (date): Transaction date
- `vendor` (str): Vendor/customer name
- `amount` (float): Transaction amount
- `category` (str): Tax category
- `type` (str): Transaction type ("income" or "expense")
- `description` (Optional[str]): Description/notes
- `document_path` (Optional[str]): Path to source document
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Update timestamp

##### Methods

###### `from_dict(data: Dict[str, Any]) -> Transaction` (classmethod)

Create Transaction from dictionary.

**Example**:
```python
from agentic_bookkeeper.models.transaction import Transaction
from datetime import date

data = {
    "date": "2025-10-29",
    "vendor": "Office Depot",
    "amount": 150.00,
    "category": "Office Supplies",
    "type": "expense",
    "description": "Printer supplies"
}
transaction = Transaction.from_dict(data)
```

###### `to_dict() -> Dict[str, Any]`

Convert Transaction to dictionary.

**Example**:
```python
data = transaction.to_dict()
print(data["vendor"])  # "Office Depot"
```

###### `from_db_row(row: tuple) -> Transaction` (classmethod)

Create Transaction from database row.

**Example**:
```python
cursor.execute("SELECT * FROM transactions WHERE id = ?", (123,))
row = cursor.fetchone()
transaction = Transaction.from_db_row(row)
```

---

### Database

**Module**: `agentic_bookkeeper.models.database`

SQLite database connection manager.

#### Class: `Database`

```python
class Database:
    """SQLite database connection manager."""
```

##### Constructor

```python
def __init__(self, db_path: str)
```

**Parameters**:
- `db_path` (str): Path to SQLite database file

**Example**:
```python
from agentic_bookkeeper.models.database import Database

db = Database("~/.agentic_bookkeeper/bookkeeper.db")
db.connect()
db.initialize_schema()
```

##### Methods

###### `connect() -> None`

Connect to database and enable WAL mode.

###### `close() -> None`

Close database connection.

###### `initialize_schema() -> None`

Initialize database schema (create tables and indexes).

###### `get_cursor() -> ContextManager`

Get database cursor context manager.

**Example**:
```python
with db.get_cursor() as cursor:
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
```

###### `backup(backup_path: str) -> bool`

Create database backup.

**Parameters**:
- `backup_path` (str): Path for backup file

**Returns**:
- `bool`: True if backup successful

**Example**:
```python
db.backup("/path/to/backup.db")
```

---

## Utilities

### Config

**Module**: `agentic_bookkeeper.utils.config`

Configuration management with encrypted API key storage.

#### Class: `Config`

```python
class Config:
    """Application configuration manager."""
```

##### Methods

###### `load_config() -> Dict[str, Any]` (staticmethod)

Load configuration from file.

**Returns**:
- `Dict[str, Any]`: Configuration dictionary

###### `save_config(config: Dict[str, Any]) -> None` (staticmethod)

Save configuration to file.

**Parameters**:
- `config` (Dict): Configuration dictionary

###### `get_api_key(provider: str) -> Optional[str]` (staticmethod)

Get decrypted API key for provider.

**Parameters**:
- `provider` (str): Provider name ("openai", "anthropic", "xai", "google")

**Returns**:
- `Optional[str]`: Decrypted API key or None

###### `set_api_key(provider: str, api_key: str) -> None` (staticmethod)

Set encrypted API key for provider.

**Parameters**:
- `provider` (str): Provider name
- `api_key` (str): API key to encrypt and store

**Example**:
```python
from agentic_bookkeeper.utils.config import Config

# Set API key (encrypted)
Config.set_api_key("openai", "sk-...")

# Get API key (decrypted)
api_key = Config.get_api_key("openai")
```

---

### Logger

**Module**: `agentic_bookkeeper.utils.logger`

Logging setup with sensitive data filtering.

#### Functions

###### `setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None`

Setup logging configuration.

**Parameters**:
- `log_level` (str, optional): Log level ("DEBUG", "INFO", "WARNING", "ERROR"). Defaults to "INFO".
- `log_file` (Optional[str], optional): Log file path. Defaults to None (console only).

**Example**:
```python
from agentic_bookkeeper.utils.logger import setup_logging

setup_logging(log_level="DEBUG", log_file="app.log")
```

#### Class: `SensitiveDataFilter`

```python
class SensitiveDataFilter(logging.Filter):
    """Filter sensitive data from log records."""
```

Automatically removes API keys, tokens, and other sensitive data from logs.

---

## Code Examples

### Example 1: Process a Document

```python
from agentic_bookkeeper.llm.openai_provider import OpenAIProvider
from agentic_bookkeeper.core.document_processor import DocumentProcessor
from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.models.database import Database

# Initialize components
db = Database("~/.agentic_bookkeeper/bookkeeper.db")
db.connect()
db.initialize_schema()

provider = OpenAIProvider(api_key="sk-...")
categories = ["Advertising", "Office Supplies", "Travel", "Utilities"]
processor = DocumentProcessor(provider, categories)
manager = TransactionManager(db)

# Process document
transaction = processor.process_document("/path/to/receipt.pdf")
if transaction:
    transaction_id = manager.create_transaction(transaction)
    print(f"Transaction created: ID {transaction_id}")
else:
    print("Extraction failed")
```

### Example 2: Generate and Export Report

```python
from agentic_bookkeeper.core.report_generator import ReportGenerator
from agentic_bookkeeper.core.exporters.pdf_exporter import PDFExporter
from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.models.database import Database

# Initialize components
db = Database("~/.agentic_bookkeeper/bookkeeper.db")
db.connect()
manager = TransactionManager(db)
generator = ReportGenerator(manager, jurisdiction="CRA", currency="CAD")
exporter = PDFExporter(jurisdiction="CRA", currency="CAD")

# Generate report
report = generator.generate_income_statement("2025-01-01", "2025-12-31")
print(f"Net Income: {report['net_income']}")

# Export to PDF
exporter.export(report, "/path/to/income_statement.pdf")
print("Report exported successfully")
```

### Example 3: Monitor Directory for Documents

```python
from agentic_bookkeeper.core.document_monitor import DocumentMonitor
from agentic_bookkeeper.core.document_processor import DocumentProcessor
from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.models.database import Database
from agentic_bookkeeper.llm.openai_provider import OpenAIProvider
import time

# Initialize components
db = Database("~/.agentic_bookkeeper/bookkeeper.db")
db.connect()
db.initialize_schema()

provider = OpenAIProvider(api_key="sk-...")
categories = ["Advertising", "Office Supplies", "Travel"]
processor = DocumentProcessor(provider, categories)
manager = TransactionManager(db)

# Start monitoring
monitor = DocumentMonitor(
    watch_folder="/home/user/bookkeeper_inbox",
    processor=processor,
    transaction_manager=manager
)
monitor.start()

print("Monitoring started. Drop documents in watch folder...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    monitor.stop()
    print("Monitoring stopped")
```

### Example 4: Add Custom LLM Provider

```python
from agentic_bookkeeper.llm.llm_provider import LLMProvider, ExtractionResult
from typing import List
import time

class CustomProvider(LLMProvider):
    """Custom LLM provider implementation."""

    @property
    def provider_name(self) -> str:
        return "Custom Provider"

    def extract_transaction(self, document_path: str,
                          categories: List[str]) -> ExtractionResult:
        start_time = time.time()

        try:
            # Your custom extraction logic here
            # 1. Read document
            # 2. Call your LLM API
            # 3. Parse response

            transaction_data = {
                "date": "2025-10-29",
                "vendor": "Example Corp",
                "amount": 150.00,
                "category": "Office Supplies",
                "type": "expense",
                "description": "Example transaction"
            }

            return ExtractionResult(
                success=True,
                transaction_data=transaction_data,
                confidence=0.95,
                provider=self.provider_name,
                processing_time=time.time() - start_time
            )

        except Exception as e:
            return ExtractionResult(
                success=False,
                error_message=str(e),
                provider=self.provider_name,
                processing_time=time.time() - start_time
            )

    def _prepare_prompt(self, categories: List[str]) -> str:
        return f"Extract transaction from document. Categories: {categories}"

# Usage
provider = CustomProvider(api_key="your-api-key")
processor = DocumentProcessor(provider, categories)
```

### Example 5: Batch Processing

```python
from pathlib import Path
from agentic_bookkeeper.core.document_processor import DocumentProcessor
from agentic_bookkeeper.core.transaction_manager import TransactionManager

# Process all documents in directory
documents_dir = Path("/path/to/documents")
success_count = 0
fail_count = 0

for doc_path in documents_dir.glob("*.pdf"):
    print(f"Processing: {doc_path.name}")

    transaction = processor.process_document(str(doc_path))
    if transaction:
        manager.create_transaction(transaction)
        success_count += 1
        print(f"  ✓ Success: {transaction.vendor}, ${transaction.amount}")
    else:
        fail_count += 1
        print(f"  ✗ Failed")

print(f"\nResults: {success_count} success, {fail_count} failed")
```

---

## See Also

- [Architecture Documentation](ARCHITECTURE.md) - System architecture overview
- [Development Guide](DEVELOPMENT.md) - Development environment setup
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [User Guide](USER_GUIDE.md) - End-user documentation

---

**End of API Reference**
