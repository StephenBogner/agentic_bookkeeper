# Task Specification: T-004

**Task Name:** Configuration Management
**Task ID:** T-004
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 1: Project Setup & Database Foundation
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 3 hours
**Dependencies:** T-002

---

## OBJECTIVE

Implement a comprehensive configuration management system to handle environment variables, API keys, application settings, and CRA/IRS tax categories with proper encryption and validation.

**Success Criteria:**

- Configuration loads from .env and JSON files
- API keys are stored encrypted in database
- Invalid configuration is rejected with clear errors
- Default configuration creates successfully
- CRA and IRS category files are properly structured

---

## REQUIREMENTS

### Functional Requirements

1. **Environment Variable Loading**
   - Load configuration from .env file using python-dotenv
   - Support for API keys (OpenAI, Anthropic, XAI, Google)
   - Support for application settings (directories, database path)
   - Support for defaults when variables not set

2. **API Key Management**
   - Store API keys encrypted in database
   - Encrypt keys using cryptography library (Fernet)
   - Decrypt keys for use at runtime
   - Never log or display API keys
   - Validate API key format

3. **Category Configuration**
   - Load CRA categories from JSON file
   - Load IRS categories from JSON file
   - Validate category structure
   - Provide category lookup methods
   - Support for category codes and descriptions

4. **Configuration Persistence**
   - Store configuration in database config table
   - Load configuration from database on startup
   - Update configuration via setter methods
   - Validate before persisting

5. **Default Configuration**
   - Generate default configuration if not exists
   - Create default directories
   - Set reasonable defaults for all settings
   - Document all configuration options

### Non-Functional Requirements

- API keys encrypted at rest
- Configuration validation prevents invalid states
- Performance: load config <100ms
- Thread-safe configuration access

---

## DESIGN CONSIDERATIONS

### Config Class Structure

```python
"""
Module: config
Purpose: Configuration management with encryption
Author: Stephen Bogner
Created: 2025-10-29
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

class Config:
    """
    Application configuration manager with encryption support.

    Handles loading configuration from environment variables, JSON files,
    and database storage with encryption for sensitive data.
    """

    def __init__(self, db_connection=None):
        """Initialize configuration manager."""
        self.db = db_connection
        self._encryption_key = None
        self._cache = {}

        # Load environment variables
        load_dotenv()

        # Load or generate encryption key
        self._init_encryption_key()

        # Load categories
        self._cra_categories = self._load_categories('cra')
        self._irs_categories = self._load_categories('irs')

    def _init_encryption_key(self) -> None:
        """Initialize or load encryption key."""
        pass

    def _load_categories(self, jurisdiction: str) -> Dict[str, str]:
        """Load category definitions from JSON."""
        pass

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        pass

    def set(self, key: str, value: Any, encrypt: bool = False) -> None:
        """Set configuration value."""
        pass

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get decrypted API key for provider."""
        pass

    def set_api_key(self, provider: str, api_key: str) -> None:
        """Store encrypted API key."""
        pass

    def get_categories(self, jurisdiction: str) -> Dict[str, str]:
        """Get categories for tax jurisdiction."""
        pass

    def validate(self) -> bool:
        """Validate current configuration."""
        pass
```

### Category JSON Structure

**config/categories_cra.json:**

```json
{
  "meta": {
    "jurisdiction": "CRA",
    "country": "Canada",
    "version": "1.0",
    "updated": "2025-10-29"
  },
  "income_categories": {
    "SALES": "Sales of goods or services",
    "CONSULTING": "Consulting income",
    "INTEREST": "Interest income",
    "DIVIDENDS": "Dividend income",
    "RENTAL": "Rental income",
    "OTHER_INCOME": "Other income"
  },
  "expense_categories": {
    "ADVERTISING": "Advertising and promotion",
    "OFFICE": "Office expenses",
    "SUPPLIES": "Supplies",
    "VEHICLE": "Vehicle expenses",
    "TRAVEL": "Travel expenses",
    "MEALS": "Meals and entertainment (50%)",
    "RENT": "Rent",
    "UTILITIES": "Utilities",
    "TELEPHONE": "Telephone and internet",
    "INSURANCE": "Insurance",
    "PROFESSIONAL_FEES": "Professional fees",
    "BANK_CHARGES": "Bank charges",
    "DEPRECIATION": "Depreciation",
    "OTHER_EXPENSES": "Other expenses"
  }
}
```

**config/categories_irs.json:**

