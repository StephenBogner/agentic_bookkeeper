# Development Guide

**Project:** Agentic Bookkeeper
**Version:** 0.1.0
**Last Updated:** 2025-10-29

---

## Table of Contents

1. [Overview](#overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Building and Running](#building-and-running)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Development Workflows](#development-workflows)
8. [Troubleshooting](#troubleshooting)
9. [Development Tools](#development-tools)

---

## Overview

This guide helps developers set up their development environment and provides information about common development workflows, testing, and debugging for Agentic Bookkeeper.

### Prerequisites

- **Python**: 3.8 or higher
- **pip**: Latest version
- **Git**: For version control
- **Virtual environment**: venv or conda
- **OS**: Windows 10/11 or Linux (Ubuntu 20.04+)

### Recommended Tools

- **IDE**: VS Code, PyCharm, or similar
- **Terminal**: Bash, PowerShell, or Windows Terminal
- **Database Viewer**: DB Browser for SQLite (optional)

---

## Development Environment Setup

### 1. Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/your-org/agentic_bookkeeper.git
cd agentic_bookkeeper
```

### 2. Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Verify activation:**
```bash
which python  # Linux/macOS
where python  # Windows
# Should show path to venv/bin/python
```

### 3. Install Dependencies

**Production Dependencies:**
```bash
pip install -r requirements.txt
```

**Development Dependencies:**
```bash
pip install -r requirements-dev.txt
```

**Verify installation:**
```bash
pip list
```

### 4. Configure Environment Variables

Create `.env` file in project root:

```bash
# .env file
# API Keys (encrypted in config, these are for development)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
XAI_API_KEY=xai-...
GOOGLE_API_KEY=AIza...

# Development Settings
DEBUG=true
LOG_LEVEL=DEBUG

# Database (optional, uses default if not set)
DATABASE_PATH=~/.agentic_bookkeeper/bookkeeper.db
```

**Load environment variables:**
```bash
# Automatically loaded by python-dotenv
```

### 5. Initialize Database

```bash
# Run database initialization
python -c "from src.agentic_bookkeeper.models.database import Database; db = Database('~/.agentic_bookkeeper/bookkeeper.db'); db.connect(); db.initialize_schema()"
```

Or run the application once:
```bash
python -m src.agentic_bookkeeper.main
```

### 6. Verify Setup

```bash
# Run tests to verify everything works
pytest

# Should see output like:
# ============================= test session starts ==============================
# collected 554 items
# ...
# ============================== 554 passed in 79.23s ==============================
```

---

## Project Structure

```
agentic_bookkeeper_module/
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md           # System architecture
│   ├── API_REFERENCE.md          # API documentation
│   ├── CONTRIBUTING.md           # Contribution guidelines
│   ├── DEVELOPMENT.md            # This file
│   ├── USER_GUIDE.md             # User guide
│   ├── SECURITY_REVIEW.md        # Security audit
│   ├── PERFORMANCE_METRICS.md    # Performance benchmarks
│   ├── KNOWN_ISSUES.md           # Known issues and enhancements
│   ├── UAT_SCENARIOS.md          # User acceptance tests
│   └── UAT_RESULTS.md            # UAT execution results
├── specs/                         # Task specifications
│   ├── MASTER_PROJECT_SPEC.md    # Master specification
│   └── PHASE_*/SPRINT_*/         # Task specs by phase/sprint
├── src/
│   └── agentic_bookkeeper/       # Main application package
│       ├── __init__.py
│       ├── main.py               # Application entry point
│       ├── core/                 # Core business logic
│       │   ├── document_processor.py
│       │   ├── document_monitor.py
│       │   ├── transaction_manager.py
│       │   ├── report_generator.py
│       │   └── exporters/        # Export modules
│       │       ├── pdf_exporter.py
│       │       ├── csv_exporter.py
│       │       └── json_exporter.py
│       ├── gui/                  # PySide6 GUI
│       │   ├── main_window.py
│       │   ├── dashboard_widget.py
│       │   ├── transactions_widget.py
│       │   ├── reports_widget.py
│       │   └── settings_dialog.py
│       ├── llm/                  # LLM providers
│       │   ├── llm_provider.py   # Abstract base class
│       │   ├── openai_provider.py
│       │   ├── anthropic_provider.py
│       │   ├── xai_provider.py
│       │   └── google_provider.py
│       ├── models/               # Data models
│       │   ├── database.py
│       │   └── transaction.py
│       ├── utils/                # Utilities
│       │   ├── config.py
│       │   └── logger.py
│       └── tests/                # Test suite
│           ├── conftest.py       # Shared fixtures
│           ├── test_*.py         # Test files
│           └── test_integration_e2e.py
├── resources/                     # Application resources
├── .env                          # Environment variables (not in git)
├── .gitignore                    # Git ignore patterns
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── pyproject.toml                # Project configuration
├── setup.py                      # Package setup
├── PROJECT_STATUS.md             # Project status tracking
├── CONTEXT.md                    # Persistent context
├── CLAUDE.md                     # Project memory
└── README.md                     # Project overview
```

---

## Building and Running

### Running the Application

**GUI Mode (default):**
```bash
# From project root
python -m src.agentic_bookkeeper.main

# Or with Python path
PYTHONPATH=src python -m agentic_bookkeeper.main
```

**CLI Mode (future feature):**
```bash
# Process single document
python -m src.agentic_bookkeeper.main process document.pdf

# Generate report
python -m src.agentic_bookkeeper.main report income-statement --start 2025-01-01 --end 2025-12-31
```

### Running with Debug Logging

```bash
# Set environment variable
export LOG_LEVEL=DEBUG  # Linux/macOS
set LOG_LEVEL=DEBUG     # Windows CMD
$env:LOG_LEVEL="DEBUG"  # Windows PowerShell

# Run application
python -m src.agentic_bookkeeper.main
```

### Building Distribution

**PyInstaller Executable (Windows):**
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --name="Agentic Bookkeeper" \
            --windowed \
            --icon=resources/icon.ico \
            --add-data "resources:resources" \
            src/agentic_bookkeeper/main.py

# Output: dist/Agentic Bookkeeper.exe
```

**Python Package:**
```bash
# Build wheel and source distribution
python -m build

# Output: dist/agentic_bookkeeper-0.1.0-py3-none-any.whl
```

---

## Testing

### Running Tests

**All Tests:**
```bash
pytest
```

**With Coverage:**
```bash
pytest --cov=agentic_bookkeeper --cov-report=html
```

**Specific Test Categories:**
```bash
# Unit tests only
pytest tests/ -k "not integration and not performance"

# Integration tests only
pytest tests/test_integration_e2e.py

# Performance tests only
pytest tests/test_performance.py

# GUI tests only
pytest tests/test_gui_*.py
```

**Specific Test File:**
```bash
pytest tests/test_document_processor.py
```

**Specific Test Function:**
```bash
pytest tests/test_document_processor.py::test_process_pdf
```

**Verbose Output:**
```bash
pytest -v
```

**Show Print Statements:**
```bash
pytest -s
```

### Test Coverage

**View Coverage Report:**
```bash
# Generate HTML report
pytest --cov=agentic_bookkeeper --cov-report=html

# Open in browser
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS
start htmlcov/index.html     # Windows
```

**Coverage Targets:**
- Overall: >80% (currently 91%)
- New code: >90%
- Critical modules: >95%

### Writing Tests

**Test File Structure:**
```python
import pytest
from agentic_bookkeeper.core.module import ClassName

class TestClassName:
    """Test suite for ClassName."""

    @pytest.fixture
    def instance(self):
        """Create test instance."""
        return ClassName()

    def test_method_success(self, instance):
        """Test method with valid input."""
        result = instance.method(valid_input)
        assert result == expected_output

    def test_method_invalid_input(self, instance):
        """Test method with invalid input raises error."""
        with pytest.raises(ValueError):
            instance.method(invalid_input)
```

**Using Fixtures:**
```python
@pytest.fixture
def sample_transaction():
    """Create sample transaction for testing."""
    return Transaction(
        date=date(2025, 10, 29),
        vendor="Test Vendor",
        amount=100.0,
        category="Office Supplies",
        type="expense"
    )

def test_create_transaction(transaction_manager, sample_transaction):
    """Test transaction creation."""
    transaction_id = transaction_manager.create_transaction(sample_transaction)
    assert transaction_id > 0
```

**Mocking:**
```python
def test_with_mock_llm(mocker):
    """Test with mocked LLM provider."""
    mock_provider = mocker.Mock()
    mock_provider.extract_transaction.return_value = ExtractionResult(
        success=True,
        transaction_data={"vendor": "Test", "amount": 100.0}
    )

    processor = DocumentProcessor(mock_provider, categories)
    result = processor.process_document("test.pdf")

    assert result is not None
    mock_provider.extract_transaction.assert_called_once()
```

---

## Debugging

### VS Code Debugging

**Launch Configuration** (`.vscode/launch.json`):
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Main Application",
            "type": "python",
            "request": "launch",
            "module": "agentic_bookkeeper.main",
            "cwd": "${workspaceFolder}/src",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            },
            "console": "integratedTerminal"
        },
        {
            "name": "Python: Current Test",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "${file}",
                "-v"
            ],
            "console": "integratedTerminal"
        }
    ]
}
```

### PyCharm Debugging

1. **Run Configuration**:
   - Script path: `src/agentic_bookkeeper/main.py`
   - Working directory: Project root
   - Environment variables: Add API keys

2. **Test Configuration**:
   - Target: Script path or module
   - Script path: `tests/test_module.py`
   - Module: `pytest`

### Command Line Debugging

**Using pdb:**
```python
import pdb

