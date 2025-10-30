# Task Specification: T-011

**Task Name:** Google Provider Implementation
**Task ID:** T-011
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 2: LLM Integration & Document Processing
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Medium
**Estimated Effort:** 4 hours
**Dependencies:** T-007

---

## OBJECTIVE

Implement the Google LLM provider class that extracts transaction data from financial documents using Gemini Vision API.

---

## REQUIREMENTS

### Functional Requirements

- Implement LLMProvider abstract base class
- Authenticate with Google AI API using API key
- Create document extraction prompt optimized for receipts/invoices
- Call Gemini Vision API with image data
- Parse and validate JSON responses
- Handle API errors gracefully with retries
- Track API usage
- Support rate limiting

### Non-Functional Requirements

- API calls must complete within 30 seconds
- Retry with exponential backoff on transient failures
- Log all API interactions for debugging
- Mask API keys in logs

---

## ACCEPTANCE CRITERIA

- [ ] Google provider class implements LLMProvider interface
- [ ] Successfully extracts data from sample receipts/invoices
- [ ] Handles API errors with appropriate exceptions
- [ ] Retries on transient failures (network, rate limit)
- [ ] Validates response format (JSON with required fields)
- [ ] Tracks API usage
- [ ] API keys never logged in plaintext
- [ ] Unit tests achieve >80% coverage

---

## EXPECTED DELIVERABLES

**Files to Create:**

- `src/agentic_bookkeeper/llm/google_provider.py`

**Files to Modify:**

- `src/agentic_bookkeeper/llm/__init__.py` (export provider)

---

## VALIDATION COMMANDS

```bash
# Test Google provider with mock
pytest src/agentic_bookkeeper/tests/test_llm_providers.py::TestGoogleProvider -v

# Test with real API (requires API key)
python -c "
from src.agentic_bookkeeper.llm.google_provider import GoogleProvider
provider = GoogleProvider(api_key='YOUR_KEY')
result = provider.extract_transaction('test_receipt.jpg')
print(result)
"
```

---

## IMPLEMENTATION NOTES

### Key Implementation Details

1. **API Authentication:** Use Google AI Python SDK
2. **Model:** Use gemini-pro-vision or latest Gemini model
3. **Error Handling:** Catch Google API exceptions
4. **Retry Logic:** Exponential backoff with 3 retries
5. **Response Validation:** Check for required fields, validate types
6. **Usage Tracking:** Log API calls and token usage

### Extraction Prompt

```python
EXTRACTION_PROMPT = """
Extract transaction data from this receipt/invoice image.

Return JSON object with fields:
- date (YYYY-MM-DD)
- type ("income" or "expense")
- category (business category)
- vendor_customer (name)
- description (brief)
- amount (number)
- tax_amount (number)

Return only valid JSON, no other text.
"""
```

---

## NOTES

- Gemini API offers competitive pricing
- Strong vision capabilities for document understanding
- Rate limits: varies by account (60 requests/minute typical)
- Response time: 3-8 seconds typical
- Free tier available for development/testing
- Gemini excels at multilingual document processing

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-012 - Document Processor Implementation
