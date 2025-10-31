# Simple Tax Reporting Enhancement

**Date:** 2025-10-30
**Scope:** Cash-basis tax reporting for lightweight bookkeeping
**Status:** 📋 **PLANNING**

---

## Product Vision Alignment

**Original Vision:**
> Drop paid invoices (income) and paid receipts (expenses) into a directory, and Agentic Bookkeeper sorts it out.

**Target Users:**
- Small business owners / freelancers
- Below or near GST registration threshold ($30k in Canada)
- Using separate billing/payment systems (QuickBooks, Wave, FreshBooks, etc.)
- Need simple tax reporting for filing purposes

**Out of Scope (handled by other systems):**
- Invoice generation
- Purchase order generation
- Payment tracking (A/R, A/P)
- Receipt generation
- Double-entry bookkeeping
- Chart of accounts

**In Scope (this application):**
- Automatic transaction extraction from documents
- Cash-basis income and expense tracking
- Tax amount tracking (collected and paid)
- Simple tax summary for filing

---

## Current State Analysis

### Problem 1: Tax Amounts Excluded from Reports

**File:** `src/agentic_bookkeeper/core/report_generator.py:579, 583`

```python
# WRONG - Excludes tax amounts
revenue_total = sum((Decimal(str(t.amount)) for t in income_transactions), Decimal("0.00"))
expense_total = sum((Decimal(str(t.amount)) for t in expense_transactions), Decimal("0.00"))
```

**Impact:**
- Income statement shows $1,000 revenue when actual cash received was $1,130 ($1,000 + $130 GST)
- Expense report shows $500 when actual cash paid was $565 ($500 + $65 GST)
- Cash flow doesn't match bank account
- Can't reconcile with bank statements

### Problem 2: No Tax Summary Report