def problematic_function():
    pdb.set_trace()  # Breakpoint
    # Debug code here
```

**Using pytest debugger:**
```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure
pytest -x --pdb
```

### Logging for Debugging

**Enable Debug Logging:**
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.debug("Debug message with variables: %s", variable)
```

**Log to File:**
```python
logging.basicConfig(
    level=logging.DEBUG,
    filename='debug.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Development Workflows

### Adding a New Feature

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Write Code**
   - Follow coding standards
   - Add type hints
   - Write docstrings

3. **Write Tests**
   ```bash
   # Create test file
   touch tests/test_new_feature.py

   # Write tests
   pytest tests/test_new_feature.py
   ```

4. **Run All Tests**
   ```bash
   pytest
   ```

5. **Check Code Quality**
   ```bash
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

6. **Update Documentation**
   - API reference if public API changed
   - User guide if user-facing
   - Architecture if architectural change

7. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   git push origin feature/new-feature
   ```

8. **Create Pull Request**

### Fixing a Bug

1. **Create Bug Fix Branch**
   ```bash
   git checkout -b bugfix/fix-issue-123
   ```

2. **Write Failing Test**
   ```python
   def test_bug_reproduction():
       """Test that reproduces the bug."""
       # This should fail before fix
       assert buggy_function() == expected_result
   ```

3. **Fix the Bug**
   ```python
   def buggy_function():
       # Fixed implementation
       pass
   ```

4. **Verify Test Passes**
   ```bash
   pytest tests/test_bugfix.py
   ```

5. **Run Full Test Suite**
   ```bash
   pytest
   ```

6. **Commit and Push**
   ```bash
   git add .
   git commit -m "fix: Fix issue with X (closes #123)"
   git push origin bugfix/fix-issue-123
   ```

### Adding a New LLM Provider

1. **Create Provider File**
   ```bash
   touch src/agentic_bookkeeper/llm/newprovider_provider.py
   ```

2. **Implement Provider**
   ```python
   from agentic_bookkeeper.llm.llm_provider import LLMProvider, ExtractionResult

   class NewProvider(LLMProvider):
       @property
       def provider_name(self) -> str:
           return "New Provider"

       def extract_transaction(self, document_path: str, categories: List[str]) -> ExtractionResult:
           # Implementation
           pass

       def _prepare_prompt(self, categories: List[str]) -> str:
           # Implementation
           pass
   ```

3. **Write Tests**
   ```bash
   touch tests/test_newprovider_provider.py
   ```

4. **Add to Settings Dialog**
   ```python
   # In gui/settings_dialog.py
   self.provider_combo.addItem("New Provider")
   ```

5. **Update Documentation**
   - API_REFERENCE.md
   - USER_GUIDE.md

### Database Migrations

**Schema Changes:**
```python
# In models/database.py

