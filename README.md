# Agentic Bookkeeper

> Intelligent bookkeeping automation powered by AI

[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-647%20passing-brightgreen.svg)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen.svg)](#testing)
[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](CHANGELOG.md)

**Agentic Bookkeeper** is an intelligent bookkeeping automation system that leverages
AI and Large Language Models (LLMs) to automate document processing, transaction
management, and financial reporting for small businesses, freelancers, and
self-employed individuals.

---

## Features

### Core Capabilities

- **AI-Powered Document Processing**: Automatically extract transaction data from receipts,
  invoices, and financial documents (PDF and images)
- **Multi-LLM Provider Support**: Choose from OpenAI, Anthropic, XAI, or Google AI providers
- **Tax Jurisdiction Support**: Built-in support for CRA (Canada) and IRS (United States)
  tax codes
- **Modern GUI**: Full-featured PySide6 desktop application with intuitive interface
- **Cash-Basis Tax Reporting** _(New in v0.2.0)_: All reports show pre-tax amounts, tax collected/paid,
  and cash totals for accurate bank reconciliation
- **Tax Summary Report** _(New in v0.2.0)_: Dedicated report for GST/HST filing with net tax position
- **Comprehensive Reporting**: Generate Income Statements, Expense Reports, and Tax Summaries
  with professional formatting
- **Multi-Format Export**: Export all reports to PDF, CSV, or JSON with complete tax information
- **Transaction Management**: Full CRUD operations with advanced filtering and search
- **Document Monitoring**: Automatic processing of new documents from watched directories
- **Secure Configuration**: Encrypted API key storage with proper security practices

### Technical Highlights

- **High Test Coverage**: 647 tests with 92% code coverage
- **Cross-Platform**: Runs on Windows and Linux
- **Performance Optimized**: Document processing <30s, database queries <50ms,
  report generation <5s
- **Security Audited**: Strong security posture with comprehensive audit
  (see [SECURITY_REVIEW.md](docs/developer/SECURITY_REVIEW.md))
- **Well Documented**: Complete user and developer documentation
- **Production Ready**: v0.2.0 with complete tax reporting functionality

### What's New in v0.2.0

- **Cash-Basis Tax Reporting**: All financial reports now include tax breakdown
  - Income/Expense reports show pre-tax, tax, and cash total columns
  - Percentages calculated on pre-tax amounts for accuracy
  - Cash totals match actual bank transactions

- **Tax Summary Report**: New report type for GST/HST filing
  - Lists all taxes collected from customers (output tax)
  - Lists all taxes paid to vendors (input tax credits)
  - Calculates net tax position (payable or refundable)

- **Enhanced Exports**: All export formats updated with tax information
  - PDF exports include color-coded net position and tax columns
  - CSV exports have complete tax breakdown for Excel analysis
  - JSON exports preserve all tax data for integration

See [CHANGELOG.md](CHANGELOG.md) for complete release notes.

---

## Quick Start

### Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package installer)
- **Virtual environment** (recommended)
- **API Key** for at least one LLM provider:
  - OpenAI API key (https://platform.openai.com/)
  - Anthropic API key (https://console.anthropic.com/)
  - XAI API key (https://x.ai/)
  - Google AI API key (https://makersuite.google.com/)

### Installation

#### Option 1: Windows Executable (Recommended for End Users)

**Download and install the pre-built Windows installer:**

1. Download `AgenticBookkeeper-0.2.0-Setup.exe` from the [releases page](https://github.com/StephenBogner/agentic_bookkeeper/releases)
2. Run the installer (requires administrator privileges)
3. Follow the installation wizard
4. Launch from Start Menu: **Agentic Bookkeeper**

**System Requirements:**

- Windows 10 (21H2 or later) or Windows 11
- 64-bit operating system
- 200 MB disk space
- No Python installation required

**Note:** The executable includes all dependencies. No additional software installation needed.

#### Option 2: Install from Source (Windows)

```bash
# Clone the repository
git clone https://github.com/StephenBogner/agentic_bookkeeper.git
cd agentic_bookkeeper

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -e .
pip install -r requirements-dev.txt
```

#### Option 3: Install from Source (Linux)

```bash
# Clone the repository
git clone https://github.com/StephenBogner/agentic_bookkeeper.git
cd agentic_bookkeeper

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .
pip install -r requirements-dev.txt
```

### First-Time Setup

1. **Run the application**:

   **Using the launcher script (recommended):**
   ```bash
   # Linux/Mac
   ./run_bookkeeper.sh

   # Windows
   run_bookkeeper.bat
   ```

   **Or run directly:**
   ```bash
   python src/agentic_bookkeeper/main.py
   ```

2. **Configure API Keys** (Settings → API Keys):
   - Add your LLM provider API key(s)
   - Select your preferred provider

3. **Set Up Directories** (Settings → Directories):
   - Choose document processing directory
   - Choose report output directory

4. **Configure Tax Settings** (Settings → Tax Jurisdiction):
   - Select CRA (Canada) or IRS (United States)
   - Set your currency (CAD or USD)

5. **Start Processing**:
   - Click "Start Monitoring" on the Dashboard
   - Drop documents into your configured directory
   - View processed transactions in the Transactions tab
   - Generate reports in the Reports tab

---

## Usage

### GUI Mode (Recommended)

**Option 1: Using the launcher script (easiest):**
```bash
# Linux/Mac
./run_bookkeeper.sh

# Windows
run_bookkeeper.bat
```

**Option 2: Direct Python:**
```bash
# Run the GUI application
python src/agentic_bookkeeper/main.py

# Or use the console script (if installed)
agentic_bookkeeper
```

See [LAUNCHER_GUIDE.md](LAUNCHER_GUIDE.md) for detailed launcher documentation.

### CLI Mode

```bash
# Process a single document
python cli.py process /path/to/document.pdf

# Process all documents in a directory
python cli.py process /path/to/documents/

# Generate a report
python cli.py report --type income --start-date 2025-01-01 --end-date 2025-12-31 --output report.pdf
```

---

## Screenshots

The application provides an intuitive graphical interface for all bookkeeping tasks:

- **Dashboard**: Monitor document processing and view statistics
- **Transactions**: Manage all financial transactions with filtering and search
- **Reports**: Generate and export professional financial reports
- **Settings**: Configure API keys, directories, and tax preferences

*Screenshots are available in [docs/screenshots/](docs/screenshots/README.md)*

---

## Documentation

**Complete Documentation**: See [docs/README.md](docs/README.md) for full documentation navigation

### 📖 User Documentation

Documentation for end users:

- **[User Guide](docs/user/USER_GUIDE.md)** - Complete guide for end users
- **[Quick Start](docs/user/QUICK_START.md)** - Get started quickly
- **[Environment Setup](docs/user/ENV_SETUP_GUIDE.md)** - Configure API keys and settings
- **[Release Notes](docs/user/RELEASE_NOTES.md)** - Version history and changes

### 🔧 Developer Documentation

Documentation for developers and contributors:

- **[Architecture](docs/developer/ARCHITECTURE.md)** - System architecture and design patterns
- **[API Reference](docs/developer/API_REFERENCE.md)** - Complete API documentation
- **[Development Guide](docs/developer/DEVELOPMENT.md)** - Development setup and workflows
- **[Contributing](docs/developer/CONTRIBUTING.md)** - How to contribute to the project
- **[Build for Windows](docs/developer/BUILD_WINDOWS.md)** - Windows executable creation
- **[Build for Linux](docs/developer/BUILD_LINUX.md)** - Linux package preparation

### 📊 Testing & Quality

- **[UAT Scenarios](docs/developer/UAT_SCENARIOS.md)** - User acceptance test scenarios
- **[UAT Results](docs/developer/UAT_RESULTS.md)** - Testing results and validation
- **[Performance Metrics](docs/developer/PERFORMANCE_METRICS.md)** - Performance benchmarks
- **[Security Review](docs/developer/SECURITY_REVIEW.md)** - Security audit and recommendations
- **[Known Issues](docs/developer/KNOWN_ISSUES.md)** - Known limitations and enhancements

### 📋 Project Management

- **[Project Status](PROJECT_STATUS.md)** - Current development status and progress
- **[Context](CONTEXT.md)** - Project context and architectural decisions

---

## Testing

The project maintains high test coverage with comprehensive test suites:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=agentic_bookkeeper --cov-report=html

# Run specific test categories
pytest src/agentic_bookkeeper/tests/test_gui_*.py        # GUI tests
pytest src/agentic_bookkeeper/tests/test_integration_*.py # Integration tests
pytest src/agentic_bookkeeper/tests/test_performance.py   # Performance tests

# Run with verbose output
pytest -v
```

**Test Statistics:**

- Total Tests: 647 passing (99.2% pass rate)
- Code Coverage: 92%
- Test Categories: Unit, Integration, Performance, GUI
- Performance: All tests complete in <2 minutes

---

## Project Structure

```text
agentic_bookkeeper/
├── src/
│   └── agentic_bookkeeper/
│       ├── main.py               # Application entry point
│       ├── core/                 # Core business logic
│       │   ├── document_processor.py
│       │   ├── document_monitor.py
│       │   ├── transaction_manager.py
│       │   ├── report_generator.py
│       │   └── exporters/        # PDF, CSV, JSON exporters
│       ├── models/               # Data models
│       │   ├── database.py
│       │   └── transaction.py
│       ├── llm/                  # LLM provider integrations
│       │   ├── llm_provider.py
│       │   ├── openai_provider.py
│       │   ├── anthropic_provider.py
│       │   ├── xai_provider.py
│       │   └── google_provider.py
│       ├── gui/                  # PySide6 GUI
│       │   ├── main_window.py
│       │   ├── dashboard_widget.py
│       │   ├── transactions_widget.py
│       │   ├── reports_widget.py
│       │   └── settings_dialog.py
│       ├── utils/                # Utilities
│       │   ├── config.py
│       │   ├── logger.py
│       │   ├── exceptions.py
│       │   └── error_handler.py
│       └── tests/                # Test suite (647 tests)
├── docs/                         # Documentation
│   ├── user/                     # User documentation
│   ├── developer/                # Developer documentation
│   └── screenshots/              # Application screenshots
├── specs/                        # Task specifications
├── samples/                      # Sample documents and config
├── cli.py                        # CLI interface
├── main.py                       # Direct entry point
├── run_bookkeeper.sh             # Linux/Mac launcher script
├── run_bookkeeper.bat            # Windows launcher script
├── install.sh                    # Linux installation script
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── setup.py                      # Package setup
├── PROJECT_STATUS.md             # Project tracking
├── CONTEXT.md                    # Project context
├── LICENSE                       # Proprietary license
├── THIRD_PARTY_LICENSES.md       # Third-party licenses
├── LAUNCHER_GUIDE.md             # Launcher documentation
└── README.md                     # This file
```

---

## Development

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest -v

# Format code (PEP 8, 100 char line length)
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

### Code Quality Standards

- **Style Guide**: PEP 8 compliance
- **Formatter**: black (100 character line length)
- **Linter**: flake8
- **Type Checker**: mypy
- **Test Coverage**: Minimum 80% required
- **Documentation**: Google-style docstrings required

See [CONTRIBUTING.md](docs/developer/CONTRIBUTING.md) for complete development guidelines.

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](docs/developer/CONTRIBUTING.md) for:

- Code of conduct
- Development workflow
- Coding standards
- Testing requirements
- Pull request process
- Issue reporting guidelines

---

## License

This software is proprietary and confidential. Unauthorized copying, distribution,
or use of this software, via any medium, is strictly prohibited without written
permission from the author.

See [LICENSE](LICENSE) for complete license terms.

### Third-Party Licenses

This project uses several open-source libraries. See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for details on
third-party dependencies and their licenses.

---

## Support

### Getting Help

- **User Guide**: See [docs/user/USER_GUIDE.md](docs/user/USER_GUIDE.md)
- **Troubleshooting**: See [docs/user/USER_GUIDE.md#troubleshooting](docs/user/USER_GUIDE.md#troubleshooting)
- **Known Issues**: See [docs/developer/KNOWN_ISSUES.md](docs/developer/KNOWN_ISSUES.md)

### Reporting Issues

Found a bug or have a feature request? Please check:

1. [Known Issues](docs/developer/KNOWN_ISSUES.md) - Check if already documented
2. [GitHub Issues](https://github.com/StephenBogner/agentic_bookkeeper/issues) - Search existing issues
3. Create a new issue with detailed information (see [CONTRIBUTING.md](docs/developer/CONTRIBUTING.md))

---

## Author

**Stephen Bogner, P.Eng.**

- Professional Engineer (P.Eng.)
- Software Developer & Systems Architect

---

## Acknowledgments

This project was developed using:

- **AI Assistant**: Claude (Anthropic) for code generation and testing
- **LLM Providers**: OpenAI, Anthropic, XAI, Google AI
- **GUI Framework**: PySide6 (Qt for Python)
- **Testing Framework**: pytest
- **Documentation**: Markdown with markdownlint validation

---

## Project Status

**Current Version**: 0.1.0 (Production Ready)

**Development Status**: ✅ **ALL PHASES COMPLETE**

- Phase 1 (Core Functionality): ✅ Complete (20/20 tasks)
- Phase 2 (GUI Development): ✅ Complete (11/11 tasks)
- Phase 3 (Reporting Engine): ✅ Complete (8/8 tasks)
- Phase 4 (Testing & Documentation): ✅ Complete (10/10 tasks)
- Phase 5 (Refinement & Distribution): ✅ Complete (9/9 tasks)

**Project Completion**: 58/58 tasks (100%)

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed progress tracking.

---

## Roadmap

### ✅ Completed Development (All Phases)

All 58 planned tasks across 5 phases and 10 sprints have been successfully completed:

**Phase 1 - Core Functionality** (20 tasks)

- ✅ Project setup and database foundation
- ✅ LLM integration and document processing
- ✅ Integration testing and validation

**Phase 2 - GUI Development** (11 tasks)

- ✅ PySide6 main window and dashboard
- ✅ Transaction management UI with full CRUD operations

**Phase 3 - Reporting Engine** (8 tasks)

- ✅ Report generator core and templates
- ✅ PDF, CSV, and JSON export capabilities

**Phase 4 - Testing & Documentation** (10 tasks)

- ✅ Comprehensive test suite (553 tests, 91% coverage)
- ✅ Complete user and developer documentation
- ✅ Security audit and performance testing

**Phase 5 - Refinement & Distribution** (9 tasks)

- ✅ Performance optimization and error handling
- ✅ UI/UX polish and logging enhancements
- ✅ Windows executable and Linux packages
- ✅ GitHub repository setup and release v0.1.0

### Future Enhancements (Post-v1.0)

Potential features for future releases:

- Bank statement import and reconciliation
- Multi-year comparison reports
- Budget tracking and alerts
- Export to QuickBooks/Xero formats
- Mobile app for receipt capture
- Multi-currency support
- Multi-user/multi-company support

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed completion history.

---

Built with AI-Assisted Development | Tested with 92% Coverage | Ready for Production Use
