# Task Specification: T-016

**Task Name:** Unit Tests for LLM & Document Processing
**Task ID:** T-016
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 2: LLM Integration & Document Processing
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 6 hours
**Dependencies:** T-008, T-009, T-012, T-013, T-014

---

## OBJECTIVE

Create comprehensive unit tests for LLM providers, document processor, transaction manager, and document monitor to achieve >80% code coverage.

---

## REQUIREMENTS

### Functional Requirements

- Test all LLM providers with mock API responses
- Test document processor with sample PDFs and images
- Test transaction manager CRUD operations
- Test transaction manager filtering and search
- Test document monitor file detection and processing
- Create realistic mock data and fixtures
- Test error handling and edge cases
- Achieve >80% code coverage for all modules

### Non-Functional Requirements

- Tests must run in <30 seconds total
- Tests must be deterministic (no flaky tests)
- Mock external dependencies (APIs, file system)
- Tests should be isolated (no shared state)

---

## ACCEPTANCE CRITERIA

- [ ] All tests pass consistently
- [ ] Coverage >80% for llm module
- [ ] Coverage >80% for core module
- [ ] Mock API responses for all LLM providers
- [ ] Sample documents created for testing
- [ ] Error scenarios tested
- [ ] Edge cases covered
- [ ] Test fixtures organized and reusable
- [ ] Tests documented with clear descriptions

---

## EXPECTED DELIVERABLES

**Files to Create:**

- `src/agentic_bookkeeper/tests/test_llm_providers.py`
- `src/agentic_bookkeeper/tests/test_document_processor.py`
- `src/agentic_bookkeeper/tests/test_transaction_manager.py`
- `src/agentic_bookkeeper/tests/test_document_monitor.py`
- `src/agentic_bookkeeper/tests/fixtures/sample_receipt.pdf`
- `src/agentic_bookkeeper/tests/fixtures/sample_invoice.jpg`

**Files to Modify:**

- `src/agentic_bookkeeper/tests/conftest.py` (add fixtures)

---

## VALIDATION COMMANDS

```bash
# Run all tests
pytest src/agentic_bookkeeper/tests/ -v

# Run specific test modules
pytest src/agentic_bookkeeper/tests/test_llm_providers.py -v
pytest src/agentic_bookkeeper/tests/test_document_processor.py -v
pytest src/agentic_bookkeeper/tests/test_transaction_manager.py -v
pytest src/agentic_bookkeeper/tests/test_document_monitor.py -v

# Check coverage
pytest --cov=src/agentic_bookkeeper/llm --cov=src/agentic_bookkeeper/core \
  --cov-report=html --cov-report=term

# Run with verbose output
pytest -vv -s
```

---

## IMPLEMENTATION NOTES

### Test Structure for LLM Providers

```python
# test_llm_providers.py
import pytest
from unittest.mock import Mock, patch
from src.agentic_bookkeeper.llm.openai_provider import OpenAIProvider

class TestOpenAIProvider:
    """Test OpenAI provider."""

    @pytest.fixture
    def provider(self):
        return OpenAIProvider(api_key='test_key')

    @pytest.fixture
    def mock_response(self):
        return {
            "date": "2025-01-15",
            "type": "expense",
            "category": "Office Supplies",
            "vendor_customer": "Staples",
            "description": "Printer paper",
            "amount": 45.99,
            "tax_amount": 5.99
        }

    def test_extract_transaction_success(self, provider, mock_response):
        """Test successful transaction extraction."""
        with patch('openai.ChatCompletion.create') as mock_api:
            mock_api.return_value.choices[0].message.content = \
                json.dumps(mock_response)

            result = provider.extract_transaction('test_image.jpg')

            assert result['date'] == '2025-01-15'
            assert result['amount'] == 45.99

    def test_extract_transaction_api_error(self, provider):
        """Test API error handling."""
        with patch('openai.ChatCompletion.create') as mock_api:
            mock_api.side_effect = Exception('API Error')

            with pytest.raises(Exception):
                provider.extract_transaction('test_image.jpg')

    def test_validate_response(self, provider, mock_response):
        """Test response validation."""
        assert provider.validate_response(mock_response) is True

        invalid = mock_response.copy()
        del invalid['date']
        assert provider.validate_response(invalid) is False
```

### Test Fixtures in conftest.py

```python
# conftest.py
import pytest
from pathlib import Path
from src.agentic_bookkeeper.models.database import Database
from src.agentic_bookkeeper.models.transaction import Transaction

@pytest.fixture
def test_db(tmp_path):
    """Create temporary test database."""
    db_path = tmp_path / 'test.db'
    db = Database(str(db_path))
    db.initialize_schema()
    yield db
    db.close()

@pytest.fixture
def sample_transaction():
    """Create sample transaction."""
    return Transaction(
        date='2025-01-15',
        type='expense',
        category='Office Supplies',
        vendor_customer='Staples',
        description='Printer paper',
        amount=45.99,
        tax_amount=5.99
    )

@pytest.fixture
def sample_receipt_pdf(tmp_path):
    """Create sample receipt PDF."""
    # Create minimal PDF for testing
    pdf_path = tmp_path / 'receipt.pdf'
    # Generate test PDF
    return pdf_path

@pytest.fixture
def sample_receipt_image(tmp_path):
    """Create sample receipt image."""
    from PIL import Image
    img = Image.new('RGB', (800, 600), color='white')
    img_path = tmp_path / 'receipt.jpg'
    img.save(img_path)
    return img_path
```

### Test Coverage Goals

- **LLM Providers:** >80% coverage
  - API calls with mock responses
  - Error handling (network, rate limit, invalid response)
  - Response validation
  - Retry logic

- **Document Processor:** >80% coverage
  - PDF processing
  - Image processing
  - Type detection
  - Data validation
  - Error scenarios

- **Transaction Manager:** >80% coverage
  - All CRUD operations
  - Filtering and search
  - Duplicate detection
  - Statistics calculations
  - Error handling

- **Document Monitor:** >80% coverage
  - File detection
  - File processing
  - Archiving
  - Start/stop operations
  - Error handling

### Mock Data Examples

```python
# Sample extraction responses
MOCK_RECEIPT_RESPONSE = {
    "date": "2025-01-15",
    "type": "expense",
    "category": "Office Supplies",
    "vendor_customer": "Staples",
    "description": "Printer paper, pens",
    "amount": 45.99,
    "tax_amount": 5.99
}

MOCK_INVOICE_RESPONSE = {
    "date": "2025-01-20",
    "type": "income",
    "category": "Consulting Services",
    "vendor_customer": "Acme Corp",
    "description": "Website development",
    "amount": 2500.00,
    "tax_amount": 325.00
}
```

---

## NOTES

- Use pytest for all testing
- Mock external APIs to avoid actual API calls
- Use tmp_path fixture for file operations
- pytest-cov for coverage reporting
- pytest-mock for easier mocking
- Create minimal sample documents (small file sizes)
- Test both success and failure paths
- Test edge cases (empty files, corrupted data)
- Use parametrize for testing multiple scenarios
- Keep tests fast and isolated

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-017 - End-to-End Integration Testing
