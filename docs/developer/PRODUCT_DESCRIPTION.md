# Agentic Bookkeeper - Product Description

## Executive Summary

**Agentic Bookkeeper** is a lightweight, automated bookkeeping tool designed for small businesses and sole proprietors.
The system monitors a designated directory for financial documents (invoices, receipts, payments), uses AI to extract
transaction data, stores it in a local SQLite database, and generates compliant financial statements on demand. The
tool supports both Canadian (CRA) and US (IRS) tax accounting categories.

---

## Product Vision

**Mission Statement:**
To provide small business owners and sole proprietors with a simple, automated way to maintain accurate financial
records without manual data entry or expensive accounting software subscriptions.

**Core Value Proposition:**  
Drop documents in a folder, get organized financial records and professional statements automatically.

---

## Key Features

### 1. **Automated Document Monitoring**

- Monitors a user-specified directory for new financial documents
- Supports common formats: PDF, PNG, JPG, JPEG
- Processes documents automatically when detected
- Moves processed documents to archive folder with timestamps

### 2. **AI-Powered Data Extraction**

- Uses LLM API calls to read and extract data from documents
- Identifies document type (invoice, receipt, payment)
- Extracts key fields:
  - Date
  - Vendor/Customer name
  - Amount
  - Description/Line items
  - Tax amounts (GST/HST/PST or Sales Tax)
  - Payment method
- Handles multiple document formats and layouts

### 3. **Transaction Database**

- SQLite database stores all transaction records
- Schema includes:
  - Transaction ID
  - Date
  - Type (Income/Expense)
  - Category (CRA or IRS compliant)
  - Vendor/Customer
  - Description
  - Amount
  - Tax amount
  - Document reference (filename)
  - Entry timestamp

### 4. **Financial Statement Generation**

- Generate Income Statement (Profit & Loss)
- Generate Expense Report by category
- Date range filtering (monthly, quarterly, annual, custom)
- Export formats: PDF, CSV, JSON
- Professional formatting suitable for tax filing

### 5. **Compliance Categories**

**CRA (Canada) Expense Categories:**

- Advertising
- Business tax, fees, licenses
- Insurance
- Interest and bank charges
- Meals and entertainment (50% deductible)
- Motor vehicle expenses
- Office expenses
- Supplies
- Legal and professional fees
- Rent
- Salaries and wages
- Telephone and utilities
- Travel
- Other expenses

**IRS (United States) Categories:**

- Advertising
- Car and truck expenses
- Commissions and fees
- Contract labor
- Depletion
- Depreciation
- Employee benefit programs
- Insurance
- Interest (mortgage/other)
- Legal and professional services
- Office expense
- Pension and profit-sharing plans
- Rent or lease
- Repairs and maintenance
- Supplies
- Taxes and licenses
- Travel and meals
- Utilities
- Wages
- Other expenses

### 6. **User Interface**

- Simple PySide6 GUI with three main views:
  1. **Dashboard**: Status, recent transactions, quick stats
  2. **Transactions**: View/edit/delete transaction records
  3. **Reports**: Generate and export financial statements
- Settings panel for:
  - Directory configuration
  - LLM provider selection and API keys
  - Tax jurisdiction (CRA/IRS)
  - Fiscal year settings

---

## Technical Architecture

### System Components

```text
agentic-bookkeeper/
├── src/
│   ├── core/
│   │   ├── document_monitor.py      # Directory watching
│   │   ├── document_processor.py    # LLM extraction logic
│   │   ├── transaction_manager.py   # Database operations
│   │   └── report_generator.py      # Statement creation
│   ├── models/
│   │   ├── transaction.py           # Transaction data model
│   │   └── database.py              # SQLite schema & connection
│   ├── llm/
│   │   ├── llm_provider.py          # Abstract base class
│   │   ├── openai_provider.py       # OpenAI implementation
│   │   ├── anthropic_provider.py    # Anthropic implementation
│   │   ├── xai_provider.py          # XAI implementation
│   │   └── google_provider.py       # Google implementation
│   ├── gui/
│   │   ├── main_window.py           # Main application window
│   │   ├── dashboard_widget.py      # Dashboard view
│   │   ├── transactions_widget.py   # Transaction list/edit
│   │   └── reports_widget.py        # Report generation UI
│   ├── utils/
│   │   ├── config.py                # Configuration management
│   │   ├── logger.py                # Logging setup
│   │   └── validators.py            # Input validation
│   └── tests/
│       ├── test_document_processor.py
│       ├── test_transaction_manager.py
│       └── test_report_generator.py
├── config/
│   ├── .env.example
│   └── categories_cra.json
│   └── categories_irs.json
├── data/                            # Created at runtime
│   ├── bookkeeper.db                # SQLite database
│   ├── watch/                       # Directory to monitor
│   └── processed/                   # Archive for processed docs
├── docs/
│   ├── README.md
│   ├── USER_GUIDE.md
│   └── API.md
├── requirements.txt
└── main.py                          # Application entry point
```

### Core Technologies

- **Language**: Python 3.10+
- **GUI**: PySide6
- **Database**: SQLite3
- **LLM Integration**: Direct API calls (requests library)
- **Document Processing**: PyPDF2, Pillow, pytesseract (OCR backup)
- **Directory Monitoring**: watchdog library
- **Report Generation**: ReportLab (PDF), pandas (CSV)
- **Configuration**: python-dotenv, JSON
- **Testing**: pytest (>80% coverage)
- **Logging**: Python logging module

---

## User Workflow

### Initial Setup

1. Launch Agentic Bookkeeper application
2. Configure settings:
   - Select tax jurisdiction (CRA/IRS)
   - Set fiscal year start date
   - Choose LLM provider and enter API key
   - Specify watch directory path
