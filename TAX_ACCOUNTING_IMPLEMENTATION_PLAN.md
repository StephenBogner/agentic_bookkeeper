# Tax Accounting & Double-Entry Implementation Plan

**Date:** 2025-10-30
**Requested By:** User
**Requirement:** Implement proper double-entry accounting with chart of accounts to handle tax tracking
**Status:** 📋 **PLANNING**

---

## Executive Summary

The current system uses a **single-entry transaction model** that doesn't properly distinguish between:
- Revenue vs. taxes collected (liability)
- Expenses vs. taxes paid (recoverable credits)
- Tax remittance payments
- Tax refunds received

The user requires **full double-entry accounting** with:
- Chart of accounts (Assets, Liabilities, Equity, Revenue, Expenses)
- Proper tax liability and credit tracking
- Multiple tax reports (cash flow, pre-tax P&L, tax remittance summary)
- GST/HST handling for Canadian jurisdiction

---

## Current State Analysis

### Current Transaction Model

**File:** `src/agentic_bookkeeper/models/transaction.py`

```python
@dataclass
class Transaction:
    date: str
    type: str  # 'income' or 'expense'
    category: str
    amount: float  # Base amount
    tax_amount: float = 0.0  # Tax portion
    # ...
```

**Problems:**
1. ❌ No distinction between tax types (collected vs paid)
2. ❌ Taxes not tracked as liabilities/assets
3. ❌ Reports exclude tax amounts entirely
4. ❌ Can't track tax remittance or refunds
5. ❌ No double-entry validation (debits = credits)

### Current Report Issues

**File:** `src/agentic_bookkeeper/core/report_generator.py:579`

```python
revenue_total = sum((Decimal(str(t.amount)) for t in income_transactions), Decimal("0.00"))
# ❌ Excludes tax_amount completely!
```

**Issues:**
- Income statement shows only `amount`, not `amount + tax_amount`
- No tax liability tracking
- No tax credit tracking
- Can't generate tax remittance reports

---

## Proper Tax Accounting Treatment

### Example: Sales Transaction with GST

**Scenario:** Invoice customer $1,000 + $130 GST (13% HST in Ontario)

**Current System (Wrong):**
```
Transaction(type='income', amount=1000, tax_amount=130)
→ Revenue: $1,000
→ Tax: Ignored
```

**Proper Double-Entry:**
```
Debit:  Accounts Receivable    $1,130
Credit: Revenue                 $1,000
Credit: GST/HST Payable          $130
```

### Example: Purchase Transaction with GST

**Scenario:** Buy supplies $500 + $65 GST

**Current System (Wrong):**
```
Transaction(type='expense', amount=500, tax_amount=65)
→ Expense: $500
→ Tax: Ignored
```

**Proper Double-Entry:**
```
Debit:  Office Supplies         $500
Debit:  GST/HST Recoverable      $65
Credit: Cash/Accounts Payable   $565
```

### Example: Tax Remittance

**Scenario:** Pay net GST to CRA (Collected $130 - Paid $65 = Remit $65)

**Current System:**
```
No way to represent this!
```

**Proper Double-Entry:**
```
Debit:  GST/HST Payable         $130
Debit:  GST/HST Recoverable      $65
Credit: Cash                     $65
```

---

## Recommended Architecture

### Phase 1: Chart of Accounts

**New File:** `src/agentic_bookkeeper/models/account.py`

```python
@dataclass
class Account:
    """Represents a general ledger account."""
    id: Optional[int]
    code: str  # e.g., "1000", "2100", "4000"
    name: str  # e.g., "Cash", "GST/HST Payable", "Revenue"
    type: str  # 'asset', 'liability', 'equity', 'revenue', 'expense'
    subtype: Optional[str]  # e.g., 'current_asset', 'tax_liability'
    parent_id: Optional[int]  # For hierarchical chart of accounts
    is_active: bool = True
    tax_treatment: Optional[str]  # 'taxable', 'exempt', 'zero_rated'
```

**Standard Chart of Accounts for Small Business:**

```
Assets (1000-1999)
├── 1000: Cash
├── 1100: Accounts Receivable
├── 1200: GST/HST Recoverable (Input Tax Credits)
└── 1500: Equipment

Liabilities (2000-2999)
├── 2000: Accounts Payable
├── 2100: GST/HST Payable (Output Tax Collected)
└── 2200: Income Tax Payable

Equity (3000-3999)
├── 3000: Owner's Equity
└── 3100: Retained Earnings

Revenue (4000-4999)
├── 4000: Professional Services Revenue
├── 4100: Consulting Revenue
└── 4200: Sales Revenue

Expenses (5000-9999)
├── 5000: Advertising
├── 5100: Office Supplies
├── 5200: Rent
└── 5900: Other Expenses
```

### Phase 2: Journal Entry Model

