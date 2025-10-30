# Task Specification: T-007

**Task Name:** LLM Provider Abstraction
**Task ID:** T-007
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 2: LLM Integration & Document Processing
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 3 hours
**Dependencies:** T-004

---

## OBJECTIVE

Create an abstract base class defining the interface for all LLM providers, including methods for document extraction, response validation, error handling, and retry logic with exponential backoff.

**Success Criteria:**
- Abstract base class defines clear contract for LLM providers
- All required methods are abstract
- Error handling is comprehensive
- Retry logic with exponential backoff implemented
- Rate limiting interface defined
- Documentation is complete

---

## REQUIREMENTS

### Functional Requirements

1. **Abstract Base Class**
   - Define LLMProvider abstract base class
   - Abstract method: extract_transaction(document_data, document_type)
   - Abstract method: validate_response(response)
   - Abstract method: get_provider_name()

2. **Response Validation Interface**
   - Define expected response structure
   - Validate required fields present
   - Validate data types
   - Return structured validation errors

3. **Error Handling Base**
   - Define LLMError exception hierarchy
   - APIError, ValidationError, RateLimitError, AuthenticationError
   - Include provider name and error details
   - Logging of all errors

4. **Retry Logic**
   - Implement retry decorator with exponential backoff
   - Configurable max retries (default 3)
   - Configurable backoff multiplier (default 2)
   - Retry only on transient errors
   - Log retry attempts

5. **Rate Limiting Interface**
   - Define rate limit tracking method
   - Check rate limits before API calls
   - Wait if rate limited
   - Log rate limit events

### Non-Functional Requirements

- Provider implementations must be swappable
- Error messages must be clear and actionable
- Retry logic must not cause infinite loops
- Thread-safe implementation

---

## DESIGN CONSIDERATIONS

```python
"""
Module: llm_provider
Purpose: Abstract base class for LLM providers
Author: Stephen Bogner
Created: 2025-10-29
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Base exception for LLM provider errors."""
    pass


class APIError(LLMError):
    """API request failed."""
    pass


class ValidationError(LLMError):
    """Response validation failed."""
    pass


class RateLimitError(LLMError):
    """Rate limit exceeded."""
    pass


class AuthenticationError(LLMError):
    """Authentication failed."""
    pass


def retry_with_backoff(max_retries: int = 3, backoff_multiplier: float = 2.0):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        backoff_multiplier: Multiplier for backoff delay

    Transient errors (rate limit, temporary API failures) are retried.
    Permanent errors (authentication, validation) are not retried.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = 1.0  # Initial delay in seconds

            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)

                except RateLimitError as e:
                    if retries == max_retries:
                        logger.error(f"Max retries reached: {e}")
                        raise

                    logger.warning(f"Rate limited, retry {retries+1}/{max_retries} after {delay}s")
                    time.sleep(delay)
                    delay *= backoff_multiplier
                    retries += 1

                except APIError as e:
                    if retries == max_retries:
                        logger.error(f"Max retries reached: {e}")
                        raise

                    logger.warning(f"API error, retry {retries+1}/{max_retries} after {delay}s: {e}")
                    time.sleep(delay)
                    delay *= backoff_multiplier
                    retries += 1

                except (AuthenticationError, ValidationError) as e:
                    # Don't retry permanent errors
                    logger.error(f"Permanent error, not retrying: {e}")
                    raise

            return None  # Should never reach here

        return wrapper
    return decorator


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All LLM provider implementations must inherit from this class
    and implement the abstract methods.
    """

    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize LLM provider.

        Args:
            api_key: API key for the provider
            config: Optional configuration dictionary
        """
        self.api_key = api_key
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.

        Returns:
            Provider name (e.g., 'OpenAI', 'Anthropic')
        """
        pass

    @abstractmethod
    @retry_with_backoff(max_retries=3)
    def extract_transaction(
        self,
        document_data: bytes,
        document_type: str
    ) -> Dict[str, Any]:
        """
        Extract transaction data from document using LLM.

        Args:
            document_data: Document content (image bytes or PDF)
            document_type: Type of document ('pdf', 'image')

        Returns:
            Extracted transaction data as dictionary

        Raises:
            APIError: If API request fails
            ValidationError: If response is invalid
            RateLimitError: If rate limited
            AuthenticationError: If authentication fails
        """
        pass

    def validate_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate LLM response structure.

        Args:
            response: Response dictionary from LLM

        Returns:
            True if valid, raises ValidationError if invalid

        Raises:
            ValidationError: If response structure is invalid
        """
        required_fields = ['date', 'type', 'category', 'amount']

        for field in required_fields:
            if field not in response:
                raise ValidationError(f"Missing required field: {field}")

        # Validate types
        if response['type'] not in ['income', 'expense']:
            raise ValidationError(f"Invalid type: {response['type']}")

        try:
            amount = float(response['amount'])
            if amount < 0:
                raise ValidationError(f"Amount must be non-negative: {amount}")
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid amount: {response['amount']}")

        return True

    def _check_rate_limit(self) -> None:
        """
        Check if rate limit allows request.

        Raises:
            RateLimitError: If rate limited
        """
        # Default implementation - override in subclasses if needed
        pass

    def _track_usage(self, tokens: int) -> None:
        """
        Track API usage for monitoring.

        Args:
            tokens: Number of tokens used
        """
        self.logger.debug(f"API usage: {tokens} tokens")
```

