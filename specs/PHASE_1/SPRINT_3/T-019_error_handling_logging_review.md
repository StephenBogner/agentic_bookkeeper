# Task Specification: T-019

**Task Name:** Error Handling & Logging Review
**Task ID:** T-019
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 3: Integration & Validation
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** High
**Estimated Effort:** 2 hours
**Dependencies:** T-017

---

## OBJECTIVE

Review and improve error handling and logging across all modules to ensure comprehensive coverage, clear error messages, and no sensitive data leakage.

---

## REQUIREMENTS

### Functional Requirements

- Review all error handling paths
- Ensure all exceptions are caught and logged
- Add user-friendly error messages
- Test error scenarios
- Validate logging coverage
- Check for sensitive data in logs (API keys, personal data)
- Ensure proper log levels (DEBUG, INFO, WARNING, ERROR)
- Add contextual information to logs

### Non-Functional Requirements

- All errors must be logged with context
- No sensitive data in logs
- Error messages must be actionable
- Logs must be parseable for debugging

---

## ACCEPTANCE CRITERIA

- [ ] All error paths have exception handling
- [ ] All exceptions are logged with context
- [ ] Error messages are clear and user-friendly
- [ ] No sensitive data in logs (API keys, passwords)
- [ ] Log levels are appropriate for each message
- [ ] Error scenarios tested in unit tests
- [ ] Recovery from errors is graceful
- [ ] Logging documentation updated

---

## EXPECTED DELIVERABLES

**Files to Create:**

- None (review and improve existing files)

**Files to Modify:**

- All modules with improved error handling and logging

---

## VALIDATION COMMANDS

```bash
# Check for API keys in logs
grep -r "sk-" logs/
grep -r "api_key" logs/

# Test error scenarios
pytest src/agentic_bookkeeper/tests/ -v -k "error or exception"

# Check log output
tail -f logs/agentic_bookkeeper.log

# Validate log levels
python -c "
import logging
from src.agentic_bookkeeper.utils.logger import setup_logging
setup_logging(level=logging.DEBUG)
# Trigger various operations
"
```

---

## IMPLEMENTATION NOTES

### Error Handling Best Practices

```python
# Good: Specific exception with context
try:
    result = api_call()
except APIError as e:
    logger.error(f"API call failed: {e}", exc_info=True)
    raise ProcessingError(f"Failed to process document: {e}") from e

# Bad: Generic exception, no context
try:
    result = api_call()
except Exception as e:
    print(f"Error: {e}")
```

### Logging Best Practices

```python
import logging

logger = logging.getLogger(__name__)

# Good: Structured logging with context
logger.info("Processing document",
            extra={
                'document': filename,
                'provider': provider_name,
                'size': file_size
            })

# Good: Appropriate log levels
logger.debug("Detailed processing step")  # DEBUG for detailed flow
logger.info("Document processed successfully")  # INFO for significant events
logger.warning("Using default config")  # WARNING for recoverable issues
logger.error("Failed to process", exc_info=True)  # ERROR for failures

# Bad: Print statements
print("Processing...")

# Bad: Logging sensitive data
logger.info(f"API key: {api_key}")  # NEVER log API keys
```

### Sensitive Data Filtering

```python
import re

class SensitiveDataFilter(logging.Filter):
    """Filter sensitive data from logs."""

    PATTERNS = [
        (re.compile(r'sk-[a-zA-Z0-9]+'), 'sk-***REDACTED***'),
        (re.compile(r'"api_key":\s*"[^"]+"'), '"api_key": "***REDACTED***"'),
        (re.compile(r'password=\S+'), 'password=***REDACTED***'),
    ]

    def filter(self, record):
        """Filter sensitive data from log record."""
        if isinstance(record.msg, str):
            for pattern, replacement in self.PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        return True
```

### Error Messages for Users

```python
# Good: User-friendly with action
raise ValueError(
    "Invalid date format. Please use YYYY-MM-DD format. "
    "Example: 2025-01-15"
)

# Bad: Technical jargon
raise ValueError("Date validation failed: regex mismatch")

# Good: Explain what happened and what to do
logger.error(
    "Failed to connect to API. Please check your internet connection "
    "and verify your API key is correct."
)

# Bad: Vague error
logger.error("API error")
```

### Error Recovery Example

```python
def process_document(file_path: str) -> dict:
    """Process document with error recovery."""
    try:
        # Attempt processing
        result = _do_processing(file_path)
        logger.info(f"Successfully processed {file_path}")
        return result

    except NetworkError as e:
        # Recoverable: retry
        logger.warning(f"Network error, retrying: {e}")
        return _retry_with_backoff(file_path)

    except InvalidDocumentError as e:
        # Not recoverable: inform user
        logger.error(f"Invalid document {file_path}: {e}")
        return {
            'success': False,
            'error': str(e),
            'user_message': 'This document cannot be processed. '
                           'Please check the file is a valid receipt or invoice.'
        }

    except Exception as e:
        # Unexpected: log and re-raise
        logger.exception(f"Unexpected error processing {file_path}")
        raise ProcessingError(f"Failed to process {file_path}") from e
```

### Review Checklist

**For Each Module:**

- [ ] All exceptions are caught
- [ ] All errors are logged with context
- [ ] No print() statements (use logging)
- [ ] No sensitive data in logs
- [ ] Error messages are user-friendly
- [ ] Appropriate log levels used
- [ ] Exception chaining preserved (raise ... from e)
- [ ] Cleanup in finally blocks where needed

**Error Scenarios to Test:**

- [ ] File not found
- [ ] Invalid file format
- [ ] API timeout
- [ ] API rate limit
- [ ] Database locked
- [ ] Disk full
- [ ] Invalid configuration
- [ ] Missing API key
- [ ] Network error
- [ ] Corrupted data

---

## NOTES

- Use structured logging for easier parsing
- Always use logger, never print()
- Log at appropriate level (DEBUG, INFO, WARNING, ERROR)
- Include context in error messages
- Use exc_info=True to log stack traces
- Filter sensitive data automatically
- Test error paths explicitly
- Document common errors in troubleshooting guide
- Consider centralized error handling for GUI

### Log Level Guidelines

- **DEBUG:** Detailed information for debugging
- **INFO:** Significant events in normal operation
- **WARNING:** Unexpected but recoverable situations
- **ERROR:** Error conditions that need attention
- **CRITICAL:** Severe errors that may cause shutdown

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-020 - Phase 1 Documentation
