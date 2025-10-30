# Contributing to Agentic Bookkeeper

**Thank you for your interest in contributing to Agentic Bookkeeper!**

This document provides guidelines for contributing to the project. We welcome contributions from the community and appreciate your help in making this project better.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing Requirements](#testing-requirements)
6. [Documentation Requirements](#documentation-requirements)
7. [Pull Request Process](#pull-request-process)
8. [Issue Reporting](#issue-reporting)
9. [Community Guidelines](#community-guidelines)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior

- Be respectful and constructive in all interactions
- Welcome newcomers and help them get started
- Focus on what is best for the project and community
- Accept constructive criticism gracefully
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting, or derogatory remarks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct that could reasonably be considered inappropriate

### Reporting

If you experience or witness unacceptable behavior, please report it to the project maintainers at [contact information].

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.8 or higher
- Git for version control
- A GitHub account
- Familiarity with Python development

### Setting Up Development Environment

1. **Fork the Repository**

   Click the "Fork" button on GitHub to create your own copy of the repository.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/YOUR-USERNAME/agentic_bookkeeper.git
   cd agentic_bookkeeper
   ```

3. **Set Up Upstream Remote**

   ```bash
   git remote add upstream https://github.com/ORIGINAL-OWNER/agentic_bookkeeper.git
   ```

4. **Create Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

6. **Run Tests to Verify Setup**

   ```bash
   pytest
   ```

   All tests should pass before you start making changes.

---

## Development Workflow

### Branch Strategy

We use a feature branch workflow:

1. **Main Branch** (`main`): Stable, production-ready code
2. **Feature Branches**: Individual features or bug fixes

### Creating a Feature Branch

1. **Update Your Main Branch**

   ```bash
   git checkout main
   git pull upstream main
   ```

2. **Create Feature Branch**

   Use descriptive branch names:
   - `feature/add-llm-provider`
   - `bugfix/fix-csv-export`
   - `docs/update-api-reference`
   - `test/add-integration-tests`

   ```bash
   git checkout -b feature/your-feature-name
   ```

### Making Changes

1. **Write Code**

   Follow the [Coding Standards](#coding-standards) below.

2. **Write Tests**

   All new code must include tests. See [Testing Requirements](#testing-requirements).

3. **Update Documentation**

   Update relevant documentation for your changes.

4. **Commit Your Changes**

   Write clear, descriptive commit messages:

   ```bash
   git add .
   git commit -m "feat: Add support for new LLM provider

   - Implement CustomProvider class
   - Add tests for CustomProvider
   - Update documentation with usage examples"
   ```

   **Commit Message Format**:
   ```
   <type>: <subject>

   <body>

   <footer>
   ```

   **Types**:
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation changes
   - `test`: Adding or updating tests
   - `refactor`: Code refactoring
   - `style`: Code style changes (formatting)
   - `perf`: Performance improvements
   - `chore`: Build process or auxiliary tool changes

5. **Push to Your Fork**

   ```bash
   git push origin feature/your-feature-name
   ```

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** style guidelines with the following tools:

#### 1. Code Formatting (black)

All code must be formatted with black:

```bash
black src/ tests/
```

**Configuration**:
- Line length: 100 characters
- Target Python version: 3.8+

#### 2. Linting (flake8)

All code must pass flake8 linting:

```bash
flake8 src/ tests/
```

**Configuration** (`.flake8`):
```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv
ignore = E203, W503
```

#### 3. Type Checking (mypy)

All code must pass mypy type checking:

```bash
mypy src/
```

**Requirements**:
- Type hints on all function signatures
- No `Any` types unless absolutely necessary
- Use `Optional[T]` for nullable types

### Code Organization

#### File Structure

- **One class per file** (maximum 500 lines)
- **One test file per source file**: `test_module.py` for `module.py`
- **Descriptive file names**: Match class name in snake_case

#### File Header

All Python files must include a header:

```python
"""
Module: <module_name>
Purpose: <brief description>
Author: <your name>
Created: <YYYY-MM-DD>
"""
```

#### Import Organization

Organize imports in this order:

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
# Standard library
import logging
from typing import List, Optional

# Third-party
from PIL import Image
import pandas as pd

# Local
from agentic_bookkeeper.models.transaction import Transaction
from agentic_bookkeeper.core.transaction_manager import TransactionManager
```

### Naming Conventions

- **Classes**: PascalCase (`TransactionManager`, `DocumentProcessor`)
- **Functions/Methods**: snake_case (`process_document`, `get_transaction`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Private methods**: Leading underscore (`_validate_input`, `_parse_response`)

### Docstrings

Use **Google-style docstrings** for all classes and public methods:

```python
def process_document(self, document_path: str, validate: bool = True) -> Optional[Transaction]:
    """
    Process a document and extract transaction data.

    Args:
        document_path: Path to document file (PDF or image)
        validate: Whether to validate the extracted data

    Returns:
        Transaction object or None if extraction fails

    Raises:
        FileNotFoundError: If document doesn't exist
        ValueError: If document format is unsupported

    Example:
        >>> processor = DocumentProcessor(provider, categories)
        >>> transaction = processor.process_document("receipt.pdf")
        >>> print(transaction.vendor)
        'Office Depot'
    """
```

### Input Validation

All public methods must validate inputs:

```python
def create_transaction(self, transaction: Transaction) -> int:
    """Create a new transaction."""
    if not isinstance(transaction, Transaction):
        raise TypeError(f"Expected Transaction, got {type(transaction)}")

    if not transaction.vendor:
        raise ValueError("Vendor cannot be empty")

    if transaction.amount <= 0:
        raise ValueError("Amount must be positive")

    # Process transaction...
```

### Logging

Use the logging module (not print statements):

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed debugging information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Exception with traceback")
```

---

## Testing Requirements

### Test Framework

We use **pytest** for all tests.

### Test Coverage

- **Minimum coverage**: 80% overall
- **Target coverage**: 90%+ for new code
- All new features must include tests

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agentic_bookkeeper --cov-report=html

# Run specific test file
pytest tests/test_module.py

# Run specific test
pytest tests/test_module.py::test_function_name

# Run with verbose output
pytest -v
```

### Test Structure

**Test File Naming**: `test_<module>.py` for `<module>.py`

**Test Class Organization**:

```python
import pytest
from agentic_bookkeeper.core.document_processor import DocumentProcessor

class TestDocumentProcessor:
    """Test suite for DocumentProcessor."""

    @pytest.fixture
    def processor(self):
        """Create DocumentProcessor instance for testing."""
        provider = MockLLMProvider()
        categories = ["Office Supplies", "Travel"]
        return DocumentProcessor(provider, categories)

    def test_process_document_success(self, processor):
        """Test successful document processing."""
        transaction = processor.process_document("test_receipt.pdf")
        assert transaction is not None
        assert transaction.vendor == "Test Vendor"

    def test_process_document_invalid_format(self, processor):
        """Test processing with invalid format raises error."""
        with pytest.raises(ValueError):
            processor.process_document("invalid.txt")

    def test_process_document_file_not_found(self, processor):
        """Test processing nonexistent file returns None."""
        transaction = processor.process_document("nonexistent.pdf")
        assert transaction is None
```

### Test Categories

1. **Unit Tests**: Test individual functions/methods in isolation
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete workflows

### Mocking

Use `pytest-mock` for mocking external dependencies:

```python
def test_document_processing_with_mock_llm(mocker):
    """Test document processing with mocked LLM provider."""
    mock_provider = mocker.Mock()
    mock_provider.extract_transaction.return_value = ExtractionResult(
        success=True,
        transaction_data={"vendor": "Test", "amount": 100.0}
    )

    processor = DocumentProcessor(mock_provider, categories)
    transaction = processor.process_document("test.pdf")

    assert transaction.vendor == "Test"
    mock_provider.extract_transaction.assert_called_once()
```

---

## Documentation Requirements

### Code Documentation

- **All classes**: Comprehensive docstrings
- **All public methods**: Docstrings with Args, Returns, Raises
- **Complex algorithms**: Inline comments explaining logic
- **Type hints**: On all function signatures

### User-Facing Documentation

If your changes affect users, update:

- `docs/USER_GUIDE.md`: User-facing instructions
- `docs/API_REFERENCE.md`: Public API changes
- `docs/ARCHITECTURE.md`: Architectural changes
- `README.md`: Installation or usage changes

### Markdown Style

- Use **markdownlint** to validate markdown files
- Follow consistent heading hierarchy
- Include code examples where relevant
- Use proper formatting for code blocks

```bash
# Validate markdown
markdownlint docs/*.md
```

---

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**

   ```bash
   pytest --cov=agentic_bookkeeper --cov-report=term
   ```

2. **Check code quality**

   ```bash
   black src/ tests/ --check
   flake8 src/ tests/
   mypy src/
   ```

3. **Update documentation**

   Ensure all relevant documentation is updated.

4. **Rebase on latest main**

   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

### Creating Pull Request

1. **Push to Your Fork**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open Pull Request on GitHub**

   - Go to your fork on GitHub
   - Click "Pull Request" button
   - Select base branch: `main`
   - Select compare branch: `feature/your-feature-name`

3. **Write Clear PR Description**

   Use this template:

   ```markdown
   ## Description

   Brief description of what this PR does.

   ## Related Issues

   Closes #123

   ## Changes Made

   - Added X feature
   - Fixed Y bug
   - Updated Z documentation

   ## Testing

   - [ ] Unit tests added/updated
   - [ ] Integration tests added/updated
   - [ ] All tests passing
   - [ ] Code coverage maintained/improved

   ## Documentation

   - [ ] Code documentation updated
   - [ ] User guide updated (if applicable)
   - [ ] API reference updated (if applicable)

   ## Checklist

   - [ ] Code follows project style guidelines
   - [ ] Tests pass locally
   - [ ] No new linter warnings
   - [ ] Type checking passes
   - [ ] Documentation is complete
   ```

### Code Review Process

1. **Maintainer Review**: A project maintainer will review your PR
2. **Automated Checks**: CI/CD pipeline will run tests and checks
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, a maintainer will merge your PR

### After Merge

1. **Update Your Fork**

   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

2. **Delete Feature Branch**

   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

---

## Issue Reporting

### Before Creating an Issue

1. **Search existing issues** to avoid duplicates
2. **Check documentation** to ensure it's not expected behavior
3. **Try latest version** to see if issue is already fixed

### Bug Reports

Use the bug report template:

```markdown
## Bug Description

Clear description of the bug.

## Steps to Reproduce

1. Step one
2. Step two
3. Step three

## Expected Behavior

What should happen.

## Actual Behavior

What actually happens.

## Environment

- OS: [e.g., Windows 11, Ubuntu 22.04]
- Python version: [e.g., 3.10.5]
- Package version: [e.g., 0.1.0]

## Additional Context

Any other relevant information, error messages, screenshots, etc.
```

### Feature Requests

Use the feature request template:

```markdown
## Feature Description

Clear description of the proposed feature.

## Use Case

Explain the problem this feature would solve.

## Proposed Solution

How you think this feature should work.

## Alternatives Considered

Other solutions you've considered.

## Additional Context

Any other relevant information or examples.
```

---

## Community Guidelines

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Requests**: Code contributions

### Response Time

- Maintainers will try to respond to issues within 48 hours
- Pull requests will be reviewed within one week
- Complex contributions may take longer

### Getting Help

If you need help:

1. Check the [User Guide](USER_GUIDE.md)
2. Check the [API Reference](API_REFERENCE.md)
3. Search existing GitHub issues
4. Create a new issue with your question

### Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file (if created)
- Release notes for their contributions
- GitHub contributor stats

---

## Development Tips

### Running Specific Tests

```bash
# Run only unit tests
pytest tests/ -k "not integration and not performance"

# Run only integration tests
pytest tests/ -k "integration"

# Run only performance tests
pytest tests/ -k "performance"
```

### Debugging Tests

```bash
# Run with print statements visible
pytest -s

# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l
```

### Code Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=agentic_bookkeeper --cov-report=html

# Open report in browser
# Linux
xdg-open htmlcov/index.html

# macOS
open htmlcov/index.html

# Windows
start htmlcov/index.html
```

### Pre-Commit Hooks (Optional)

Set up pre-commit hooks to automatically run checks:

```bash
pip install pre-commit
pre-commit install
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        args: [--line-length=100]

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
```

---

## Questions?

If you have questions about contributing, please:

1. Check this guide thoroughly
2. Review existing issues and pull requests
3. Create a GitHub issue with your question

**Thank you for contributing to Agentic Bookkeeper!**

---

**End of Contributing Guide**