**New File:** `src/agentic_bookkeeper/models/journal_entry.py`

```python
@dataclass
class JournalEntry:
    """Represents a double-entry journal entry."""
    id: Optional[int]
    date: str  # YYYY-MM-DD
    description: str
    reference: Optional[str]  # Invoice #, Receipt #, etc.
    document_filename: Optional[str]
    created_at: Optional[str]
    modified_at: Optional[str]

@dataclass
class JournalLine:
    """Represents a single line (debit or credit) in a journal entry."""
    id: Optional[int]
    entry_id: int  # Foreign key to JournalEntry
    account_id: int  # Foreign key to Account
    debit: Decimal = Decimal("0.00")
    credit: Decimal = Decimal("0.00")
    description: Optional[str]

    def validate(self):
        """Ensure either debit OR credit is set, not both."""
        if self.debit > 0 and self.credit > 0:
            raise ValueError("Line cannot have both debit and credit")
        if self.debit < 0 or self.credit < 0:
            raise ValueError("Amounts must be >= 0")
```

**Validation Rules:**
- Each journal entry must have at least 2 lines (minimum one debit, one credit)
- Total debits must equal total credits
- Each line has either debit OR credit, never both
- All amounts must be non-negative

### Phase 3: Transaction Migration

**Strategy:** Keep existing Transaction model for backward compatibility, but internally convert to journal entries.

**New File:** `src/agentic_bookkeeper/core/transaction_converter.py`

```python
class TransactionConverter:
    """Convert single-entry transactions to double-entry journal entries."""

    def transaction_to_journal_entry(self, transaction: Transaction) -> JournalEntry:
        """
        Convert a Transaction to a JournalEntry with proper debits/credits.

        For income transactions:
            Debit:  Cash/AR (amount + tax_amount)
            Credit: Revenue (amount)
            Credit: GST/HST Payable (tax_amount)

        For expense transactions:
            Debit:  Expense Category (amount)
            Debit:  GST/HST Recoverable (tax_amount)
            Credit: Cash/AP (amount + tax_amount)
        """
        # Implementation details...
```

### Phase 4: Enhanced Reporting

**File:** `src/agentic_bookkeeper/core/report_generator.py` (enhancements)

**New Reports:**

1. **Income Statement (P&L) - Excludes Taxes**
   ```
   Revenue
     Professional Services      $10,000
     Consulting Revenue         $15,000
   Total Revenue               $25,000

   Expenses
     Office Supplies            $1,000
     Rent                       $2,000
   Total Expenses              $3,000

   Net Income                  $22,000

   Note: Excludes GST/HST (reported separately below)
   ```

2. **Tax Summary Report**
   ```
   GST/HST Summary (Period: 2025-01-01 to 2025-03-31)

   Output Tax (Collected):
     Sales transactions            $3,250

   Input Tax Credits (Paid):
     Office supplies                 $130
     Rent                           $260
   Total ITCs                      $390

   Net Tax Payable                $2,860

   Remittances Made:
     2025-01-31                    $800
     2025-02-28                    $900
   Total Remitted                 $1,700

   Outstanding Balance            $1,160
   ```

3. **Cash Flow Statement**
   ```
   Operating Activities:
     Collections from customers   $28,250  (includes tax)
     Payments to suppliers        ($3,890) (includes tax)
     Tax remittance to CRA        ($1,700)
   Net Cash from Operations       $22,660
   ```

4. **General Ledger Report**
   ```
   Account: 2100 - GST/HST Payable

   Date       Description          Debit    Credit   Balance
   2025-01-15 Invoice #001                   $130     $130 CR
   2025-01-20 Invoice #002                   $195     $325 CR
   2025-01-31 GST Remittance        $325              $0
   ```

---

## Database Schema Changes

### New Tables

**accounts table:**
```sql
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('asset', 'liability', 'equity', 'revenue', 'expense')),
    subtype TEXT,
    parent_id INTEGER,
    is_active BOOLEAN DEFAULT 1,
    tax_treatment TEXT,
    created_at TEXT,
    modified_at TEXT,
    FOREIGN KEY (parent_id) REFERENCES accounts(id)
);
```

**journal_entries table:**
```sql
CREATE TABLE journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    reference TEXT,
    document_filename TEXT,
    created_at TEXT,
    modified_at TEXT
);
```

**journal_lines table:**
```sql
CREATE TABLE journal_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    debit REAL DEFAULT 0.00,
    credit REAL DEFAULT 0.00,
    description TEXT,
    FOREIGN KEY (entry_id) REFERENCES journal_entries(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    CHECK ((debit = 0 AND credit >= 0) OR (credit = 0 AND debit >= 0)),
    CHECK (NOT (debit > 0 AND credit > 0))
);
```