```json
{
  "meta": {
    "jurisdiction": "IRS",
    "country": "United States",
    "version": "1.0",
    "updated": "2025-10-29"
  },
  "income_categories": {
    "GROSS_RECEIPTS": "Gross receipts or sales",
    "RETURNS_ALLOWANCES": "Returns and allowances",
    "OTHER_INCOME": "Other income"
  },
  "expense_categories": {
    "ADVERTISING": "Advertising",
    "CAR_TRUCK": "Car and truck expenses",
    "COMMISSIONS": "Commissions and fees",
    "CONTRACT_LABOR": "Contract labor",
    "DEPLETION": "Depletion",
    "DEPRECIATION": "Depreciation",
    "EMPLOYEE_BENEFIT": "Employee benefit programs",
    "INSURANCE": "Insurance (other than health)",
    "INTEREST_MORTGAGE": "Interest - Mortgage",
    "INTEREST_OTHER": "Interest - Other",
    "LEGAL_PROFESSIONAL": "Legal and professional services",
    "OFFICE_EXPENSE": "Office expense",
    "PENSION_PLANS": "Pension and profit-sharing plans",
    "RENT_VEHICLES": "Rent or lease - Vehicles, machinery, equipment",
    "RENT_PROPERTY": "Rent or lease - Other business property",
    "REPAIRS": "Repairs and maintenance",
    "SUPPLIES": "Supplies",
    "TAXES_LICENSES": "Taxes and licenses",
    "TRAVEL": "Travel",
    "MEALS": "Meals and entertainment",
    "UTILITIES": "Utilities",
    "WAGES": "Wages",
    "OTHER_EXPENSES": "Other expenses"
  }
}
```

---

## ACCEPTANCE CRITERIA

### Must Have

- [ ] Config class implemented in src/utils/config.py
- [ ] Environment variables loaded from .env
- [ ] API keys encrypted before database storage
- [ ] API keys decrypted correctly for use
- [ ] CRA categories JSON file created
- [ ] IRS categories JSON file created
- [ ] Category loading and validation working
- [ ] Default configuration generator working
- [ ] Configuration persistence to database working
- [ ] Type hints and docstrings complete

### Should Have

- [ ] Configuration validation with clear error messages
- [ ] Category lookup by code or description
- [ ] Configuration caching for performance
- [ ] Environment variable override support

### Nice to Have

- [ ] Configuration hot-reloading
- [ ] Configuration export/import
- [ ] Multiple encryption key support
- [ ] Configuration version migration

---

## CONTEXT REQUIRED

### Information Needed

- Database connection from T-002
- Encryption best practices
- CRA and IRS category standards
- Environment variable naming conventions

### Artifacts from Previous Tasks

- T-001: Project structure, .env.example
- T-002: Database config table

---

## EXPECTED DELIVERABLES

### Files to Create

- `src/agentic_bookkeeper/utils/config.py` - Config class
- `config/categories_cra.json` - CRA categories
- `config/categories_irs.json` - IRS categories

### Files to Modify

- `src/agentic_bookkeeper/utils/__init__.py` - Export Config class
- `.env.example` - Ensure all variables documented

---

## VALIDATION COMMANDS

```bash
# Test configuration loading
python -c "
from src.agentic_bookkeeper.utils.config import Config
config = Config()
print('Config loaded successfully')
print('Default provider:', config.get('default_llm_provider', 'openai'))
"

# Test category loading
python -c "
from src.agentic_bookkeeper.utils.config import Config
config = Config()
cra_cats = config.get_categories('cra')
print('CRA categories:', len(cra_cats))
irs_cats = config.get_categories('irs')
print('IRS categories:', len(irs_cats))
"

# Test API key encryption (mock)
python -c "
from src.agentic_bookkeeper.utils.config import Config
config = Config()
config.set_api_key('openai', 'test_key_12345')
key = config.get_api_key('openai')
print('Encryption test:', 'PASS' if key == 'test_key_12345' else 'FAIL')
"

# Verify JSON files are valid
python -c "
import json
with open('config/categories_cra.json') as f:
    cra = json.load(f)
    print('CRA JSON valid:', 'jurisdiction' in cra.get('meta', {}))
with open('config/categories_irs.json') as f:
    irs = json.load(f)
    print('IRS JSON valid:', 'jurisdiction' in irs.get('meta', {}))
"
```

---

## IMPLEMENTATION NOTES

### Encryption Implementation

