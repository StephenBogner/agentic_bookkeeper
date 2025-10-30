# Task Specification: T-012

**Task Name:** Document Processor Implementation
**Task ID:** T-012
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 2: LLM Integration & Document Processing
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 5 hours
**Dependencies:** T-008, T-009

---

## OBJECTIVE

Implement the document processor that detects document types, preprocesses files, integrates with LLM providers, and validates extracted transaction data.

---

## REQUIREMENTS

### Functional Requirements

- Detect document type (PDF, JPG, PNG, JPEG)
- Extract text from PDFs using pypdf
- Preprocess images with Pillow (resize, enhance)
- Select and instantiate appropriate LLM provider
- Call LLM provider to extract transaction data
- Validate extracted data against Transaction model
- Create user review data structure
- Handle extraction errors gracefully
- Support fallback to OCR if LLM fails

### Non-Functional Requirements

- Document processing must complete within 30 seconds
- Support images up to 20MB
- Support multi-page PDFs
- Maintain document quality during preprocessing

---

## ACCEPTANCE CRITERIA

- [ ] Processes PDF documents successfully
- [ ] Processes image documents (JPG, PNG) successfully
- [ ] Detects document type automatically from extension
- [ ] Switches between LLM providers based on configuration
- [ ] Validates extracted transaction data
- [ ] Returns structured review data for user confirmation
- [ ] Handles errors with clear error messages
- [ ] Logs all processing steps
- [ ] Unit tests achieve >80% coverage

---

## EXPECTED DELIVERABLES

**Files to Create:**

- `src/agentic_bookkeeper/core/document_processor.py`

**Files to Modify:**

- `src/agentic_bookkeeper/core/__init__.py` (export processor)

---

## VALIDATION COMMANDS

```bash
# Test document processor
pytest src/agentic_bookkeeper/tests/test_document_processor.py -v

# Manual test with sample document
python -c "
from src.agentic_bookkeeper.core.document_processor import DocumentProcessor
processor = DocumentProcessor(llm_provider='anthropic')
result = processor.process_document('test_receipt.pdf')
print(result)
"
```

---

## IMPLEMENTATION NOTES

### Document Processor Class Structure

```python
class DocumentProcessor:
    """Process financial documents and extract transaction data."""

    def __init__(self, llm_provider: str = 'anthropic'):
        """Initialize processor with LLM provider."""
        self.llm_provider_name = llm_provider
        self.llm_provider = self._create_provider(llm_provider)

    def process_document(self, file_path: str) -> dict:
        """Process document and extract transaction data."""
        # 1. Detect document type
        # 2. Preprocess document
        # 3. Extract data via LLM
        # 4. Validate extracted data
        # 5. Return review structure
        pass

    def _detect_type(self, file_path: str) -> str:
        """Detect document type from extension."""
        pass

    def _preprocess_pdf(self, file_path: str) -> bytes:
        """Extract text/images from PDF."""
        pass

    def _preprocess_image(self, file_path: str) -> bytes:
        """Preprocess image for LLM."""
        pass

    def _validate_extraction(self, data: dict) -> bool:
        """Validate extracted data."""
        pass
```

### Review Data Structure

```python
{
    "success": True,
    "document_path": "/path/to/document.pdf",
    "extracted_data": {
        "date": "2025-01-15",
        "type": "expense",
        "category": "Office Supplies",
        "vendor_customer": "Staples",
        "description": "Printer paper",
        "amount": 45.99,
        "tax_amount": 5.99
    },
    "confidence": 0.95,
    "requires_review": False,
    "errors": []
}
```

### Image Preprocessing

- Resize if larger than 4096x4096
- Convert to RGB if necessary
- Enhance contrast for poor quality scans
- Compress to reduce API payload size

---

## NOTES

- pypdf replaces deprecated PyPDF2
- Pillow handles all common image formats
- Consider EXIF orientation for rotated images
- Multi-page PDFs: process first page or all pages?
- OCR fallback: pytesseract integration (future enhancement)
- Document quality affects extraction accuracy
- Some receipts may require manual review

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-013 - Transaction Manager Implementation
