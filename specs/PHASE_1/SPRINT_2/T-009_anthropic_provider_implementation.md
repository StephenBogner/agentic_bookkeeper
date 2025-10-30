# Task Specification: T-009

**Task Name:** Anthropic Provider Implementation
**Task ID:** T-009
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 2: LLM Integration & Document Processing
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 4 hours
**Dependencies:** T-007

---

## OBJECTIVE

Implement the Anthropic LLM provider class that extracts transaction data from financial documents using Claude Vision API.

---

## REQUIREMENTS

### Functional Requirements

- Implement LLMProvider abstract base class
- Authenticate with Anthropic API using API key
- Create document extraction prompt optimized for receipts/invoices
- Call Claude Vision API with image data
- Parse and validate JSON responses
- Handle API errors gracefully with retries
- Track API usage and costs
- Support rate limiting

### Non-Functional Requirements

- API calls must complete within 30 seconds
- Retry with exponential backoff on transient failures
- Log all API interactions for debugging
- Mask API keys in logs

---

## ACCEPTANCE CRITERIA

- [ ] Anthropic provider class implements LLMProvider interface
- [ ] Successfully extracts data from sample receipts/invoices
- [ ] Handles API errors with appropriate exceptions
- [ ] Retries on transient failures (network, rate limit)
- [ ] Validates response format (JSON with required fields)
- [ ] Tracks API usage (tokens, cost)
- [ ] API keys never logged in plaintext
- [ ] Unit tests achieve >80% coverage

---

## EXPECTED DELIVERABLES

**Files to Create:**

- `src/agentic_bookkeeper/llm/anthropic_provider.py`

**Files to Modify:**

- `src/agentic_bookkeeper/llm/__init__.py` (export provider)

---

## VALIDATION COMMANDS

```bash
# Test Anthropic provider with mock
pytest src/agentic_bookkeeper/tests/test_llm_providers.py::TestAnthropicProvider -v

# Test with real API (requires API key)
python -c "
from src.agentic_bookkeeper.llm.anthropic_provider import AnthropicProvider
provider = AnthropicProvider(api_key='YOUR_KEY')
result = provider.extract_transaction('test_receipt.jpg')
print(result)
"
```

---

## IMPLEMENTATION NOTES

### Extraction Prompt Template

```python
EXTRACTION_PROMPT = """
Extract transaction information from this receipt/invoice image.

Return a JSON object with these fields:
- date: Transaction date (YYYY-MM-DD)
- type: "income" or "expense"
- category: Business category
- vendor_customer: Vendor or customer name
- description: Brief description
- amount: Total amount (number)
- tax_amount: Tax amount if shown (number)

Respond ONLY with valid JSON, no other text.
"""
```

### Key Implementation Details

1. **API Authentication:** Use Anthropic Python SDK with API key
2. **Vision API:** Use claude-3-opus or claude-3-sonnet model
3. **Error Handling:** Catch Anthropic exceptions (RateLimitError, APIError)
4. **Retry Logic:** Exponential backoff with 3 retries
5. **Response Validation:** Check for required fields, validate types
6. **Usage Tracking:** Log tokens and estimated cost

---

## NOTES

- Claude Vision API is cost-effective and accurate
- Rate limits: 50 requests per minute (tier dependent)
- Image size limits: 5MB per image
- Response time typically 3-10 seconds
- Claude excels at structured data extraction

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-010 - XAI Provider Implementation
