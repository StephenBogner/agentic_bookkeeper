# Task Specification: T-039

**Task Name:** Unit Tests for Reporting
**Task ID:** T-039
**Phase:** Phase 3: Reporting Engine
**Sprint:** Sprint 6: Report Generation
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 5 hours
**Dependencies:** T-032, T-033, T-034, T-035, T-036, T-037, T-038

---

## OBJECTIVE

Create comprehensive unit tests for report generator, templates, exporters, and reports widget achieving >80% coverage.

---

## REQUIREMENTS

### Functional Requirements
- Test income statement generation
- Test expense report generation
- Test date range filtering
- Test all calculations
- Test PDF export
- Test CSV export
- Test JSON export
- Validate output formats
- Achieve >80% coverage

---

## ACCEPTANCE CRITERIA

- [ ] All tests pass
- [ ] Coverage >80% for reporting modules
- [ ] Calculations validated
- [ ] Export formats verified
- [ ] Edge cases tested

---

## EXPECTED DELIVERABLES

**Files to Create:**
- `src/agentic_bookkeeper/tests/test_report_generator.py`
- `src/agentic_bookkeeper/tests/test_exporters.py`
- `src/agentic_bookkeeper/tests/test_gui_reports.py`

---

## VALIDATION COMMANDS

```bash
pytest src/agentic_bookkeeper/tests/test_report*.py -v
pytest src/agentic_bookkeeper/tests/test_exporters.py -v
```

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-040 - Integration Test Suite Expansion (Phase 4)
