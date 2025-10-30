# Task Specification: T-038

**Task Name:** Reports Widget Implementation
**Task ID:** T-038
**Phase:** Phase 3: Reporting Engine
**Sprint:** Sprint 6: Report Generation
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 6 hours
**Dependencies:** T-035, T-036, T-037

---

## OBJECTIVE

Create reports widget GUI with report type selection, date range picker, format selector, preview, and export functionality.

---

## REQUIREMENTS

### Functional Requirements

- Report type selector (Income Statement, Expense Report)
- Date range picker (presets + custom)
- Format selector (PDF, CSV, JSON)
- Preview functionality
- Generate button
- Save dialog
- Progress indicator
- Error handling
- Connect to report generator

---

## ACCEPTANCE CRITERIA

- [ ] User can select report parameters
- [ ] Preview shows report before export
- [ ] All export formats work
- [ ] Progress shown during generation
- [ ] Error messages are clear

---

## EXPECTED DELIVERABLES

**Files to Create:**

- `src/agentic_bookkeeper/gui/reports_widget.py`

---

## VALIDATION COMMANDS

```bash
pytest src/agentic_bookkeeper/tests/test_gui_reports.py -v
```

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-039 - Unit Tests for Reporting
