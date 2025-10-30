# Task Specification: T-034

**Task Name:** Expense Report Template
**Task ID:** T-034
**Phase:** Phase 3: Reporting Engine
**Sprint:** Sprint 6: Report Generation
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 3 hours
**Dependencies:** T-032

---

## OBJECTIVE

Create expense report template grouping expenses by category with totals and percentages for tax filing.

---

## REQUIREMENTS

### Functional Requirements

- Group expenses by category
- Calculate totals per category
- Calculate percentage of total for each category
- Include CRA/IRS category codes
- Format for tax filing

---

## ACCEPTANCE CRITERIA

- [ ] Expenses grouped by category
- [ ] Totals and percentages accurate
- [ ] Report suitable for tax filing
- [ ] Category codes match jurisdiction

---

## EXPECTED DELIVERABLES

**Files to Create:**

- Template methods in `report_generator.py`

---

## VALIDATION COMMANDS

```bash
pytest src/agentic_bookkeeper/tests/test_report_generator.py::test_expense_report -v
```

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-035 - PDF Export Implementation