**Migration Strategy:**
- Keep existing `transactions` table for backward compatibility
- Add new tables for double-entry
- Create view that exposes journal entries as transactions for legacy code
- Gradually migrate UI to use journal entry model

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Create Account model
- [ ] Create JournalEntry and JournalLine models
- [ ] Create database schema and migrations
- [ ] Implement chart of accounts initialization
- [ ] Write unit tests for new models

**Deliverables:**
- `models/account.py`
- `models/journal_entry.py`
- `models/database.py` (enhanced)
- Database migration script
- Unit tests

### Phase 2: Core Functionality (Week 2)
- [ ] Implement TransactionConverter (Transaction → JournalEntry)
- [ ] Create AccountManager (CRUD for accounts)
- [ ] Create JournalEntryManager (CRUD for journal entries)
- [ ] Implement validation (debits = credits)
- [ ] Write integration tests

**Deliverables:**
- `core/transaction_converter.py`
- `core/account_manager.py`
- `core/journal_entry_manager.py`
- Integration tests

### Phase 3: Enhanced Reporting (Week 3)
- [ ] Update ReportGenerator to use journal entries
- [ ] Implement Income Statement (excluding taxes)
- [ ] Implement Tax Summary Report
- [ ] Implement Cash Flow Statement
- [ ] Implement General Ledger Report
- [ ] Implement Trial Balance
- [ ] Write report tests

**Deliverables:**
- Enhanced `core/report_generator.py`
- New report templates
- Report unit tests

### Phase 4: GUI Updates (Week 4)
- [ ] Add Chart of Accounts management screen
- [ ] Update transaction entry to create journal entries
- [ ] Add journal entry viewer
- [ ] Update reports widget with new reports
- [ ] Add tax dashboard widget
- [ ] GUI integration tests

**Deliverables:**
- `gui/accounts_widget.py`
- `gui/journal_entry_dialog.py`
- Updated `gui/reports_widget.py`
- `gui/tax_dashboard_widget.py`
- GUI tests

### Phase 5: Migration & Polish (Week 5)
- [ ] Create migration tool (old transactions → journal entries)
- [ ] Implement backward compatibility layer
- [ ] Update documentation
- [ ] End-to-end testing
- [ ] Performance optimization

**Deliverables:**
- Migration utility
- Updated user guide
- Performance benchmarks
- E2E tests

---

## Backward Compatibility Strategy

### Option 1: Dual Models (Recommended)

Keep existing Transaction model, add JournalEntry model:

```python
class TransactionManager:
    def create_transaction(self, transaction: Transaction) -> int:
        """
        Create transaction (legacy API).
        Internally converts to journal entry.
        """
        # Convert to journal entry
        converter = TransactionConverter(self.account_manager)
        journal_entry = converter.transaction_to_journal_entry(transaction)

        # Save journal entry
        entry_id = self.journal_entry_manager.create_entry(journal_entry)

        # Save original transaction for backward compatibility
        transaction_id = self._save_transaction_legacy(transaction)

        return transaction_id
```

**Benefits:**
- Existing code continues to work
- New code uses proper accounting
- Gradual migration path
- Both views available during transition

### Option 2: View-Based Abstraction

Create database view that presents journal entries as transactions:

```sql
CREATE VIEW transactions_view AS
SELECT
    je.id,
    je.date,
    CASE
        WHEN revenue_line.credit > 0 THEN 'income'
        ELSE 'expense'
    END as type,
    -- ... map to transaction fields
FROM journal_entries je
JOIN journal_lines revenue_line ON ...
-- Complex join to reconstruct transaction view
```

**Benefits:**
- No data duplication
- Single source of truth
- Automatic sync between models

**Drawbacks:**
- Complex view logic
- Potential performance issues

---

## Tax Reporting Specifics

### Canadian GST/HST Handling

**Account Setup:**
```
1200: GST/HST Recoverable (Asset)
2100: GST/HST Payable (Liability)
```

**Transaction Examples:**

**1. Invoice with 13% HST (Ontario):**
```
Debit:  1100 Accounts Receivable  $1,130
Credit: 4000 Revenue               $1,000
Credit: 2100 GST/HST Payable        $130
```

**2. Expense with 13% HST:**
```
Debit:  5100 Office Supplies        $500
Debit:  1200 GST/HST Recoverable     $65
Credit: 1000 Cash                   $565
```

**3. GST Remittance:**
```
Debit:  2100 GST/HST Payable        $130
Credit: 1200 GST/HST Recoverable     $65
Credit: 1000 Cash                    $65
```

