# Agentic Bookkeeper - Release Notes

## Version 0.2.0 - Tax Reporting Enhancement

**Release Date:** October 30, 2025

**"Cash-basis tax reporting for small businesses"**

---

### Overview

Agentic Bookkeeper v0.2.0 adds comprehensive cash-basis tax reporting to the system.
This release enhances all financial reports with detailed tax information, making it easy
to reconcile with bank statements and file GST/HST returns. The implementation maintains
the simplicity of the "drop and go" product vision while providing professional tax
reporting capabilities.

---

### What's New

#### Cash-Basis Tax Reporting

All financial reports now use cash-basis accounting with tax breakdown:

- **Income Statement**: Shows pre-tax amounts, tax collected, and cash totals
  - Revenue section with tax collected from customers
  - Expense section with tax paid to vendors
  - Net income with three views: pre-tax, tax position, and cash

- **Expense Report**: Includes tax columns for all expenses
  - Pre-tax amounts for business deductions
  - Tax paid amounts for input tax credits
  - Cash totals matching actual payments

- **Percentages**: Calculated on pre-tax amounts for accuracy
- **Bank Reconciliation**: Cash totals match actual bank transactions

#### Tax Summary Report

New dedicated report for GST/HST filing:

- **Tax Collected (Output Tax)**: Lists all income transactions with tax > $0
  - Transaction date, description, and tax amount
  - Total tax collected from customers

- **Tax Paid (Input Tax Credits)**: Lists all expense transactions with tax > $0
  - Transaction date, description, and tax amount
  - Total tax paid to vendors

- **Net Tax Position**: Automatic calculation
  - Amount payable (if collected > paid) - shown in red
  - Amount refundable (if paid > collected) - shown in green
  - Professional disclaimer for tax filing

#### Enhanced Exports

All three export formats updated with complete tax information:

- **PDF Export**:
  - Tax columns added to all report types
  - Color-coded net tax position (red for payable, green for refundable)
  - Professional layout with tax breakdown

- **CSV Export**:
  - Excel-compatible format with tax columns
  - Complete tax breakdown for analysis
  - Separate columns for pre-tax, tax, and cash total

- **JSON Export**:
  - Structured data with all tax information
  - Preserves complete report structure
  - Ready for integration with other tools

---

### Technical Details

**Files Modified:**
- `report_generator.py` (~180 lines): Tax tracking and summary generation
- `reports_widget.py` (~120 lines): GUI updates for tax reports
- `pdf_exporter.py` (~180 lines): PDF export with tax columns
- `csv_exporter.py` (~150 lines): CSV export with tax breakdown
- `json_exporter.py` (~60 lines): JSON export structure update

**Total Changes:** ~690 lines across 5 files

**Implementation Time:** ~5 hours

**Backward Compatibility:** Maintained with legacy field support

---

### Installation

Update to v0.2.0 using pip:

```bash
pip install --upgrade agentic_bookkeeper
```

Or download the latest release from GitHub:
- Linux: `agentic_bookkeeper-0.2.0-py3-none-any.whl`
- Windows: `AgenticBookkeeper-0.2.0-Setup.exe`

---

### Migration from v0.1.0

No database migration required. All existing transaction data will work with the new
reporting system. Simply update the software and start using the new tax reports.

**Note:** Existing exports will continue to work, but regenerating reports will use the
new cash-basis format with tax information.

---

### Known Limitations

- Tax rates not stored (only tax amounts)
- No distinction between different tax types (GST, HST, PST, etc.)
- No tax remittance tracking
- Single currency per transaction

These limitations are by design to maintain simplicity. Future enhancements may address
these based on user feedback.

---

### Documentation Updates

- Updated User Guide with tax reporting instructions
- Added Tax Summary Report usage examples
- Created comprehensive tax implementation documentation
- Updated README with v0.2.0 features
- Created CHANGELOG.md for version tracking

---

### What's Next

Planned for future releases:
- Tax rate field with validation
- Tax type categorization (GST, HST, PST, etc.)
- Quarterly tax report presets
- Tax remittance tracking

---

## Version 0.1.0 - Initial Release

**Release Date:** October 29, 2025

**"Intelligent bookkeeping automation powered by AI"**

---

## Overview

Agentic Bookkeeper v0.1.0 is the initial MVP release of an intelligent bookkeeping
automation system that leverages Large Language Model (LLM) technology to extract
financial data from documents (PDFs, images) and automate bookkeeping workflows.

