# Task Specification: T-010

**Task Name:** XAI Provider Implementation
**Task ID:** T-010
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 2: LLM Integration & Document Processing
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Medium
**Estimated Effort:** 4 hours
**Dependencies:** T-007

---

## OBJECTIVE

Implement the XAI (X.AI/Grok) LLM provider class that extracts transaction data from financial documents.

---

## REQUIREMENTS

### Functional Requirements
- Implement LLMProvider abstract base class
- Authenticate with XAI API using API key
- Create document extraction prompt optimized for receipts/invoices
- Call XAI API for document processing
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

- [ ] XAI provider class implements LLMProvider interface
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
- `src/agentic_bookkeeper/llm/xai_provider.py`

**Files to Modify:**
- `src/agentic_bookkeeper/llm/__init__.py` (export provider)

---

## VALIDATION COMMANDS

```bash
# Test XAI provider with mock
pytest src/agentic_bookkeeper/tests/test_llm_providers.py::TestXAIProvider -v

# Test with real API (requires API key)
python -c "
from src.agentic_bookkeeper.llm.xai_provider import XAIProvider
provider = XAIProvider(api_key='YOUR_KEY')
result = provider.extract_transaction('test_receipt.jpg')
print(result)
"
```

---

## IMPLEMENTATION NOTES

### Key Implementation Details

1. **API Authentication:** Use XAI API key
2. **API Endpoint:** Check XAI documentation for current endpoints
3. **Error Handling:** Catch HTTP and API exceptions
4. **Retry Logic:** Exponential backoff with 3 retries
5. **Response Validation:** Check for required fields, validate types
6. **Usage Tracking:** Log API calls and responses

### Extraction Prompt

```python
EXTRACTION_PROMPT = """
Extract transaction information from this document.

Return JSON with: date, type (income/expense), category,
vendor_customer, description, amount, tax_amount.

Respond ONLY with valid JSON.
"""
```

---

## NOTES

- XAI/Grok API is newer, documentation may be limited
- Check current vision capability support
- May not support image input - handle gracefully
- Consider this as alternative/experimental provider
- API availability and pricing may vary

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-011 - Google Provider Implementation