**GST Return Calculation:**
```python
def calculate_gst_return(start_date: str, end_date: str) -> Dict:
    """
    Calculate GST/HST return for filing.

    Returns:
        {
            'output_tax': Decimal,      # Total collected
            'input_credits': Decimal,   # Total paid (recoverable)
            'net_tax': Decimal,         # Amount to remit/refund
            'remittances': Decimal,     # Already remitted
            'balance': Decimal          # Outstanding balance
        }
    """
    # Query account 2100 for credits (collected)
    output_tax = sum_credits_for_account('2100', start_date, end_date)

    # Query account 1200 for debits (paid)
    input_credits = sum_debits_for_account('1200', start_date, end_date)

    # Calculate net
    net_tax = output_tax - input_credits

    # Check for remittances (debits to 2100)
    remittances = sum_debits_for_account('2100', start_date, end_date)

    # Outstanding balance
    balance = net_tax - remittances

    return {...}
```

---

## Risk Analysis

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Data migration failures | High | Medium | Extensive testing, backup/rollback procedures |
| Performance degradation | Medium | Low | Optimize queries, add indexes, benchmark |
| Backward compatibility breaks | High | Medium | Maintain dual models, comprehensive tests |
| Complex journal entry UI | Medium | High | Provide templates, validation, good UX |
| User confusion | High | Medium | Excellent documentation, training, examples |

### Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Incorrect tax calculations | High | Medium | Extensive testing, CPA review of logic |
| Regulatory non-compliance | High | Low | Follow CRA guidelines, professional review |
| User adoption resistance | Medium | High | Gradual rollout, maintain legacy mode |

---

## Next Steps

### Immediate Actions (This Week)

1. **Review & Approve Plan**
   - Review this document
   - Get feedback from stakeholders
   - Approve scope and timeline

2. **Create Detailed Specs**
   - Create detailed spec for Phase 1 (Foundation)
   - Define exact database schema
   - Define exact API contracts

3. **Set Up Development**
   - Create feature branch: `feature/double-entry-accounting`
   - Set up test fixtures for accounting
   - Create sample chart of accounts

### Phase 1 Kickoff (Next Week)

1. **Implement Account Model**
   - Create `models/account.py`
   - Create database migration
   - Initialize default chart of accounts

2. **Implement Journal Entry Model**
   - Create `models/journal_entry.py`
   - Implement validation logic
   - Write comprehensive tests

3. **Database Migration**
   - Create migration script
   - Add new tables
   - Create indexes
   - Test rollback procedures

---

## Questions for Stakeholders

1. **GST Registration Status:**
   - Are you currently GST/HST registered?
   - If not, when do you expect to exceed the $30,000 threshold?
   - Do you want to track GST anyway for when you register?

2. **Account Structure:**
   - Do you need additional expense categories beyond current list?
   - Any specific accounts for your business type?
   - Need to track multiple bank accounts?

3. **Migration:**
   - Do you have existing transactions that need migrating?
   - How far back does your data go?
   - Acceptable downtime for migration?

4. **Reporting:**
   - What accounting period do you use (calendar year, fiscal year)?
   - How often do you need tax reports (monthly, quarterly, annually)?
   - Need integration with accounting software (QuickBooks, Xero)?

5. **Complexity:**
   - Comfortable with double-entry concepts (debits/credits)?
   - Need simplified "single-entry mode" option?
   - Want automatic journal entry creation or manual control?

---

## Estimated Timeline

**Phase 1 (Foundation):** 1 week
**Phase 2 (Core Functionality):** 1 week
**Phase 3 (Enhanced Reporting):** 1 week
**Phase 4 (GUI Updates):** 1 week
**Phase 5 (Migration & Polish):** 1 week

**Total:** 5 weeks for complete implementation

**Alternative - MVP (Minimum Viable Product):**
- Phases 1-2 only: 2 weeks
- Provides basic double-entry and tax tracking
- Reports and full GUI come later

---

## Success Criteria

### Technical
- ✅ All journal entries balance (debits = credits)
- ✅ Tax accounts (payable/recoverable) track correctly
- ✅ Reports show accurate pre-tax amounts
- ✅ Tax summary report matches manual calculation
- ✅ No data loss during migration
- ✅ Performance acceptable (< 1 sec for reports)

### Functional
- ✅ Can record income with GST collected
- ✅ Can record expenses with GST paid
- ✅ Can record tax remittances
- ✅ Can generate tax summary for filing
- ✅ Income statement excludes tax amounts
- ✅ Cash flow includes all tax movements

### User Experience
- ✅ Transaction entry remains simple
- ✅ Reports are clear and understandable
- ✅ No regression in existing functionality
- ✅ Documentation complete and helpful

---

**Status:** 📋 **AWAITING APPROVAL**

**Next Action:** Review plan and decide on:
1. Full 5-week implementation vs. MVP 2-week approach
2. Chart of accounts structure
3. Migration strategy
4. Timeline and priorities

---

**Document Created:** 2025-10-30
**Author:** Claude (AI Assistant)
**Review Required:** Stephen Bogner