3. Start monitoring service

### Day-to-Day Operation

1. Save/scan financial documents to watch directory
2. System automatically:
   - Detects new document
   - Calls LLM to extract transaction data
   - Prompts user to review/confirm categorization
   - Saves transaction to database
   - Moves document to processed folder
3. User reviews dashboard for recent activity

### Generating Reports

1. Click "Generate Report" button
2. Select report type (Income Statement, Expense Report)
3. Choose date range
4. Select export format (PDF/CSV/JSON)
5. Save report to desired location

### Transaction Management

1. View all transactions in searchable table
2. Edit transaction details if extraction was incorrect
3. Delete duplicate or erroneous entries
4. Manually add transactions if needed

---

## Database Schema

### Transactions Table

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    category TEXT NOT NULL,
    vendor_customer TEXT,
    description TEXT,
    amount REAL NOT NULL,
    tax_amount REAL DEFAULT 0,
    document_filename TEXT,
    created_at TEXT NOT NULL,
    modified_at TEXT NOT NULL
);
```

### Configuration Table

```sql
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

---

## LLM Extraction Prompt Strategy

### Document Analysis Prompt Template

```text
You are a financial document analyzer. Extract transaction information from the provided document.

Document Type: Identify if this is an invoice, receipt, or payment record.

Extract the following information:
1. Date of transaction (YYYY-MM-DD format)
2. Vendor/Customer name
3. Total amount (numeric only)
4. Tax amount if shown (numeric only)
5. Description of goods/services
6. Category from this list: [insert CRA or IRS categories]

Return ONLY valid JSON in this format:
{
  "document_type": "invoice|receipt|payment",
  "date": "YYYY-MM-DD",
  "transaction_type": "income|expense",
  "vendor_customer": "string",
  "amount": number,
  "tax_amount": number,
  "description": "string",
  "category": "string"
}

If you cannot extract a field with confidence, use null.
```

---

## Implementation Roadmap

### Phase 1: Core Functionality (Weeks 1-4)

- SQLite database schema and models
- Document monitor with watchdog
- LLM provider abstraction class
- OpenAI and Anthropic provider implementations
- Basic document extraction and database storage
- Command-line interface for testing

### Phase 2: GUI Development (Weeks 5-8)

- PySide6 main window framework
- Dashboard widget with summary statistics
- Transaction list view with edit/delete
- Settings dialog for configuration
- Start/stop monitoring controls

### Phase 3: Reporting Engine (Weeks 9-10)

- Report generator class
- Income statement template
- Expense report template
- PDF export using ReportLab
- CSV/JSON export functionality

### Phase 4: Testing & Documentation (Weeks 11-12)

- pytest unit tests for all core classes
- Integration testing with sample documents
- User guide documentation
- Code documentation (docstrings)
- Installation instructions

### Phase 5: Refinement (Weeks 13-14)

- Error handling improvements
- Logging enhancements
- Performance optimization
- Bug fixes from testing
- Package for distribution

---

## Success Metrics

### Functional Metrics

- **Extraction Accuracy**: >90% for standard invoices/receipts
- **Processing Speed**: <30 seconds per document
- **Database Reliability**: Zero data loss during normal operation
- **Report Accuracy**: 100% accurate calculations from stored data

### User Experience Metrics

- **Setup Time**: <10 minutes from install to first document processed
- **Learning Curve**: User can generate first report within 30 minutes
- **Error Rate**: <5% of documents require manual correction

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM extraction errors | Medium | User review/confirmation before saving |
| API rate limits/costs | Low | Configurable provider selection, caching |
| Document format variations | Medium | Multiple LLM attempts, OCR fallback |
| Database corruption | High | Regular automated backups, transaction logging |
| Incorrect categorization | Medium | Easy edit interface, learning from corrections |

---

## Development Requirements

### Single Developer Timeline

- **Estimated Duration**: 14 weeks (part-time) or 7 weeks (full-time)
- **Skills Required**: Python OOP, PySide6, SQLite, LLM API integration

### Infrastructure

- **Development**: Local machine (Windows/Ubuntu)
- **LLM APIs**: API keys for chosen providers
- **Version Control**: GitHub repository
- **Testing**: Local SQLite database, sample financial documents

### Estimated Costs

- **LLM API Usage**: $20-50/month during development
- **No infrastructure costs**: Fully local application
- **Total Development Budget**: <$100 (API costs only)

---

## Deployment

### Distribution

- **Windows**: Standalone .exe using PyInstaller
- **Linux**: Python package with requirements.txt
- **Installation**: Simple installer or pip install

### Requirements

- Python 3.10+ (if not using standalone executable)
- 100MB disk space
- Internet connection (for LLM API calls)

---

## Future Enhancements (Post-MVP)

- Bank statement import and reconciliation
- Multi-year comparison reports
- Budget tracking and alerts
- Export to QuickBooks/Xero formats
- Mobile app for receipt capture
- Multi-currency support
- Audit trail and document search

---

## Conclusion

**Agentic Bookkeeper** provides a focused, achievable solution for automated bookkeeping that solves a real pain point
for small businesses and sole proprietors. By limiting scope to directory monitoring, AI extraction, and statement
generation, the project remains manageable for a single developer while delivering significant value.

The tool eliminates manual data entry, ensures tax-compliant categorization, and provides professional financial
statements—all without subscription fees or complex setup.

---

**Document Information:**

- **Product Name**: Agentic Bookkeeper
- **Version**: 1.0 (Product Description - Revised Scope)
- **Author**: Stephen Bogner, P.Eng.
- **LLM**: Claude Sonnet 4.5
- **Date Created**: 2025-10-24