**Current Reports:**
1. ✅ Income Statement (but excluding tax)
2. ✅ Expense Report (but excluding tax)
3. ❌ Tax Summary Report (doesn't exist)

**User Need:**
> "I need a report that tells me how much tax I collected and how much tax I paid."

For GST/HST filing or tax return preparation.

### Problem 3: Ambiguous "Amount" Field

**Transaction Model:** `transaction.py:42-45`

```python
amount: float  # Base amount before tax
tax_amount: float = 0.0  # Tax portion
```

**Questions:**
- What is "total cash flow" for this transaction?
- Currently: `amount + tax_amount`
- Should we have a dedicated `total_amount` field?
- Or always calculate it?

---

## Proposed Simple Solution

### Enhancement 1: Fix Income/Expense Reports to Include Tax

**Cash-Basis Reporting:**

When a user drops a paid receipt for $565 ($500 + $65 GST), they paid **$565 cash**. The report should show:

**Option A: Show Both (Recommended)**
```
INCOME STATEMENT (Cash Basis)
Period: 2025-01-01 to 2025-12-31

REVENUE
Category                    Amount      Tax         Total
Consulting Revenue          $10,000     $1,300      $11,300
Sales Revenue               $5,000      $650        $5,650
                            -------     ------      -------
Total Revenue               $15,000     $1,950      $16,950

EXPENSES
Category                    Amount      Tax         Total
Office Supplies             $500        $65         $565
Rent                        $2,000      $260        $2,260
Advertising                 $1,000      $130        $1,130
                            -------     ------      -------
Total Expenses              $3,500      $455        $3,955

NET INCOME
Pre-tax Net Income:         $11,500
Tax Net Position:           $1,495 (collected - paid)
Cash Net Income:            $12,995
```

**Option B: Show Total Only (Simpler)**
```
INCOME STATEMENT (Cash Basis)
Period: 2025-01-01 to 2025-12-31

REVENUE
Consulting Revenue          $11,300
Sales Revenue               $5,650
                            -------
Total Revenue               $16,950

EXPENSES
Office Supplies             $565
Rent                        $2,260
Advertising                 $1,130
                            -------
Total Expenses              $3,955

NET INCOME                  $12,995

Note: Amounts include applicable taxes (GST/HST)
```

**Recommendation:** Option A - shows both pre-tax and total, giving users complete picture.

### Enhancement 2: Add Tax Summary Report

**New Report Type:** Tax Summary

```
TAX SUMMARY REPORT
Period: 2025-01-01 to 2025-12-31
Jurisdiction: Canada (GST/HST)

TAX COLLECTED (Output Tax)
Date        Description                     Amount      Tax Type
2025-01-15  Invoice - ABC Corp             $1,300      GST (13%)
2025-02-10  Invoice - XYZ Ltd              $650        GST (13%)
                                            ------
Total Tax Collected                        $1,950

TAX PAID (Input Tax Credits)
Date        Description                     Amount      Tax Type
2025-01-20  Office Supplies                $65         GST (13%)
2025-02-01  Rent Payment                   $260        GST (13%)
2025-03-15  Advertising                    $130        GST (13%)
                                            ------
Total Tax Paid                             $455

NET TAX POSITION
Tax Collected                              $1,950
Tax Paid (ITCs)                            ($455)
                                            ------
Net Tax Payable                            $1,495

Notes:
- This is an informational summary only
- Consult with tax professional for actual filing
- Keep original receipts/invoices for CRA audit
```

### Enhancement 3: Add Total Amount Helper

**File:** `src/agentic_bookkeeper/models/transaction.py`

```python
def get_total_amount(self) -> float:
    """
    Get total cash amount (amount + tax).

    This represents the actual cash flow for this transaction.
    For income: total cash received
    For expense: total cash paid

    Returns:
        Amount + tax_amount
    """
    return round(self.amount + self.tax_amount, 2)
```

**Already exists!** `get_total_with_tax()` at line 245

Just need to **use it** in reports.

---

## Implementation Plan

### Phase 1: Fix Existing Reports (1-2 hours)

**File:** `src/agentic_bookkeeper/core/report_generator.py`

**Changes:**

1. **Update `generate_income_statement()` to include tax:**

```python
def generate_income_statement(self, start_date: str, end_date: str, **kwargs: Any) -> Dict[str, Any]:
    # ... existing code ...

    # Calculate revenue section WITH TAX
    revenue_total = sum((Decimal(str(t.amount)) for t in income_transactions), Decimal("0.00"))
    revenue_tax_total = sum((Decimal(str(t.tax_amount)) for t in income_transactions), Decimal("0.00"))
    revenue_cash_total = revenue_total + revenue_tax_total

    # Calculate expense section WITH TAX
    expense_total = sum((Decimal(str(t.amount)) for t in expense_transactions), Decimal("0.00"))
    expense_tax_total = sum((Decimal(str(t.tax_amount)) for t in expense_transactions), Decimal("0.00"))
    expense_cash_total = expense_total + expense_tax_total

    # Calculate net income (multiple views)
    net_income_pretax = revenue_total - expense_total
    net_income_cash = revenue_cash_total - expense_cash_total
    net_tax_position = revenue_tax_total - expense_tax_total

    # Build the income statement
    income_statement = {
        "report_type": "income_statement",
        "metadata": metadata,
        "revenue": {
            "total": revenue_total,
            "total_formatted": self.format_currency(revenue_total),
            "tax_total": revenue_tax_total,
            "tax_total_formatted": self.format_currency(revenue_tax_total),
            "cash_total": revenue_cash_total,
            "cash_total_formatted": self.format_currency(revenue_cash_total),
            "categories": revenue_by_category,
        },
        "expenses": {
            "total": expense_total,
            "total_formatted": self.format_currency(expense_total),
            "tax_total": expense_tax_total,
            "tax_total_formatted": self.format_currency(expense_tax_total),
            "cash_total": expense_cash_total,
            "cash_total_formatted": self.format_currency(expense_cash_total),
            "categories": expenses_by_category,
        },
        "net_income": {
            "pretax_amount": net_income_pretax,
            "pretax_amount_formatted": self.format_currency(net_income_pretax),
            "cash_amount": net_income_cash,
            "cash_amount_formatted": self.format_currency(net_income_cash),
            "tax_position": net_tax_position,
            "tax_position_formatted": self.format_currency(net_tax_position),
        }
    }
```

2. **Update `group_by_category()` to include tax:**

```python
def group_by_category(self, transactions: List[Transaction], transaction_type: str) -> Dict[str, Any]:
    # ... existing grouping logic ...

    for category, txns in grouped.items():
        total = sum((Decimal(str(t.amount)) for t in txns), Decimal("0.00"))
        tax_total = sum((Decimal(str(t.tax_amount)) for t in txns), Decimal("0.00"))
        cash_total = total + tax_total

        result[category] = {
            "total": total,
            "total_formatted": self.format_currency(total),
            "tax_total": tax_total,
            "tax_total_formatted": self.format_currency(tax_total),
            "cash_total": cash_total,
            "cash_total_formatted": self.format_currency(cash_total),
            "count": len(txns),
            "percentage_formatted": f"{percentage:.1f}%",
            # ... rest ...
        }
```

### Phase 2: Add Tax Summary Report (2-3 hours)

**File:** `src/agentic_bookkeeper/core/report_generator.py`

**New Method:**

```python
def generate_tax_summary(self, start_date: str, end_date: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Generate a tax summary report showing taxes collected and paid.

    This report helps users prepare their GST/HST return or tax filing.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        **kwargs: Additional options

    Returns:
        Dictionary with tax summary structure:
        {
            'report_type': 'tax_summary',
            'metadata': {...},
            'tax_collected': {
                'transactions': [...],
                'total': Decimal,
                'total_formatted': str
            },
            'tax_paid': {
                'transactions': [...],
                'total': Decimal,
                'total_formatted': str
            },
            'net_position': {
                'amount': Decimal,
                'amount_formatted': str,
                'payable': bool  # True if owe tax, False if refund
            }
        }
    """
    logger.info(f"Generating tax summary: {start_date} to {end_date}")

    # Validate date range
    self._validate_date_range(start_date, end_date)

    # Get all transactions
    all_transactions = self.filter_by_date_range(start_date=start_date, end_date=end_date)

    # Separate income and expense
    income_transactions = [t for t in all_transactions if t.is_income()]
    expense_transactions = [t for t in all_transactions if t.is_expense()]

    # Calculate tax collected (on income)
    tax_collected_total = sum(
        (Decimal(str(t.tax_amount)) for t in income_transactions),
        Decimal("0.00")
    )

    # Build detailed list of tax collected
    tax_collected_details = [
        {
            "date": t.date,
            "description": t.description or t.category,
            "vendor_customer": t.vendor_customer,
            "amount": Decimal(str(t.tax_amount)),
            "amount_formatted": self.format_currency(Decimal(str(t.tax_amount))),
            "document": t.document_filename,
        }
        for t in income_transactions if t.tax_amount > 0
    ]

    # Calculate tax paid (on expenses)
    tax_paid_total = sum(
        (Decimal(str(t.tax_amount)) for t in expense_transactions),
        Decimal("0.00")
    )

    # Build detailed list of tax paid
    tax_paid_details = [
        {
            "date": t.date,
            "description": t.description or t.category,
            "vendor_customer": t.vendor_customer,
            "amount": Decimal(str(t.tax_amount)),
            "amount_formatted": self.format_currency(Decimal(str(t.tax_amount))),
            "document": t.document_filename,
        }
        for t in expense_transactions if t.tax_amount > 0
    ]

    # Calculate net position
    net_position = tax_collected_total - tax_paid_total

    # Generate metadata
    metadata = self.generate_metadata(
        start_date=start_date,
        end_date=end_date,
        transaction_count=len([t for t in all_transactions if t.tax_amount > 0])
    )
    metadata["report_type"] = "tax_summary"

    # Build tax summary
    tax_summary = {
        "report_type": "tax_summary",
        "metadata": metadata,
        "tax_collected": {
            "transactions": tax_collected_details,
            "total": tax_collected_total,
            "total_formatted": self.format_currency(tax_collected_total),
            "count": len(tax_collected_details),
        },
        "tax_paid": {
            "transactions": tax_paid_details,
            "total": tax_paid_total,
            "total_formatted": self.format_currency(tax_paid_total),
            "count": len(tax_paid_details),
        },
        "net_position": {
            "amount": net_position,
            "amount_formatted": self.format_currency(net_position),
            "payable": net_position > 0,  # True = owe money, False = refund due
        }
    }

    logger.info(
        f"Tax summary generated: Collected={tax_collected_total}, "
        f"Paid={tax_paid_total}, Net={net_position}"
    )

    return tax_summary
```

### Phase 3: Update GUI (2 hours)

**File:** `src/agentic_bookkeeper/gui/reports_widget.py`

**Changes:**

1. **Add "Tax Summary" to report type dropdown:**

```python
self.report_type_combo.addItems([
    "Income Statement",
    "Expense Report",
    "Tax Summary"  # NEW
])
```

2. **Update preview display to handle tax amounts:**

```python
def _display_preview(self, report_data: Dict[str, Any]) -> None:
    # ... existing code ...

    # Handle income statement with tax
    if "revenue" in report_data:
        revenue = report_data.get("revenue", {})
        expenses = report_data.get("expenses", {})
        net_income = report_data.get("net_income", {})

        # Summary section with tax breakdown
        preview_text.append("SUMMARY (Cash Basis)")
        preview_text.append("-" * 60)
        preview_text.append(f"Total Income:    {revenue.get('cash_total_formatted', '$0.00')}")
        preview_text.append(f"  (Pre-tax:      {revenue.get('total_formatted', '$0.00')})")
        preview_text.append(f"  (Tax:          {revenue.get('tax_total_formatted', '$0.00')})")
        preview_text.append("")
        preview_text.append(f"Total Expenses:  {expenses.get('cash_total_formatted', '$0.00')}")
        preview_text.append(f"  (Pre-tax:      {expenses.get('total_formatted', '$0.00')})")
        preview_text.append(f"  (Tax:          {expenses.get('tax_total_formatted', '$0.00')})")
        preview_text.append("")
        preview_text.append(f"Net Income:      {net_income.get('cash_amount_formatted', '$0.00')}")
        preview_text.append(f"  (Pre-tax:      {net_income.get('pretax_amount_formatted', '$0.00')})")
        preview_text.append(f"  (Tax position: {net_income.get('tax_position_formatted', '$0.00')})")

    # Handle tax summary report
    elif report_data.get("report_type") == "tax_summary":
        tax_collected = report_data.get("tax_collected", {})
        tax_paid = report_data.get("tax_paid", {})
        net_position = report_data.get("net_position", {})

        preview_text.append("TAX COLLECTED (Output Tax)")
        preview_text.append("-" * 60)
        for txn in tax_collected.get("transactions", []):
            preview_text.append(
                f"{txn['date']}  {txn['description']:30s}  {txn['amount_formatted']:>12s}"
            )
        preview_text.append("-" * 60)
        preview_text.append(f"Total Tax Collected: {tax_collected.get('total_formatted', '$0.00')}")
        preview_text.append("")

        preview_text.append("TAX PAID (Input Tax Credits)")
        preview_text.append("-" * 60)
        for txn in tax_paid.get("transactions", []):
            preview_text.append(
                f"{txn['date']}  {txn['description']:30s}  {txn['amount_formatted']:>12s}"
            )
        preview_text.append("-" * 60)
        preview_text.append(f"Total Tax Paid: {tax_paid.get('total_formatted', '$0.00')}")
        preview_text.append("")

        preview_text.append("NET TAX POSITION")
        preview_text.append("-" * 60)
        payable = net_position.get("payable", True)
        status = "PAYABLE" if payable else "REFUNDABLE"
        preview_text.append(f"Net Amount {status}: {net_position.get('amount_formatted', '$0.00')}")
```

3. **Update report generation call:**

```python
def _on_generate_preview(self) -> None:
    # ... existing code ...

    # Generate report
    if report_type == "Income Statement":
        report_data = self.report_generator.generate_income_statement(start_date_str, end_date_str)
    elif report_type == "Expense Report":
        report_data = self.report_generator.generate_expense_report(start_date_str, end_date_str)
    elif report_type == "Tax Summary":
        report_data = self.report_generator.generate_tax_summary(start_date_str, end_date_str)
```

### Phase 4: Update Exporters (1 hour)

**Files:**
- `src/agentic_bookkeeper/core/exporters/pdf_exporter.py`
- `src/agentic_bookkeeper/core/exporters/csv_exporter.py`

**Changes:** Support exporting tax summary report format.

---

## Testing Plan

### Unit Tests

**New Test File:** `tests/test_tax_reporting.py`

```python
def test_income_statement_includes_tax():
    """Test that income statement includes tax amounts."""
    # Create transactions with tax
    transactions = [
        Transaction(date="2025-01-01", type="income", category="Consulting Revenue",
                   amount=1000.00, tax_amount=130.00),
        Transaction(date="2025-01-01", type="expense", category="Office Supplies",
                   amount=500.00, tax_amount=65.00),
    ]

    report = report_generator.generate_income_statement("2025-01-01", "2025-12-31")

    assert report["revenue"]["total"] == Decimal("1000.00")
    assert report["revenue"]["tax_total"] == Decimal("130.00")
    assert report["revenue"]["cash_total"] == Decimal("1130.00")

    assert report["expenses"]["total"] == Decimal("500.00")
    assert report["expenses"]["tax_total"] == Decimal("65.00")
    assert report["expenses"]["cash_total"] == Decimal("565.00")

    assert report["net_income"]["pretax_amount"] == Decimal("500.00")
    assert report["net_income"]["cash_amount"] == Decimal("565.00")
    assert report["net_income"]["tax_position"] == Decimal("65.00")


def test_tax_summary_report():
    """Test tax summary report generation."""
    # Create transactions
    transactions = [
        # Income with tax collected
        Transaction(date="2025-01-15", type="income", category="Consulting Revenue",
                   amount=1000.00, tax_amount=130.00, vendor_customer="ABC Corp"),
        Transaction(date="2025-02-10", type="income", category="Sales Revenue",
                   amount=500.00, tax_amount=65.00, vendor_customer="XYZ Ltd"),

        # Expenses with tax paid
        Transaction(date="2025-01-20", type="expense", category="Office Supplies",
                   amount=100.00, tax_amount=13.00),
        Transaction(date="2025-02-01", type="expense", category="Rent",
                   amount=2000.00, tax_amount=260.00),
    ]

    report = report_generator.generate_tax_summary("2025-01-01", "2025-12-31")

    # Check tax collected
    assert report["tax_collected"]["total"] == Decimal("195.00")  # 130 + 65
    assert report["tax_collected"]["count"] == 2

    # Check tax paid
    assert report["tax_paid"]["total"] == Decimal("273.00")  # 13 + 260
    assert report["tax_paid"]["count"] == 2

    # Check net position
    assert report["net_position"]["amount"] == Decimal("-78.00")  # 195 - 273
    assert report["net_position"]["payable"] == False  # Negative = refund


def test_zero_tax_transactions_excluded():
    """Test that transactions with zero tax are excluded from tax summary."""
    transactions = [
        Transaction(date="2025-01-01", type="income", category="Interest Income",
                   amount=100.00, tax_amount=0.00),  # No tax
    ]

    report = report_generator.generate_tax_summary("2025-01-01", "2025-12-31")

    assert report["tax_collected"]["count"] == 0
    assert report["tax_collected"]["total"] == Decimal("0.00")
```

### Integration Tests

1. **Drop receipt with tax → Extract → Generate tax summary**
2. **Drop multiple documents → Verify cash totals match bank**
3. **Export tax summary to PDF**

---

## Timeline

**Phase 1:** Fix existing reports (2 hours)
**Phase 2:** Add tax summary report (3 hours)
**Phase 3:** Update GUI (2 hours)
**Phase 4:** Update exporters (1 hour)
**Testing:** (2 hours)

**Total:** 10 hours (1-2 days of work)

---

## Success Criteria

### Functional
- ✅ Income statement shows cash totals (including tax)
- ✅ Expense report shows cash totals (including tax)
- ✅ Tax summary report available in GUI
- ✅ Tax summary shows collected vs paid
- ✅ Cash totals reconcile with bank statements

### User Experience
- ✅ Reports clearly label "Cash Basis" vs "Pre-tax"
- ✅ Tax summary is easy to understand
- ✅ Users can copy numbers directly for tax filing
- ✅ No breaking changes to existing workflow

### Technical
- ✅ All tests pass
- ✅ Reports export correctly to PDF/CSV
- ✅ No performance degradation
- ✅ Backward compatible with existing data

---

## Documentation Updates

**User Guide:** Add section on tax reporting

```markdown
## Tax Reporting

Agentic Bookkeeper automatically tracks taxes on your transactions.

### Cash-Basis Accounting

All reports use **cash-basis** accounting, meaning amounts are recorded
when money actually changes hands (when you receive payment or make payment),
not when you issue an invoice or receive a bill.

### Tax Amounts

When you drop a receipt for $565 ($500 + $65 GST), the system:
- Records base amount: $500
- Records tax amount: $65
- Shows cash total: $565

### Income Statement

Shows three views of your financial position:
- **Pre-tax amounts:** Revenue and expenses before tax
- **Tax amounts:** Tax collected and tax paid
- **Cash amounts:** Actual money in/out (pre-tax + tax)

### Tax Summary Report

Use this report when filing GST/HST returns or tax returns:
- **Tax Collected:** Tax you collected from customers (output tax)
- **Tax Paid:** Tax you paid on expenses (input tax credits)
- **Net Position:** Amount payable to (or refundable from) government

**Important:** This report is for informational purposes. Consult
with a tax professional or accountant for actual tax filing.
```

---

## Comparison: Simple vs Double-Entry

| Feature | Simple (This Plan) | Double-Entry (Previous Plan) |
|---------|-------------------|------------------------------|
| **Complexity** | Low | High |
| **User Learning Curve** | Minutes | Days/Weeks |
| **Implementation Time** | 10 hours | 200 hours |
| **Chart of Accounts** | No | Yes |
| **Journal Entries** | No | Yes |
| **Debits/Credits** | No | Yes |
| **A/R, A/P Tracking** | No | Yes |
| **Cash-Basis Reports** | Yes | Yes |
| **Tax Summary** | Yes | Yes |
| **Audit Trail** | Simple | Complete |
| **Target User** | Small business/freelancer | Accountants/CPAs |
| **Product Vision** | Aligned ✅ | Misaligned ❌ |

---

**Status:** 📋 **READY FOR IMPLEMENTATION**

**Recommendation:** Proceed with this simple plan. It delivers exactly what users need without overcomplicating the product.

**Next Steps:**
1. Approve this plan
2. Implement Phase 1 (fix existing reports)
3. Test with real data
4. Implement Phase 2 (tax summary)
5. Test and deploy

---

**Document Created:** 2025-10-30
**Estimated Effort:** 10 hours
**Aligns with Product Vision:** ✅ Yes
