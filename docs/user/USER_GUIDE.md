# Agentic Bookkeeper User Guide

**Version:** 0.1.0
**Last Updated:** 2025-10-29
**Author:** Stephen Bogner, P.Eng.

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [First-Time Setup](#first-time-setup)
5. [Daily Operations](#daily-operations)
6. [Features Guide](#features-guide)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)
9. [Appendix](#appendix)

---

## Introduction

### What is Agentic Bookkeeper?

Agentic Bookkeeper is an intelligent bookkeeping automation system that uses AI/LLM technology to
automatically process receipts, invoices, and other financial documents. The application extracts
transaction information from your documents and maintains organized financial records suitable for
tax filing and business management.

### Key Features

- **Automated Document Processing**: Upload PDF receipts or images, and the AI extracts date,
  vendor, amount, and category information
- **Multi-LLM Support**: Choose from OpenAI, Anthropic, XAI, or Google AI providers
- **Tax Jurisdiction Support**: Configured for CRA (Canada) and IRS (United States) tax codes
- **Professional Reports**: Generate income statements and expense reports with tax codes
- **Multiple Export Formats**: Export reports as PDF, CSV, or JSON
- **User-Friendly GUI**: Full-featured PySide6 desktop application
- **Secure**: API keys are encrypted, and sensitive data is protected

### Who Should Use This?

- Small business owners
- Freelancers and independent contractors
- Self-employed individuals
- Anyone needing organized financial records for tax purposes

---

## System Requirements

### Operating System

- **Windows**: Windows 10 or later (64-bit)
- **Linux**: Ubuntu 20.04 LTS or later, or equivalent distribution
- **Note**: macOS is not officially tested but should work with the Linux instructions

### Software Requirements

- **Python**: Version 3.8 or later (3.9+ recommended)
- **Tesseract OCR**: Required for image processing
  - Windows: Download from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt-get install tesseract-ocr`
- **pip**: Python package manager (included with Python 3.4+)

### Hardware Requirements

- **RAM**: Minimum 4GB, recommended 8GB
- **Disk Space**: 500MB for application + space for documents and database
- **Internet**: Required for LLM API calls

### LLM Provider API Keys

You'll need at least one API key from:

- **OpenAI**: [platform.openai.com](https://platform.openai.com)
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com)
- **XAI**: [x.ai](https://x.ai)
- **Google AI**: [ai.google.dev](https://ai.google.dev)

---

## Installation

### Windows Installation

#### Step 1: Install Python

1. Download Python 3.9+ from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation:

   ```cmd
   python --version
   ```

#### Step 2: Install Tesseract OCR

1. Download Tesseract from [UB Mannheim releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer (default location: `C:\Program Files\Tesseract-OCR`)
3. Add Tesseract to your PATH:
   - Right-click "This PC" → Properties → Advanced system settings
   - Click "Environment Variables"
   - Under "System variables", select "Path" → Edit
   - Add: `C:\Program Files\Tesseract-OCR`
4. Verify installation:

   ```cmd
   tesseract --version
   ```

#### Step 3: Install Agentic Bookkeeper

1. Open Command Prompt
2. Create a directory for the application:

   ```cmd
   mkdir C:\AgenticBookkeeper
   cd C:\AgenticBookkeeper
   ```

3. Download or clone the application (or extract from ZIP)
4. Create virtual environment:

   ```cmd
   python -m venv venv
   ```

5. Activate virtual environment:

   ```cmd
   venv\Scripts\activate
   ```

6. Install dependencies:

   ```cmd
   pip install -r requirements.txt
   ```

#### Step 4: Verify Installation

```cmd
python src\agentic_bookkeeper\main.py --version
```

### Linux Installation

#### Step 1: Install Python

Python 3.8+ is usually pre-installed. Verify:

```bash
python3 --version
```

If not installed:

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

#### Step 2: Install Tesseract OCR

```bash
sudo apt-get install tesseract-ocr
tesseract --version
```

#### Step 3: Install System Dependencies

```bash
# For PySide6 GUI
sudo apt-get install libgl1-mesa-glx libegl1-mesa libxkbcommon-x11-0

# For image processing
sudo apt-get install libtiff5 libjpeg8
```

#### Step 4: Install Agentic Bookkeeper

```bash
# Create application directory
mkdir -p ~/agentic_bookkeeper
cd ~/agentic_bookkeeper

# Download or clone the application

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 5: Verify Installation

```bash
python src/agentic_bookkeeper/main.py --version
```

---

## First-Time Setup

### Step 1: Launch the Application

**Windows:**

```cmd
cd C:\AgenticBookkeeper
venv\Scripts\activate
python src\agentic_bookkeeper\main.py
```

**Linux:**

```bash
cd ~/agentic_bookkeeper
source venv/bin/activate
python src/agentic_bookkeeper/main.py
```

### Step 2: First-Run Initialization

On first launch, the application will:

1. Create the default database: `~/.agentic_bookkeeper/bookkeeper.db`
2. Create the configuration file: `~/.agentic_bookkeeper/config.env`
3. Create the watch directory: `~/Documents/BookkeeperWatch`
4. Display the main application window

### Step 3: Configure Settings

**Configure the following settings:**

#### API Keys

Add at least one LLM provider API key:

- **OpenAI API Key**: Your OpenAI API key
- **Anthropic API Key**: Your Anthropic API key
- **XAI API Key**: Your XAI API key
- **Google API Key**: Your Google AI API key

**Security Note**: API keys are encrypted and stored securely in the database.

#### Directories

- **Watch Directory**: Where you'll place documents for processing (default: `~/Documents/BookkeeperWatch`)
- **Database Path**: Location of your transaction database (default: `~/.agentic_bookkeeper/bookkeeper.db`)

#### Preferences

- **Tax Jurisdiction**: Select CRA (Canada) or IRS (United States)
- **Currency**: Select USD or CAD
- **LLM Provider**: Choose your preferred AI provider
- **Auto-start Monitoring**: Whether to start document monitoring on launch

**Save your settings** by clicking the **Save Settings** button.

### Step 4: Test Document Processing

1. Copy a sample receipt (PDF or image) to your watch directory
2. Go to the **Dashboard** tab
3. Click **Start Monitoring**
4. Wait for the document to be processed (typically 3-10 seconds)
5. Check the **Transactions** tab to see the extracted transaction

---

## Daily Operations

### Starting the Application

**Windows:**

```cmd
cd C:\AgenticBookkeeper
venv\Scripts\activate
python src\agentic_bookkeeper\main.py
```

**Linux:**

```bash
cd ~/agentic_bookkeeper
source venv/bin/activate
python src/agentic_bookkeeper/main.py
```

**Tip**: Create a desktop shortcut or shell script for quick access.

### Processing Documents

#### Automatic Processing (Recommended)

1. Click the **Dashboard** tab
2. Click **Start Monitoring** button
3. Place receipts/invoices in your watch directory
4. The application automatically processes new documents
5. Transactions appear in the **Transactions** tab

**Supported Formats:**

- PDF files (`.pdf`)
- Image files (`.jpg`, `.jpeg`, `.png`, `.tiff`, `.bmp`)

**Processing Time:** 3-10 seconds per document, depending on:

- Document complexity
- Selected LLM provider (XAI is fastest at ~1.8s)
- Internet connection speed

#### Manual Transaction Entry

If you prefer to enter transactions manually:

1. Go to **Transactions** tab
2. Click **Add Transaction** button
3. Fill in the form:
   - **Date**: Transaction date
   - **Type**: Income or Expense
   - **Vendor**: Business name
   - **Amount**: Dollar amount (numbers only)
   - **Category**: Select from dropdown
   - **Description**: Optional notes
4. Click **Save**

### Managing Transactions

#### Viewing Transactions

The **Transactions** tab displays all transactions in a table:

- **Color Coding**:
  - Green background: Income transactions
  - Red background: Expense transactions
- **Columns**: Date, Type, Vendor, Amount, Category, Description

#### Filtering Transactions

Use the filter controls at the top:

1. **Type Filter**: All, Income, or Expense
2. **Category Filter**: Select specific category or "All"
3. **Date Range**: From date and To date
4. **Search**: Text search across vendor and description
5. Click **Apply Filters**

#### Editing Transactions

1. Select a transaction in the table
2. Click **Edit Selected** button
3. Modify the fields
4. Click **Save**

**Note**: You can correct the AI's categorization if needed.

#### Deleting Transactions

1. Select a transaction in the table
2. Click **Delete Selected** button
3. Confirm deletion in the dialog

### Generating Reports

#### Step 1: Select Report Type

1. Go to **Reports** tab
2. Choose report type:
   - **Income Statement**: Complete income/expense summary with net income
   - **Expense Report**: Detailed expense breakdown by category with tax codes

#### Step 2: Select Date Range

Choose a preset or custom date range:

- **This Month**: Current month to date
- **Last Month**: Previous complete month
- **This Quarter**: Current quarter (Q1-Q4)
- **Last Quarter**: Previous complete quarter
- **This Year**: Current year to date
- **Last Year**: Previous complete year
- **Custom**: Select specific from/to dates

#### Step 3: Preview Report

Click **Preview** to see the report in the text area. Review:

- Date range
- Transaction counts
- Totals and percentages
- Category breakdowns

#### Step 4: Export Report

1. Select export format: **PDF**, **CSV**, or **JSON**
2. Click **Export** button
3. Choose save location in file dialog
4. Wait for generation (typically 1-2 seconds)
5. Confirmation dialog appears when complete

**Export Formats:**

- **PDF**: Professional report suitable for printing and tax filing
- **CSV**: Excel-compatible spreadsheet for further analysis
- **JSON**: Structured data for integration with other tools

### Reviewing Processed Documents

To review how a document was processed:

1. Go to **Transactions** tab
2. Select a transaction that was auto-processed
3. Click **Edit Selected**
4. Click **View Source Document** (if available)
5. The Document Review Dialog shows:
   - Original document image
   - Extracted transaction details
   - AI confidence/notes

---

## Features Guide

### Document Processing

#### How It Works

1. Application monitors the watch directory
2. When a new file appears, it's queued for processing
3. The selected LLM provider analyzes the document
4. AI extracts: date, vendor, amount, category
5. Transaction is saved to the database
6. Original document is moved to processed folder

#### Accuracy

Based on testing:

- **Date**: 100% accuracy
- **Vendor**: 100% accuracy
- **Amount**: 100% accuracy
- **Category**: 80% accuracy (AI's best guess, review recommended)

**Best Practice**: Review auto-categorized transactions periodically.

#### Supported Document Types

- Receipts (retail, restaurant, gas, etc.)
- Invoices (vendor, service provider)
- Bank statements (individual transactions)
- Utility bills
- Credit card statements

### Transaction Management

#### Categories

**Expense Categories** (with IRS Schedule C codes):

- Advertising (Line 8)
- Car and Truck Expenses (Line 9)
- Depreciation (Line 13)
- Insurance (Line 15)
- Legal and Professional Services (Line 17)
- Office Expense (Line 18)
- Supplies (Line 22)
- Travel (Line 24a)
- Meals (Line 24b)
- Utilities (Line 25)

**Income Categories**:

- Sales
- Services
- Interest
- Other Income

**Adding Custom Categories**: Contact support (future feature planned).

#### Bulk Operations

**Future Enhancement**: Bulk edit/delete operations planned for next version.

### Report Generation

#### Income Statement

Includes:

- **Revenue Section**: All income by category
- **Expenses Section**: All expenses by category
- **Net Income**: Revenue minus expenses
- **Percentages**: Each category as % of total

**Use Case**: Monthly/quarterly financial review, tax filing.

#### Expense Report

Includes:

- **Expense Breakdown**: Grouped by category
- **Tax Codes**: IRS Schedule C or CRA T2125 codes
- **Category Totals**: Sum per category
- **Percentages**: Each category as % of total expenses

**Use Case**: Tax preparation, deduction tracking, expense analysis.

#### Report Customization

**Current Version**: Reports use fixed templates.

**Future Enhancement**: Custom templates planned for future version.

### Settings & Configuration

#### API Key Management

- **Encryption**: All API keys are encrypted using Fernet (AES-256)
- **Storage**: Encrypted keys stored in SQLite database
- **Changing Keys**: Simply enter new key and save
- **Multiple Providers**: Configure all providers, switch easily

#### Directory Configuration

- **Watch Directory**: Where you place documents
- **Processed Directory**: Where processed documents are moved (auto-created inside watch directory)
- **Database Path**: Location of transaction database

**Important**: Paths must exist and be writable.

#### Tax Jurisdiction

Affects:

- Tax codes in expense reports
- Currency symbols
- Report formatting

**Switching Jurisdiction**: Change in settings, affects future reports only.

#### LLM Provider Selection

**Provider Comparison**:

| Provider   | Speed    | Cost    | Accuracy |
|------------|----------|---------|----------|
| XAI        | Fastest  | Low     | High     |
| OpenAI     | Fast     | Medium  | High     |
| Anthropic  | Fast     | Medium  | High     |
| Google AI  | Moderate | Low     | High     |

**Recommendation**: Start with XAI for best performance.

---

## Troubleshooting

### Installation Issues

#### "Python not found"

**Windows:**

- Reinstall Python and check "Add Python to PATH"
- Restart Command Prompt after installation

**Linux:**

- Use `python3` instead of `python`
- Install: `sudo apt-get install python3`

#### "pip not found"

```bash
python -m ensurepip --upgrade
```

#### "Tesseract not found"

**Windows:**

- Verify Tesseract is in PATH
- Restart Command Prompt after adding to PATH
- Try full path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

**Linux:**

```bash
sudo apt-get install tesseract-ocr
```

### Application Errors

#### "Failed to connect to LLM provider"

**Cause**: Invalid API key or network issue

**Solution**:

1. Verify API key is correct in Settings
2. Check internet connection
3. Try a different LLM provider
4. Check provider service status online

#### "Database locked" error

**Cause**: Another instance of the application is running

**Solution**:

1. Close all instances of the application
2. Restart the application
3. If persists, check for zombie processes

#### "Permission denied" on watch directory

**Cause**: Application doesn't have write permissions

**Solution**:

1. Check directory permissions
2. Choose a different directory (Documents folder recommended)
3. Windows: Run as Administrator (not recommended for regular use)

### Document Processing Issues

#### Document not processing

**Check**:

1. File is in the correct watch directory
2. File format is supported (PDF, JPG, PNG)
3. Document monitoring is started (Dashboard tab)
4. Check application logs for errors

#### Wrong category assigned

**Solution**:

1. Edit transaction and change category
2. This is normal; AI makes best guess
3. Common for ambiguous receipts

#### Amount extracted incorrectly

**Rare, but possible causes**:

- Document quality is poor
- Multiple amounts on receipt
- Currency symbol issues

**Solution**:

1. Edit transaction and correct amount
2. For persistent issues, try manual entry

### Performance Issues

#### Slow document processing

**Causes**:

- Slow LLM provider (try switching to XAI)
- Poor internet connection
- Large/complex documents

**Solutions**:

1. Switch to faster LLM provider (Settings)
2. Check internet speed
3. Use higher quality document scans

#### Application freezing

**Solution**:

1. Force quit application
2. Restart application
3. Check available RAM (close other applications)
4. Check database file size (large databases may slow queries)

### GUI Issues

#### Application window not appearing

**Linux specific**:

```bash
export QT_QPA_PLATFORM=xcb
python src/agentic_bookkeeper/main.py
```

#### Blurry text on high-DPI displays

**Windows**:

- Right-click executable → Properties → Compatibility
- Check "Override high DPI scaling behavior"

### Report Generation Issues

#### "No transactions in date range"

**Cause**: Selected date range has no transactions

**Solution**:

1. Expand date range
2. Check Transactions tab to verify data exists
3. Check filters are not too restrictive

#### PDF export fails

**Solution**:

1. Check write permissions on save location
2. Ensure enough disk space
3. Try exporting to different location

---

## FAQ

### General Questions

**Q: Is my financial data secure?**

A: Yes. All API keys are encrypted with AES-256, and the database is stored locally on your computer.
Data is never sent anywhere except to the LLM provider during document processing.

**Q: Can I use this for personal and business finances?**

A: Yes, but we recommend using separate databases (different database paths in Settings) to keep them
separate.

**Q: Does this replace my accountant?**

A: No. This tool helps organize your financial records, but you should still consult with a qualified
accountant for tax advice and filing.

**Q: How much does it cost?**

A: The application is free, but you'll pay for LLM API usage. Cost is typically $0.01-0.05 per
document, depending on the provider.

### Features

**Q: Can I process multiple documents at once?**

A: Yes. Place multiple files in the watch directory, and they'll be processed sequentially.

**Q: Can I import existing transactions from Excel?**

A: Not in the current version. This feature is planned for a future release.

**Q: Can I add custom categories?**

A: Not in the current version. This feature is planned for a future release.

**Q: Can I use multiple currencies?**

A: You can set USD or CAD, but mixing currencies in a single database is not currently supported.

### Technical Questions

**Q: What LLM provider should I use?**

A: XAI is recommended for speed and cost. OpenAI and Anthropic are also excellent choices.

**Q: How much disk space do I need?**

A: The application itself is ~50MB. Your database and processed documents will require additional
space (typically 100-500MB for a year's worth of documents).

**Q: Can I run this on a network drive?**

A: Not recommended. SQLite databases should be on local disk for best performance and
reliability.

**Q: Can multiple users share a database?**

A: No. The application is designed for single-user operation. Database locking will prevent
concurrent access.

### Troubleshooting

**Q: What if the AI extracts wrong information?**

A: Simply edit the transaction and correct the fields. The AI is typically 80-100% accurate, but
mistakes happen.

**Q: Why is document processing slow?**

A: Most time is spent in LLM API calls (1.8-3 seconds per document). Try switching to XAI for
fastest processing.

**Q: Can I use this offline?**

A: No. Document processing requires internet for LLM API calls. However, you can view transactions
and generate reports offline from already-processed data.

---

## Appendix

### Configuration File Reference

The configuration file is located at `~/.agentic_bookkeeper/config.env`:

```bash
# LLM Provider Settings
OPENAI_API_KEY=<your_key_here>
ANTHROPIC_API_KEY=<your_key_here>
XAI_API_KEY=<your_key_here>
GOOGLE_API_KEY=<your_key_here>
LLM_PROVIDER=xai

# Application Settings
TAX_JURISDICTION=IRS
CURRENCY=USD
WATCH_DIRECTORY=/home/user/Documents/BookkeeperWatch
DATABASE_PATH=/home/user/.agentic_bookkeeper/bookkeeper.db
AUTO_START_MONITORING=false
```

**Note**: API keys in this file are encrypted when loaded into the application.

### Keyboard Shortcuts

**Main Window:**

- `Ctrl+Q` (or `Cmd+Q` on Mac): Quit application
- `Ctrl+Tab`: Switch between tabs
- `Ctrl+S`: Save settings (when in Settings tab)

**Transactions Tab:**

- `Ctrl+A`: Add new transaction
- `Ctrl+E`: Edit selected transaction
- `Delete`: Delete selected transaction
- `Ctrl+F`: Focus search box
- `F5`: Refresh transaction list

**Reports Tab:**

- `Ctrl+P`: Preview report
- `Ctrl+E`: Export report
- `Ctrl+R`: Refresh report

### Default Directories

**Windows:**

- Config: `C:\Users\<username>\.agentic_bookkeeper\`
- Database: `C:\Users\<username>\.agentic_bookkeeper\bookkeeper.db`
- Watch: `C:\Users\<username>\Documents\BookkeeperWatch\`
- Processed: `C:\Users\<username>\Documents\BookkeeperWatch\processed\`

**Linux:**

- Config: `~/.agentic_bookkeeper/`
- Database: `~/.agentic_bookkeeper/bookkeeper.db`
- Watch: `~/Documents/BookkeeperWatch/`
- Processed: `~/Documents/BookkeeperWatch/processed/`

### Database Schema

**Transactions Table:**

- `id`: INTEGER PRIMARY KEY
- `date`: TEXT (ISO format: YYYY-MM-DD)
- `type`: TEXT ('income' or 'expense')
- `vendor`: TEXT
- `amount`: REAL
- `category`: TEXT
- `description`: TEXT
- `source_document`: TEXT (path to original file)
- `created_at`: TEXT (timestamp)
- `updated_at`: TEXT (timestamp)

### API Usage Estimates

**Cost per document** (average):

- **XAI**: ~$0.01-0.02
- **OpenAI**: ~$0.02-0.03
- **Anthropic**: ~$0.03-0.05
- **Google AI**: ~$0.01-0.02

**Monthly cost** (processing 100 documents/month):

- **XAI**: ~$1-2/month
- **OpenAI**: ~$2-3/month
- **Anthropic**: ~$3-5/month
- **Google AI**: ~$1-2/month

### File Size Limits

- **PDF files**: Up to 20MB
- **Image files**: Up to 10MB
- **Database**: No hard limit (tested with 10,000+ transactions)

### Performance Benchmarks

Based on testing with 1000 transactions:

- **Document Processing**: 1.8-3s per document (varies by provider)
- **Database Query**: <50ms for typical queries
- **Report Generation**: 1-2s for 1000 transactions
- **PDF Export**: <500ms
- **CSV Export**: <200ms
- **JSON Export**: <100ms
- **Memory Usage**: <200MB typical

### Support & Contact

**Bug Reports:** Create an issue on GitHub (URL to be provided)

**Feature Requests:** Submit via GitHub Issues

**Email:** stephen@example.com (replace with actual email)

**Documentation:** Check docs/ folder for additional guides

### Version History

**Version 0.1.0** (2025-10-29):

- Initial MVP release
- Core document processing
- Transaction management
- Report generation (PDF, CSV, JSON)
- Multi-LLM support (OpenAI, Anthropic, XAI, Google)

### Known Limitations

See `docs/KNOWN_ISSUES.md` for complete list. Key limitations:

1. Single-user operation only
2. No custom categories (yet)
3. No bank reconciliation (yet)
4. No budget tracking (yet)
5. No multi-currency support (yet)

### Roadmap

**Planned for Future Versions:**

- Bank statement import and reconciliation
- Multi-year comparison reports
- Budget tracking and alerts
- Export to QuickBooks/Xero formats
- Mobile app for receipt capture
- Multi-currency support
- Custom categories

---

## Additional Resources

For additional help, please refer to:

- `docs/UAT_SCENARIOS.md` - Usage examples
- `docs/KNOWN_ISSUES.md` - Known issues and workarounds
- `docs/SECURITY_REVIEW.md` - Security details
- `docs/PERFORMANCE_METRICS.md` - Performance details

Thank you for using Agentic Bookkeeper!
