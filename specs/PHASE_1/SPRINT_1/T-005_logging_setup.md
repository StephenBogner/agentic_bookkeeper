# Task Specification: T-005

**Task Name:** Logging Setup
**Task ID:** T-005
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 1: Project Setup & Database Foundation
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** High
**Estimated Effort:** 2 hours
**Dependencies:** T-001

---

## OBJECTIVE

Implement a comprehensive logging system with structured logging, multiple handlers, log rotation, and sensitive data filtering to support debugging and monitoring of the Agentic Bookkeeper application.

**Success Criteria:**
- Logs written to both file and console
- Log rotation works correctly
- Different log levels filter appropriately
- Sensitive data (API keys) is not logged
- Structured logging with context information

---

## REQUIREMENTS

### Functional Requirements

1. **Logging Configuration**
   - Configure Python logging module
   - Set up log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - Support configuration via environment variables
   - Default to INFO level in production, DEBUG in development

2. **File and Console Handlers**
   - Console handler for immediate feedback
   - File handler for persistent logs
   - Different formatters for console (simple) vs file (detailed)
   - Console with color coding (optional)

3. **Log Rotation**
   - Rotate log files daily or by size (10MB limit)
   - Keep last 30 days of logs
   - Compressed old logs (gzip)
   - Automatic cleanup of old logs

4. **Structured Logging**
   - Include timestamp, level, module, function name
   - Include context information (user, transaction_id if applicable)
   - JSON format option for log analysis tools
   - Correlation IDs for request tracking

5. **Sensitive Data Filtering**
   - Filter API keys from log output
   - Filter passwords and tokens
   - Redact sensitive fields in data structures
   - Configurable patterns for filtering

6. **Module-Specific Loggers**
   - Separate loggers for each module (core, llm, gui, models)
   - Configurable log levels per module
   - Hierarchical logger names

### Non-Functional Requirements

- Minimal performance impact (<5ms per log statement)
- Thread-safe logging
- No log loss during rotation
- Graceful handling of disk space issues

---

## DESIGN CONSIDERATIONS

### Logger Setup

```python
"""
Module: logger
Purpose: Logging configuration and utilities
Author: Stephen Bogner
Created: 2025-10-29
"""

import logging
import logging.handlers
import os
import re
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Sensitive data patterns
SENSITIVE_PATTERNS = [
    (re.compile(r'(api[_-]?key["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.I), r'\1***REDACTED***\3'),
    (re.compile(r'(token["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.I), r'\1***REDACTED***\3'),
    (re.compile(r'(password["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.I), r'\1***REDACTED***\3'),
    (re.compile(r'(Bearer\s+)([A-Za-z0-9\-._~+/]+=*)', re.I), r'\1***REDACTED***'),
]

class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive data from log messages."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record, redacting sensitive data."""
        if isinstance(record.msg, str):
            for pattern, replacement in SENSITIVE_PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)

        # Filter args
        if record.args:
            filtered_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    for pattern, replacement in SENSITIVE_PATTERNS:
                        arg = pattern.sub(replacement, arg)
                filtered_args.append(arg)
            record.args = tuple(filtered_args)

        return True


def setup_logging(
    log_dir: Optional[Path] = None,
    log_level: str = "INFO",
    console: bool = True,
    file_logging: bool = True
) -> logging.Logger:
    """
    Set up application logging with file rotation and console output.

    Args:
        log_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console: Enable console logging
        file_logging: Enable file logging

    Returns:
        Configured root logger
    """
    # Get root logger
    logger = logging.getLogger('agentic_bookkeeper')
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        fmt='%(levelname)s: %(message)s'
    )

    # Add sensitive data filter
    sensitive_filter = SensitiveDataFilter()

    # Console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        console_handler.addFilter(sensitive_filter)
        logger.addHandler(console_handler)

    # File handler with rotation
    if file_logging:
        if log_dir is None:
            log_dir = Path.home() / '.agentic_bookkeeper' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / 'agentic_bookkeeper.log'

        # Rotating file handler (10MB max, keep 30 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=30,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        file_handler.addFilter(sensitive_filter)
        logger.addHandler(file_handler)

    logger.info(f"Logging initialized at {log_level} level")
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name

    Returns:
        Configured logger
    """
    return logging.getLogger(f'agentic_bookkeeper.{name}')
```

### Structured Logging Helper

```python
class StructuredLogger:
    """Helper for structured logging with context."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.context: Dict[str, Any] = {}

    def set_context(self, **kwargs) -> None:
        """Set context for subsequent log messages."""
        self.context.update(kwargs)

    def clear_context(self) -> None:
        """Clear logging context."""
        self.context.clear()

    def _format_message(self, message: str) -> str:
        """Format message with context."""
        if self.context:
            context_str = ' | '.join(f'{k}={v}' for k, v in self.context.items())
            return f'{message} | {context_str}'
        return message

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context."""
        self.logger.debug(self._format_message(message), **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message with context."""
        self.logger.info(self._format_message(message), **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context."""
        self.logger.warning(self._format_message(message), **kwargs)

    def error(self, message: str, exc_info=False, **kwargs) -> None:
        """Log error message with context."""
        self.logger.error(self._format_message(message), exc_info=exc_info, **kwargs)

    def critical(self, message: str, exc_info=False, **kwargs) -> None:
        """Log critical message with context."""
        self.logger.critical(self._format_message(message), exc_info=exc_info, **kwargs)
```