def _migrate_to_version_2(self):
    """Migrate database to version 2."""
    with self.get_cursor() as cursor:
        # Add new column
        cursor.execute("ALTER TABLE transactions ADD COLUMN new_field TEXT")

        # Update version
        cursor.execute("PRAGMA user_version = 2")
```

**Testing Migrations:**
```python
def test_migration_from_v1_to_v2():
    """Test database migration."""
    # Create v1 database
    db_v1 = create_v1_database()

    # Run migration
    db_v1._migrate_to_version_2()

    # Verify schema
    assert has_column(db_v1, "transactions", "new_field")
```

---

## Troubleshooting

### Common Issues

#### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'agentic_bookkeeper'`

**Solution**:
```bash
# Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"  # Linux/macOS
set PYTHONPATH=%PYTHONPATH%;%CD%\src          # Windows CMD

# Or run with Python path
PYTHONPATH=src python -m agentic_bookkeeper.main
```

#### Database Locked

**Problem**: `sqlite3.OperationalError: database is locked`

**Solution**:
```bash
# Close all connections to database
# Delete lock files
rm ~/.agentic_bookkeeper/bookkeeper.db-shm
rm ~/.agentic_bookkeeper/bookkeeper.db-wal

# Restart application
```

#### Test Failures

**Problem**: Tests fail with "Connection refused" or "Timeout"

