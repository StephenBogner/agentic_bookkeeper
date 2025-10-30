# Task Specification: T-030

**Task Name:** Document Review Dialog
**Task ID:** T-030
**Phase:** Phase 2: GUI Development
**Sprint:** Sprint 5: Transaction Management UI
**Created:** 2025-10-29
**Status:** Completed
**Completed:** 2025-10-28
**Priority:** Critical
**Estimated Effort:** 5 hours
**Dependencies:** Phase 1 complete

---

## OBJECTIVE

Implement document review dialog showing extracted transaction data alongside document preview, allowing user review and editing before saving.

---

## REQUIREMENTS

### Functional Requirements
- Display extracted transaction data in form
- Show document preview (image or PDF)
- Allow editing of all extracted fields
- Accept button to save transaction
- Reject button to archive without saving
- Field validation before accept
- Connect to document processor
- Update transaction manager on accept
- Split-pane layout (document preview + form)

### Non-Functional Requirements
- Document preview must be clear
- Form must be responsive
- Validation must be comprehensive

---

## ACCEPTANCE CRITERIA

- [x] Dialog shows extracted data and document preview
- [x] User can edit extracted fields
- [x] Accept saves transaction to database
- [x] Reject archives document without saving
- [x] Validation prevents invalid data
- [x] Document preview works for images
- [x] Split-pane layout is user-friendly

---

## EXPECTED DELIVERABLES

**Files Created:**
- `src/agentic_bookkeeper/gui/document_review_dialog.py` (489 lines)
- `src/agentic_bookkeeper/tests/test_gui_document_review_dialog.py` (547 lines)

---

## VALIDATION COMMANDS

```bash
# Run tests
pytest src/agentic_bookkeeper/tests/test_gui_document_review_dialog.py -v
```

---

## IMPLEMENTATION NOTES

### Files Created
- Document review dialog with split-pane layout
- Comprehensive test suite (33 tests)
- 90% code coverage

### Test Results
- 33 tests passing
- 90% coverage for document_review_dialog.py
- All acceptance criteria met

### Features Implemented
- Split-pane layout with QSplitter (40/60 proportions)
- Document preview (left pane) with zoom and scroll
- Full transaction form (right pane)
- Image preview with QLabel and QPixmap
- All fields editable
- Dynamic category filtering based on type and jurisdiction
- Accept/Reject workflow with confirmation dialogs
- Comprehensive field validation
- Document filename automatically stored with transaction
- Test-mode detection for automated testing
- Integration with TransactionManager and DocumentProcessor

### Implementation Details
- QSplitter for resizable panes
- QScrollArea for document preview
- Full transaction form matching add/edit dialogs
- Category dropdown updates when type or jurisdiction changes
- Accept button saves to database and archives document
- Reject button archives without saving
- Confirmation dialogs for both actions
- Error handling for file operations

---

## NOTES

**Completed:** 2025-10-28
**Actual Time:** 4 hours
**Result:** Comprehensive document review dialog with split-pane layout, document preview, and full editing capabilities.

**Key Features:**
- Side-by-side document and data view
- Full editing before acceptance
- Smart category filtering
- Robust validation
- Clear accept/reject workflow

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-031 - GUI Unit Tests - Transaction Management