```python
from cryptography.fernet import Fernet
import base64
import os

class Config:
    def _init_encryption_key(self) -> None:
        """Initialize or load encryption key from database."""
        # Check if key exists in database
        if self.db:
            key_row = self.db.execute_query(
                "SELECT value FROM config WHERE key='encryption_key'"
            ).fetchone()

            if key_row:
                self._encryption_key = key_row[0].encode()
            else:
                # Generate new key
                self._encryption_key = Fernet.generate_key()
                # Store in database
                self.db.execute_query(
                    "INSERT INTO config (key, value) VALUES (?, ?)",
                    ('encryption_key', self._encryption_key.decode())
                )
        else:
            # Generate temporary key
            self._encryption_key = Fernet.generate_key()

    def _encrypt(self, value: str) -> str:
        """Encrypt a string value."""
        f = Fernet(self._encryption_key)
        encrypted = f.encrypt(value.encode())
        return encrypted.decode()

    def _decrypt(self, encrypted_value: str) -> str:
        """Decrypt an encrypted value."""
        f = Fernet(self._encryption_key)
        decrypted = f.decrypt(encrypted_value.encode())
        return decrypted.decode()

    def set_api_key(self, provider: str, api_key: str) -> None:
        """Store encrypted API key."""
        encrypted = self._encrypt(api_key)
        key = f'api_key_{provider}'

        if self.db:
            # Upsert into database
            self.db.execute_query(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                (key, encrypted)
            )

        # Update cache
        self._cache[key] = api_key

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get decrypted API key."""
        key = f'api_key_{provider}'

        # Check cache first
        if key in self._cache:
            return self._cache[key]

        # Try environment variable
        env_key = f'{provider.upper()}_API_KEY'
        if env_key in os.environ:
            return os.environ[env_key]

        # Try database
        if self.db:
            row = self.db.execute_query(
                "SELECT value FROM config WHERE key=?", (key,)
            ).fetchone()

            if row:
                decrypted = self._decrypt(row[0])
                self._cache[key] = decrypted
                return decrypted

        return None
```

### Category Loading

```python
def _load_categories(self, jurisdiction: str) -> Dict[str, Any]:
    """Load category definitions from JSON."""
    filename = f'categories_{jurisdiction.lower()}.json'
    filepath = Path(__file__).parent.parent.parent / 'config' / filename

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Validate structure
        if 'meta' not in data or 'jurisdiction' not in data['meta']:
            raise ValueError(f"Invalid category file structure: {filename}")

        # Combine income and expense categories
        categories = {}
        categories.update(data.get('income_categories', {}))
        categories.update(data.get('expense_categories', {}))

        logger.info(f"Loaded {len(categories)} categories for {jurisdiction.upper()}")
        return categories

    except FileNotFoundError:
        logger.error(f"Category file not found: {filename}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filename}: {e}")
        return {}

def get_categories(self, jurisdiction: str) -> Dict[str, str]:
    """Get categories for tax jurisdiction."""
    if jurisdiction.lower() == 'cra':
        return self._cra_categories.copy()
    elif jurisdiction.lower() == 'irs':
        return self._irs_categories.copy()
    else:
        raise ValueError(f"Unknown jurisdiction: {jurisdiction}")
```

---

## NOTES

### Important Considerations

- Encryption key must be stored securely in database
- API keys should never appear in logs or error messages
- Category files are read-only after creation
- Configuration changes should be validated before persistence
- Support both environment variables and database storage

### Potential Issues

- **Issue:** Encryption key loss means API keys are unrecoverable
  - **Solution:** Document backup procedures, warn users

- **Issue:** Environment variables override database config
  - **Solution:** Document precedence order clearly

- **Issue:** Category file modifications require restart
  - **Solution:** Accept limitation or implement hot-reload

- **Issue:** Multiple instances with different encryption keys
  - **Solution:** Store key in database, ensure consistent access

---

## COMPLETION CHECKLIST

- [ ] Config class implemented with all methods
- [ ] Encryption/decryption working correctly
- [ ] API key storage and retrieval tested
- [ ] CRA categories JSON created and valid
- [ ] IRS categories JSON created and valid
- [ ] Category loading working
- [ ] Environment variable loading working
- [ ] Database persistence working
- [ ] Default configuration generator working
- [ ] Type hints and docstrings complete
- [ ] Manual testing completed
- [ ] No API keys logged during testing

---

## REVISION HISTORY

| Version | Date       | Author | Changes                         |
|---------|------------|--------|---------------------------------|
| 1.0     | 2025-10-29 | Claude | Initial task specification      |

---

**Next Task:** T-005 - Logging Setup
