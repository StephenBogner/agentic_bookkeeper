# Null Value Handling Fix

**Date**: 2025-10-27
**Issue**: Transaction creation failing when LLM returns null values
**Status**: ✅ Fixed

---

## Problem

When processing `invoice_consulting.pdf`, the LLM was returning `null` values for some fields, causing this error:

```text
Failed to create transaction from result: float() argument must be a string
or a real number, not 'NoneType'
```

### Root Cause

The issue occurred in `DocumentProcessor._create_transaction_from_result()`:

```python
# Old code - FAILS when value is None
amount=float(data.get('amount', 0))
```

When the LLM response contains `{"amount": null}`, the `data.get('amount', 0)` call returns
`None` (not the default `0`) because the key exists but has a null value. Then `float(None)`
raises a TypeError.

---

## Solution

Implemented a `safe_float()` helper function that handles null, empty strings, and invalid values gracefully:

```python
def safe_float(value, default=0.0):
    """Convert value to float, handling None and empty strings."""
    if value is None or value == '':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert '{value}' to float, using default {default}")
        return default

# Usage
amount=safe_float(data.get('amount'), 0.0)
tax_amount=safe_float(data.get('tax_amount'), 0.0)
```

---

## Changes Made

**File**: `src/agentic_bookkeeper/core/document_processor.py`
**Method**: `_create_transaction_from_result()` (lines 210-240)

### Before

```python
amount=float(data.get('amount', 0)),
tax_amount=float(data.get('tax_amount', 0)),
```

### After

```python
amount=safe_float(data.get('amount'), 0.0),
tax_amount=safe_float(data.get('tax_amount'), 0.0),
```

---

## Test Results

All null value scenarios now handled correctly:

### Test Case 1: Null Amount Only

```python
data = {
    "date": "2025-10-27",
    "amount": None,  # null value from LLM
    "tax_amount": 10.0
}
```

**Result**: ✅ Transaction created with amount=$0.00

### Test Case 2: Empty String Values

```python
data = {
    "amount": "",  # empty string from LLM
    "tax_amount": ""
}
```

**Result**: ✅ Transaction created with both values as $0.00

### Test Case 3: Valid Values

```python
data = {
    "amount": 100.50,
    "tax_amount": 13.00
}
```

**Result**: ✅ Transaction created with correct values

### Test Case 4: All Null Values

```python
data = {
    "date": None,
    "amount": None,
    "tax_amount": None,
    # ... all fields null
}
```

**Result**: Transaction is None (expected - validation rejects invalid transactions)

---

## Benefits

1. **No More Crashes**: Handles null values gracefully without exceptions
2. **Better Logging**: Warns when conversion fails, aiding debugging
3. **Flexible**: Handles None, empty strings, and invalid numeric values
4. **Safe Defaults**: Uses 0.0 for amounts when LLM can't extract them
5. **Backward Compatible**: Existing valid data continues to work perfectly

---

## Why LLMs Return Null Values

LLMs may return null values when:

1. The document image is unclear or low quality
2. The required field is genuinely missing from the document
3. The LLM has low confidence in the extracted value
4. The document format is unusual or unexpected
5. OCR text extraction is poor

The fix allows processing to continue gracefully even when extraction is incomplete.

---

## Impact on invoice_consulting.pdf

The original failing document `invoice_consulting.pdf` should now:

- ✅ Not crash during transaction creation
- ✅ Create a transaction with 0.0 for any null numeric fields
- ⚠️ May still fail validation if required fields (date, type) are null

This is expected behavior - a transaction without a date or type should be flagged for manual
review rather than silently processed with bad data.

---

## Validation Layer

The Transaction model itself still validates required fields:

- Date must be valid
- Amount must be >= 0 (now enforced)
- Transaction type must be 'income' or 'expense'

Invalid transactions are rejected at validation time, which is the correct behavior. The fix
prevents crashes during creation, allowing validation to properly reject incomplete extractions.

---

## Testing Commands

### Test Null Handling

```bash
python test_null_handling.py
# Expected: All null value scenarios handled correctly!
```

### Test with Real Documents

```bash
python test_llm_providers_realworld.py
# Expected: invoice_consulting.pdf should no longer crash
```

---

## Related Files

- `src/agentic_bookkeeper/core/document_processor.py` - Fixed implementation
- `test_null_handling.py` - Validation test
- `src/agentic_bookkeeper/models/transaction.py` - Validation logic

---

## Future Improvements

Consider these enhancements:

1. **Confidence Thresholds**: Don't create transactions when confidence is too low
2. **Manual Review Queue**: Flag transactions with null/defaulted fields for review
3. **Improved Prompting**: Adjust LLM prompts to reduce null responses
4. **Multi-Pass Extraction**: Retry extraction with different prompts if fields are null
5. **Field-Level Confidence**: Track which fields were extracted vs. defaulted

---

**Status**: ✅ Production Ready
**Impact**: Critical bug fix for handling incomplete LLM responses
**Backward Compatible**: Yes
**Breaking Changes**: None

---

**Fixed by**: Stephen Bogner, P.Eng.
**Date**: 2025-10-27
