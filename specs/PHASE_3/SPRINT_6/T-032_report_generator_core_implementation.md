# Task Specification: T-032

**Task Name:** Report Generator Core Implementation
**Task ID:** T-032
**Phase:** Phase 3: Reporting Engine
**Sprint:** Sprint 6: Report Generation
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 4 hours
**Dependencies:** T-031

---

## OBJECTIVE

Implement core report generator with base report class, date range filtering, data aggregation, and calculation utilities.

---

## REQUIREMENTS

### Functional Requirements

- Create base report class
- Implement date range filtering logic
- Add data aggregation methods (sum, group by category)
- Create calculation utilities (totals, subtotals, percentages)
- Add currency formatting
- Implement report metadata (generated date, user info)
- Support multiple tax jurisdictions (CRA/IRS)

### Non-Functional Requirements

- Report generation must be fast (<5 seconds for 1000 transactions)
- Calculations must be accurate to 2 decimal places
- Reports must handle edge cases (zero, negative, missing data)

---

## ACCEPTANCE CRITERIA

- [ ] Report generator filters by date range accurately
- [ ] Aggregations are mathematically correct
- [ ] Calculations handle edge cases properly
- [ ] Metadata is included in all reports
- [ ] Currency formatting is consistent
- [ ] Performance meets targets
- [ ] Unit tests achieve >80% coverage

---

## EXPECTED DELIVERABLES

**Files to Create:**

- `src/agentic_bookkeeper/core/report_generator.py`

---

## VALIDATION COMMANDS

```bash
pytest src/agentic_bookkeeper/tests/test_report_generator.py -v
```

---

## IMPLEMENTATION NOTES

```python
class ReportGenerator:
    """Generate financial reports from transaction data."""

    def __init__(self, transaction_manager: TransactionManager):
        self.tm = transaction_manager

    def generate_report(self, report_type: str,
                       start_date: str, end_date: str) -> dict:
        """Generate report for date range."""
        transactions = self.tm.query_transactions(
            start_date=start_date,
            end_date=end_date
        )
        return self._process_transactions(transactions, report_type)

    def _calculate_totals(self, transactions: List[Transaction]) -> dict:
        """Calculate income, expenses, net."""
        pass

    def _group_by_category(self, transactions: List[Transaction]) -> dict:
        """Group and sum by category."""
        pass
```

---

## NOTES

- Use Decimal for accurate monetary calculations
- Support fiscal year calculations
- Include tax category codes for CRA/IRS
- Report metadata: date range, generation time, transaction count

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-033 - Income Statement Template