---

## ACCEPTANCE CRITERIA

### Must Have
- [ ] Logging module created in src/utils/logger.py
- [ ] setup_logging() function working
- [ ] Console handler outputs logs
- [ ] File handler writes to log file
- [ ] Log rotation working (by size)
- [ ] Sensitive data filter prevents API key logging
- [ ] Different log levels filter correctly
- [ ] Module-specific loggers work via get_logger()
- [ ] Type hints and docstrings complete

### Should Have
- [ ] Structured logging helper implemented
- [ ] Context information in logs
- [ ] Configurable via environment variables
- [ ] Compressed log rotation

### Nice to Have
- [ ] Color-coded console output
- [ ] JSON log format option
- [ ] Log analysis tools
- [ ] Performance profiling integration

---

## CONTEXT REQUIRED

### Information Needed
- Log directory location (from config)
- Default log level (from environment)
- Python logging best practices

### Artifacts from Previous Tasks
- T-001: Project structure
- Directory for logs (create if not exists)

---

## EXPECTED DELIVERABLES

### Files to Create
- `src/agentic_bookkeeper/utils/logger.py` - Logging setup and utilities

### Files to Modify
- `src/agentic_bookkeeper/utils/__init__.py` - Export logging functions
- `.env.example` - Add LOG_LEVEL and LOG_DIR variables

---

## VALIDATION COMMANDS

```bash
# Test basic logging
python -c "
from src.agentic_bookkeeper.utils.logger import setup_logging, get_logger
setup_logging(log_level='DEBUG')
logger = get_logger('test')
logger.debug('Debug message')
logger.info('Info message')
logger.warning('Warning message')
logger.error('Error message')
print('Logging test completed')
"

# Test sensitive data filtering
python -c "
from src.agentic_bookkeeper.utils.logger import setup_logging, get_logger
setup_logging(log_level='INFO')
logger = get_logger('test')
logger.info('API key: sk-test123456789')
logger.info('Token: Bearer abc123xyz')
logger.info('Password: secret123')
print('Check log file - sensitive data should be redacted')
"

# Test log rotation
python -c "
from src.agentic_bookkeeper.utils.logger import setup_logging, get_logger
setup_logging()
logger = get_logger('test')
for i in range(1000):
    logger.info(f'Test message {i}' * 100)  # Generate large logs
print('Log rotation test completed')
"

# Verify log file created
ls -lh ~/.agentic_bookkeeper/logs/
```

---

## IMPLEMENTATION NOTES

### Step-by-Step Execution

1. **Create Logger Module**
   - Create src/utils/logger.py
   - Import necessary logging modules

2. **Implement SensitiveDataFilter**
   - Create filter class
   - Add regex patterns for sensitive data
   - Test redaction

3. **Implement setup_logging()**
   - Configure root logger
   - Add console handler
   - Add file handler with rotation
   - Apply filters

4. **Implement get_logger()**
   - Return child logger with proper naming
   - Inherit configuration from root

5. **Add Structured Logging Helper**
   - Create StructuredLogger class
   - Implement context management
   - Test with context data

6. **Test Thoroughly**
   - Test all log levels
   - Test sensitive data filtering
   - Test log rotation
   - Test in different modules

---

## NOTES

### Important Considerations

- Use rotating file handler to prevent unbounded log growth
- Sensitive data filtering is critical for security
- Console logs should be less verbose than file logs
- Thread-safe by default with Python logging module
- Log rotation happens automatically when file size exceeded

### Potential Issues

- **Issue:** Log rotation fails due to permission errors
  - **Solution:** Ensure log directory is writable, handle errors gracefully

- **Issue:** Sensitive data patterns miss some formats
  - **Solution:** Test thoroughly, add patterns as needed

- **Issue:** Performance impact of regex filtering
  - **Solution:** Compile patterns once, profile if needed

- **Issue:** Log files fill disk space
  - **Solution:** Implement log retention policy, monitor disk usage

### Log Levels Guide

- **DEBUG**: Detailed diagnostic information (dev only)
- **INFO**: General informational messages (default)
- **WARNING**: Warning messages (potential issues)
- **ERROR**: Error messages (something failed)
- **CRITICAL**: Critical errors (application may crash)

---

## COMPLETION CHECKLIST

- [ ] logger.py module created
- [ ] setup_logging() function implemented
- [ ] get_logger() function implemented
- [ ] SensitiveDataFilter implemented and tested
- [ ] Console handler working
- [ ] File handler working with rotation
- [ ] Sensitive data filtering verified
- [ ] Log levels working correctly
- [ ] Type hints complete
- [ ] Docstrings complete
- [ ] Manual testing completed
- [ ] Log files created in correct location
- [ ] .env.example updated with logging variables

---

## REVISION HISTORY

| Version | Date       | Author | Changes                         |
|---------|------------|--------|---------------------------------|
| 1.0     | 2025-10-29 | Claude | Initial task specification      |

---

**Next Task:** T-006 - Unit Tests for Database & Models