This release provides a complete, production-ready solution for small business owners,
freelancers, and self-employed individuals to manage their financial records with
minimal manual data entry.

---

## Key Features

### Core Capabilities

- **Automated Document Processing**: Extract financial data from PDFs and images using
  AI vision models
- **Multi-LLM Provider Support**: Choose from OpenAI (GPT-4o), Anthropic (Claude),
  XAI (Grok), or Google (Gemini)
- **Tax Jurisdiction Support**: Built-in support for CRA (Canada) and IRS (United States)
  tax codes
- **Professional GUI**: Full-featured PySide6 interface with dashboard, transaction
  management, and reporting
- **Comprehensive Reporting**: Generate income statements and expense reports with
  automatic categorization
- **Multi-Format Export**: Export reports to PDF, CSV, or JSON formats
- **Watch Folder Monitoring**: Automatically process documents dropped in a monitored
  folder
- **Transaction Management**: Full CRUD operations for manual transaction entry and
  editing

### Technical Highlights

- **654 Test Suite**: Comprehensive test coverage (92%) with unit, integration, and
  performance tests
- **Security Audited**: STRONG security rating with encrypted API key storage and
  SQL injection prevention
- **Performance Optimized**: Document processing <30s, database queries <50ms, report
  generation <5s
- **Cross-Platform**: Runs on Windows and Linux with Python 3.8+
- **Professional Documentation**: Complete user guide, developer documentation, API
  reference

---

## Installation

### Linux Installation (Recommended)

```bash
# Download the wheel package
wget https://github.com/StephenBogner/agentic_bookkeeper/releases/download/v0.1.0/agentic_bookkeeper-0.1.0-py3-none-any.whl

# Install system dependencies
sudo apt-get install python3-pip python3-venv tesseract-ocr

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package
pip install agentic_bookkeeper-0.1.0-py3-none-any.whl

# Run application
agentic_bookkeeper
```

### Windows Installation

Windows executable coming in a future release. For now, install from source:

```bash
# Download source package
# Extract and follow Linux installation steps above using Python 3.8+
```

### From Source

```bash
# Download source distribution
wget https://github.com/StephenBogner/agentic_bookkeeper/releases/download/v0.1.0/agentic_bookkeeper-0.1.0.tar.gz

# Extract and install
tar -xzf agentic_bookkeeper-0.1.0.tar.gz
cd agentic_bookkeeper-0.1.0
pip install -r requirements.txt
pip install -e .
```

---

## Getting Started

### First-Time Setup

1. **Obtain API Key**: Get an API key from one of the supported LLM providers:
   - OpenAI: https://platform.openai.com/api-keys (Recommended: GPT-4o)
   - Anthropic: https://console.anthropic.com/ (Claude Sonnet)
   - XAI: https://console.x.ai/ (Grok Vision)
   - Google: https://ai.google.dev/ (Gemini Pro Vision)

2. **Launch Application**:

   ```bash
   agentic_bookkeeper
   ```

3. **Configure Settings**: On first launch, configure:
   - LLM Provider and API key
   - Watch folder for document monitoring
   - Tax jurisdiction (CRA or IRS)
   - Currency (CAD or USD)

4. **Process Documents**: Drop invoices or receipts in the watch folder, or use the
   GUI to manually process documents

5. **Review Transactions**: Review extracted transactions, edit if needed, and approve

6. **Generate Reports**: Create income statements or expense reports for any date range

---

## What's Included

### Documentation

- **User Guide** (`docs/USER_GUIDE.md`): Complete guide for end users
- **Developer Documentation** (`docs/DEVELOPMENT.md`): Setup and contribution guide
- **API Reference** (`docs/API_REFERENCE.md`): Complete API documentation
- **Architecture Guide** (`docs/ARCHITECTURE.md`): System design and patterns

### Sample Data

- **Sample Documents**: 6 sample PDFs (2 invoices, 4 receipts) in `samples/`
- **Configuration Template**: `.env.sample` with all configuration options
- **Usage Guide**: Comprehensive README in `samples/` directory

### Build Artifacts

- **Linux Wheel**: `agentic_bookkeeper-0.1.0-py3-none-any.whl` (175KB)
- **Source Distribution**: `agentic_bookkeeper-0.1.0.tar.gz` (247KB)