**Solution**:
```bash
# Check if LLM API keys are set
echo $OPENAI_API_KEY

# Use mock providers for tests
pytest tests/ --mock-llm
```

#### GUI Not Launching

**Problem**: GUI doesn't appear on launch

**Solution**:
```bash
# Check Qt platform plugin
export QT_DEBUG_PLUGINS=1  # Linux/macOS
set QT_DEBUG_PLUGINS=1     # Windows

# Install Qt dependencies (Linux)
sudo apt-get install libxcb-cursor0

# Run application
python -m src.agentic_bookkeeper.main
```

### Performance Issues

**Slow Document Processing:**
- Check LLM API response times
- Verify network connection
- Consider using faster models (e.g., XAI Grok)

**Slow Database Queries:**
- Check if indexes exist: `PRAGMA index_list(transactions)`
- Verify WAL mode enabled: `PRAGMA journal_mode`
- Analyze query plan: `EXPLAIN QUERY PLAN SELECT ...`

**High Memory Usage:**
- Check for large result sets (use pagination)
- Verify no circular references (memory leaks)
- Use memory profiler: `pip install memory_profiler`

---

## Development Tools

### Code Quality Tools

**Black (Formatting):**
```bash
# Format code
black src/ tests/

# Check without formatting
black --check src/ tests/

# Configuration: pyproject.toml
```

**Flake8 (Linting):**
```bash
# Lint code
flake8 src/ tests/

# Configuration: .flake8 or setup.cfg
```

**Mypy (Type Checking):**
```bash
# Type check
mypy src/

# Configuration: mypy.ini or pyproject.toml
```

### Database Tools

**DB Browser for SQLite:**
- Download: https://sqlitebrowser.org/
- Open: `~/.agentic_bookkeeper/bookkeeper.db`
- View schema, run queries, inspect data

**SQLite CLI:**
```bash
# Open database
sqlite3 ~/.agentic_bookkeeper/bookkeeper.db

# Run queries
SELECT * FROM transactions;
.schema transactions
.exit
```

### Profiling Tools

**cProfile (CPU Profiling):**
```bash
python -m cProfile -o profile.stats -m agentic_bookkeeper.main

# View results
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"
```

**Memory Profiler:**
```bash
pip install memory_profiler

# Add @profile decorator to function
python -m memory_profiler script.py
```

### Git Hooks

**Pre-Commit Hook** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash
# Run tests before commit

echo "Running tests..."
pytest

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi

echo "Running code quality checks..."
black --check src/ tests/
flake8 src/ tests/

if [ $? -ne 0 ]; then
    echo "Code quality checks failed. Commit aborted."
    exit 1
fi

exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Additional Resources

### Documentation

- [Architecture](ARCHITECTURE.md) - System architecture
- [API Reference](API_REFERENCE.md) - Complete API docs
- [Contributing](CONTRIBUTING.md) - Contribution guidelines
- [User Guide](USER_GUIDE.md) - End-user documentation

### External Resources

- **Python**: https://docs.python.org/3/
- **PySide6**: https://doc.qt.io/qtforpython/
- **pytest**: https://docs.pytest.org/
- **SQLite**: https://www.sqlite.org/docs.html
- **OpenAI API**: https://platform.openai.com/docs/
- **Anthropic API**: https://docs.anthropic.com/

### Community

- **GitHub Issues**: Report bugs, request features
- **GitHub Discussions**: Ask questions, share ideas
- **Pull Requests**: Contribute code

---

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting](#troubleshooting) section
2. Search [GitHub Issues](https://github.com/your-org/agentic_bookkeeper/issues)
3. Check [GitHub Discussions](https://github.com/your-org/agentic_bookkeeper/discussions)
4. Create a new issue with:
   - Problem description
   - Steps to reproduce
   - Environment details
   - Error messages/logs

---

**End of Development Guide**