---

## ACCEPTANCE CRITERIA

### Must Have
- [ ] LLMProvider abstract base class created
- [ ] All abstract methods defined
- [ ] Exception hierarchy implemented
- [ ] retry_with_backoff decorator implemented
- [ ] validate_response method implemented
- [ ] Type hints complete
- [ ] Docstrings complete

### Should Have
- [ ] Rate limiting interface defined
- [ ] Usage tracking method
- [ ] Configurable retry parameters
- [ ] Comprehensive error messages

### Nice to Have
- [ ] Async support for API calls
- [ ] Caching interface
- [ ] Cost tracking

---

## EXPECTED DELIVERABLES

### Files to Create
- `src/agentic_bookkeeper/llm/llm_provider.py` - Abstract base class

---

## VALIDATION COMMANDS

```bash
# Verify abstract class
python -c "
from src.agentic_bookkeeper.llm.llm_provider import LLMProvider
try:
    p = LLMProvider('test_key')
except TypeError as e:
    print('Abstract class working:', 'abstract' in str(e).lower())
"

# Test retry decorator
python -c "
from src.agentic_bookkeeper.llm.llm_provider import retry_with_backoff, APIError
import time

@retry_with_backoff(max_retries=2, backoff_multiplier=1.5)
def test_func(fail_count):
    if fail_count[0] > 0:
        fail_count[0] -= 1
        raise APIError('Test error')
    return 'Success'

fail_count = [2]
start = time.time()
result = test_func(fail_count)
elapsed = time.time() - start
print(f'Retry test: {result}, elapsed: {elapsed:.1f}s')
"
```

---

## IMPLEMENTATION NOTES

### Key Points

1. Use ABC and abstractmethod from abc module
2. Decorator pattern for retry logic
3. Exception hierarchy for different error types
4. Default validate_response can be overridden
5. Logging throughout for debugging

---

## COMPLETION CHECKLIST

- [ ] LLMProvider class created
- [ ] Exception classes created
- [ ] retry_with_backoff decorator implemented
- [ ] Abstract methods defined
- [ ] validate_response implemented
- [ ] Documentation complete
- [ ] Manual testing completed

---

## REVISION HISTORY

| Version | Date       | Author | Changes                         |
|---------|------------|--------|---------------------------------|
| 1.0     | 2025-10-29 | Claude | Initial task specification      |

---

**Next Task:** T-008 - OpenAI Provider Implementation
