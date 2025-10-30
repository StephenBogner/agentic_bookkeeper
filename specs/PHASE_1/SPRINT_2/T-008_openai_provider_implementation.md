# Task Specification: T-008

**Task Name:** OpenAI Provider Implementation
**Task ID:** T-008
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 2: LLM Integration & Document Processing
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 4 hours
**Dependencies:** T-007

---

## OBJECTIVE

Implement the OpenAI LLM provider class that extracts transaction data from financial documents using GPT-4 Vision API.

---

## REQUIREMENTS

### Functional Requirements

- Implement LLMProvider abstract base class
- Authenticate with OpenAI API using API key
- Create document extraction prompt optimized for receipts/invoices
- Call GPT-4 Vision API with image data
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

- [ ] OpenAI provider class implements LLMProvider interface
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

- `src/agentic_bookkeeper/llm/openai_provider.py`

**Files to Modify:**

- `src/agentic_bookkeeper/llm/__init__.py` (export provider)

---

## VALIDATION COMMANDS

```bash
# Test OpenAI provider with mock
pytest src/agentic_bookkeeper/tests/test_llm_providers.py::TestOpenAIProvider -v

# Test with real API (requires API key)
python -c "
from src.agentic_bookkeeper.llm.openai_provider import OpenAIProvider
provider = OpenAIProvider(api_key='YOUR_KEY')
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

Example: {"date": "2025-01-15", "type": "expense", "category": "Office Supplies",
          "vendor_customer": "Staples", "description": "Printer paper",
          "amount": 45.99, "tax_amount": 5.99}
"""
```

### Key Implementation Details

1. **API Authentication:** Use OpenAI Python SDK with API key
2. **Vision API:** Use gpt-4-vision-preview model
3. **Error Handling:** Catch OpenAI exceptions (RateLimitError, APIError)
4. **Retry Logic:** Exponential backoff with 3 retries
5. **Response Validation:** Check for required fields, validate types
6. **Usage Tracking:** Log tokens and estimated cost

---

## NOTES

- GPT-4 Vision API has higher costs than text-only models
- Rate limits vary by account tier
- Image size limits: 20MB, 4096x4096 pixels
- Response time typically 5-15 seconds
- Consider fallback to GPT-3.5 for cost optimization

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-009 - Anthropic Provider Implementation