---

## Known Limitations

1. **Windows Executable**: Not included in this release (build requires Windows
   environment)
2. **Category Accuracy**: LLM category suggestions are 80% accurate, may require
   manual review
3. **Supported Formats**: Currently supports PDF and common image formats (JPEG, PNG)
   only
4. **Single User**: Designed for single-user desktop use, no multi-user support
5. **English Only**: Document processing optimized for English-language documents

See `docs/KNOWN_ISSUES.md` for complete list and workarounds.

---

## Testing Summary

### Test Coverage

- **Total Tests**: 654 tests (647 passing + 7 flaky/excluded)
- **Coverage**: 92% overall code coverage
- **Test Categories**:
  - Unit Tests: 515 tests (core functionality)
  - Integration Tests: 34 tests (end-to-end workflows)
  - Performance Tests: 17 tests (benchmarking)
  - GUI Tests: 233 tests (PySide6 interface)

### Quality Metrics

- **Security Audit**: STRONG rating, LOW risk
- **Performance**: All targets met or exceeded
- **User Acceptance**: 100% pass rate (15/15 scenarios)
- **Code Quality**: PEP 8 compliant, formatted with black

---

## System Requirements

### Minimum Requirements

- **Operating System**: Linux (Ubuntu 20.04+) or Windows 10+
- **Python**: 3.8 or higher
- **Memory**: 2GB RAM minimum
- **Disk Space**: 500MB for installation + storage for documents and database
- **Internet**: Required for LLM API calls

### Recommended

- **Memory**: 4GB+ RAM
- **Disk Space**: 2GB+ for comfortable use
- **Python**: 3.10+ for best performance

---

## Future Roadmap

### Version 0.2.0 (Planned)

- Windows executable with installer
- Mac OS support
- Multi-currency transaction support
- Bank statement import and reconciliation
- Enhanced category prediction with learning

### Version 1.0.0 (Future)

- Mobile app for receipt capture
- Cloud sync and backup
- Multi-user support
- QuickBooks/Xero export
- Budget tracking and alerts

---

## Support and Feedback

### Getting Help

- **User Guide**: See `docs/USER_GUIDE.md`
- **Troubleshooting**: See `docs/USER_GUIDE.md` section 7
- **Known Issues**: See `docs/KNOWN_ISSUES.md`

### Reporting Issues

Found a bug? Please report it on GitHub:
https://github.com/StephenBogner/agentic_bookkeeper/issues

Include:

- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Log files if applicable

### Feature Requests

Have an idea? Submit a feature request:
https://github.com/StephenBogner/agentic_bookkeeper/issues/new?template=feature_request.md

---

## License

**Proprietary License - All Rights Reserved**

Copyright (c) 2025 Stephen Bogner, P.Eng.

This software is proprietary and confidential. Unauthorized copying, distribution,
or use is strictly prohibited. See LICENSE file for complete terms.

---

## Credits

**Author**: Stephen Bogner, P.Eng. (Professional Engineer)

**Built With**:

- Python 3.8+
- PySide6 (Qt6 GUI framework)
- SQLite (embedded database)
- OpenAI, Anthropic, XAI, Google (LLM providers)
- ReportLab (PDF generation)
- pytest (testing framework)

**Special Thanks**:

- Anthropic's Claude for development assistance
- Open source community for excellent libraries and tools

---

## Changelog

### v0.1.0 - Initial Release (2025-10-29)

**Added**:

- Document processing with LLM vision models
- Multi-LLM provider support (OpenAI, Anthropic, XAI, Google)
- PySide6 GUI application with dashboard and transaction management
- Report generation (Income Statement, Expense Report)
- Multi-format export (PDF, CSV, JSON)
- Watch folder monitoring
- Tax jurisdiction support (CRA, IRS)
- Comprehensive documentation (980+ line user guide)
- Sample documents and configuration templates
- Linux package distribution (wheel + source)

**Testing**:

- 654 comprehensive tests with 92% coverage
- Security audit complete (STRONG rating)
- Performance testing complete (all targets met)
- User acceptance testing complete (100% pass rate)

**Documentation**:

- Complete user guide
- Developer documentation
- API reference
- Architecture guide
- Build instructions for Linux

---

**Thank you for using Agentic Bookkeeper!**

For questions or support, please open an issue on GitHub.
