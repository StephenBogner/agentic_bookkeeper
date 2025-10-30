# Task Specification: T-033

**Task Name:** Income Statement Template
**Task ID:** T-033
**Phase:** Phase 3: Reporting Engine
**Sprint:** Sprint 6: Report Generation
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 4 hours
**Dependencies:** T-032

---

## OBJECTIVE

Create income statement template showing revenue, expenses by category, and net income calculation.

---

## REQUIREMENTS

### Functional Requirements
- Revenue section with total income
- Expense section grouped by category
- Net income calculation (revenue - expenses)
- Professional formatting
- Tax jurisdiction included
- Period comparison support (optional)

---

## ACCEPTANCE CRITERIA

- [ ] Income statement shows all revenue correctly
- [ ] Expenses categorized properly
- [ ] Net income calculation accurate
- [ ] Report professionally formatted
- [ ] Suitable for tax filing

---

## EXPECTED DELIVERABLES

**Files to Create:**
- Template methods in `report_generator.py`

---

## VALIDATION COMMANDS

```bash
pytest src/agentic_bookkeeper/tests/test_report_generator.py::test_income_statement -v
```

---

## NOTES

Standard income statement format:
- Revenue (total income)
- Cost of Goods Sold
- Operating Expenses (by category)
- Net Income

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-034 - Expense Report Template
