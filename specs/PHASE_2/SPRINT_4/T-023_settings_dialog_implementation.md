# Task Specification: T-023

**Task Name:** Settings Dialog Implementation
**Task ID:** T-023
**Phase:** Phase 2: GUI Development
**Sprint:** Sprint 4: GUI Foundation
**Created:** 2025-10-29
**Status:** Completed
**Completed:** 2025-10-28
**Priority:** Critical
**Estimated Effort:** 5 hours
**Dependencies:** T-021

---

## OBJECTIVE

Create comprehensive settings dialog for configuring watch/archive directories, LLM provider, API keys, tax jurisdiction, and fiscal year settings.

---

## REQUIREMENTS

### Functional Requirements
- Directory selection for watch folder
- Directory selection for archive folder
- LLM provider dropdown
- API key input (masked)
- Tax jurisdiction selector (CRA/IRS)
- Fiscal year start date selector
- Save/cancel buttons
- Input validation
- Connect to configuration manager

### Non-Functional Requirements
- API keys must be masked in UI
- Input validation must be comprehensive
- Settings must persist correctly

---

## ACCEPTANCE CRITERIA

- [x] Settings dialog opens from menu
- [x] All inputs validate correctly
- [x] Settings persist to configuration
- [x] Invalid inputs show error messages
- [x] API keys are masked in UI
- [x] Directory selection works
- [x] All fields save properly

---

## EXPECTED DELIVERABLES

**Files Created:**
- `src/agentic_bookkeeper/gui/settings_dialog.py` (406 lines)
- `src/agentic_bookkeeper/tests/test_gui_settings.py` (354 lines)

---

## VALIDATION COMMANDS

```bash
# Run tests
pytest src/agentic_bookkeeper/tests/test_gui_settings.py -v
```

---

## IMPLEMENTATION NOTES

### Files Created
- Settings dialog with complete form layout
- Comprehensive validation (30 tests)
- 97% code coverage

### Test Results
- 30 unit tests, all passing
- 97% code coverage
- Test execution time: 14.35s
- Validates initialization, widgets, loading, validation, saving, interactions, buttons

### Features Implemented
- Watch/archive directory selection with browse buttons
- LLM provider dropdown (OpenAI, Anthropic, Google, XAI)
- Masked API key input field
- Tax jurisdiction selector (CRA/IRS)
- Fiscal year start date picker
- Comprehensive validation for all inputs
- Save/Cancel/Apply buttons
- Integration with Config manager
- Error message display for invalid inputs

---

## NOTES

**Completed:** 2025-10-28
**Result:** Fully functional settings dialog with comprehensive validation, API key masking, and configuration persistence.

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-024 - Application Startup & Initialization
