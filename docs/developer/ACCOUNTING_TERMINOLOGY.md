# Accounting Terminology: Invoices vs Receipts

**Date**: 2025-10-27
**Status**: Documentation and Implementation Guide

---

## Correct Accounting Terminology

### From the Business Owner's Perspective

When managing books for a business, the document type determines the transaction type:

| Document Type | Business Issues | Business Receives | Transaction Type | Accounting Impact |
|---------------|----------------|-------------------|------------------|-------------------|
| **Invoice** | ✅ To customers | ❌ | **INCOME** | Accounts Receivable |
| **Receipt** | ❌ | ✅ From vendors | **EXPENSE** | Cash outflow |
| **Payment Record** | Either | Either | Depends | Settlement |

---

## Detailed Explanation

### Invoice = Income

**Definition**: A document the business sends to a customer requesting payment for goods/services provided.

**Characteristics**:

- **Issued BY** the business
- **Sent TO** the customer
- **Represents**: Money the business expects to receive
- **Accounting Entry**: Debit Accounts Receivable, Credit Revenue
- **Transaction Type**: **INCOME**

**Example**:

```text
Tech Consulting Inc. (Your Business)
INVOICE #12345

Bill To: StartUp Ventures Inc.
Service: Software Development
Amount: $7,250.00
```

→ This is **INCOME** for Tech Consulting Inc.

---

### Receipt = Expense

**Definition**: A document the business receives after paying for goods/services from a vendor.

**Characteristics**:

- **Issued BY** the vendor/supplier
- **Received BY** the business
- **Represents**: Money the business has spent
- **Accounting Entry**: Debit Expense, Credit Cash
- **Transaction Type**: **EXPENSE**

**Example**:

```text
Office Depot
RECEIPT

Thank you for your purchase
Items: Paper, Pens, Stapler
Total: $52.52
```

→ This is an **EXPENSE** for your business

---

## Edge Cases and Clarifications

### Sales Receipt (Business Issues)

If the business issues a receipt to a customer after receiving payment:

- **Still INCOME** (from business perspective)
- Indicates payment already received
- Confirms the transaction

### Vendor Invoice (Business Receives)

If the business receives an invoice from a vendor:

- **This is an EXPENSE** (from business perspective)
- The business owes this money
- Will be paid, generating a receipt later

---

## Implementation Rules

### For LLM Prompt

```text
IMPORTANT CLASSIFICATION RULES:
1. If document is an INVOICE that your business issued → INCOME
2. If document is a RECEIPT for purchases your business made → EXPENSE
3. Document headers typically show:
   - Invoice: "INVOICE", "Bill To", "Invoice Number"
   - Receipt: "RECEIPT", "Thank you for your purchase", "Receipt Number"
```

### For Validation Logic

```python
# Validate document_type matches transaction_type
if document_type == "invoice" and transaction_type != "income":
    warning: "Invoices should typically be income"

if document_type == "receipt" and transaction_type != "expense":
    warning: "Receipts should typically be expense"
```

---

## Current System Issues

### Problem

The current LLM prompt asks the AI to determine both:

1. `document_type`: "invoice|receipt|payment"
2. `transaction_type`: "income|expense"

But provides NO guidance on the relationship between them, leading to:

- ❌ Invoices sometimes classified as expenses
- ❌ Receipts sometimes classified as income
- ❌ Inconsistent classifications

### Test Results

From `test_llm_providers_realworld.py`:

```text
✅ invoice_software_license.pdf
   Type: expense  ← WRONG! Should be income

✅ receipt_office_supplies.pdf
   Type: expense  ← CORRECT
```

The invoice was incorrectly classified as an expense!

---

## Required Changes

### 1. Update LLM Prompt

Add explicit guidance:

```text
CRITICAL: Determine transaction type based on document type:
- If this is an INVOICE (your business bills customer) → transaction_type: "income"
- If this is a RECEIPT (your business paid vendor) → transaction_type: "expense"
- Look for these invoice indicators: "INVOICE", "Bill To", "Due Date", "Payment Terms"
- Look for these receipt indicators: "RECEIPT", "Thank you", "Payment Received", "Paid"
```

### 2. Add Validation Layer

Implement post-extraction validation:

```python
def validate_document_transaction_consistency(
    document_type: str,
    transaction_type: str
) -> tuple[bool, str]:
    """Validate that document type matches expected transaction type."""
    if document_type == "invoice" and transaction_type != "income":
        return False, "Invoices should be income transactions"
    if document_type == "receipt" and transaction_type != "expense":
        return False, "Receipts should be expense transactions"
    return True, ""
```

### 3. Add Confidence Penalty

If document type doesn't match transaction type:

- Reduce confidence score
- Flag for manual review
- Log warning for operator

---

## Testing Requirements

### Test Cases

1. **Invoice → Income** (correct)
   - invoice_consulting.pdf → income ✓
   - invoice_software_license.pdf → income ✓

2. **Receipt → Expense** (correct)
   - receipt_office_supplies.pdf → expense ✓
   - receipt_restaurant.pdf → expense ✓
   - receipt_gas.pdf → expense ✓
   - receipt_internet_phone.pdf → expense ✓

3. **Misclassification Detection**
   - Invoice marked as expense → Warning
   - Receipt marked as income → Warning

---

## User Documentation

### For End Users

```text
Understanding Your Documents:

📄 INVOICES (You sent to customers)
   • You provided goods/services
   • Customer owes you money
   • These are INCOME transactions
   • Example: Your consulting invoice to a client

🧾 RECEIPTS (You received from vendors)
   • You purchased goods/services
   • You paid money out
   • These are EXPENSE transactions
   • Example: Office supplies receipt from Staples

If the system incorrectly classifies a document, please report it
for model retraining.
```

---

## Accounting Standards Reference

### According to GAAP/IFRS

- **Revenue Recognition**: Invoices represent revenue when goods/services delivered
- **Expense Recognition**: Receipts document expenses when costs incurred
- **Matching Principle**: Match expenses with revenues in same period

### Common Business Terminology

- **AR (Accounts Receivable)**: Money customers owe (from invoices)
- **AP (Accounts Payable)**: Money business owes (from vendor invoices)
- **Cash Out**: Money paid (documented by receipts)

---

## Implementation Priority

**Priority**: 🔴 **HIGH** - Critical for correct financial reporting

**Impact**:

- ❌ Incorrect classification leads to wrong profit/loss
- ❌ Tax calculations will be wrong
- ❌ Financial statements will be inaccurate

**Effort**: Low (2-3 hours)

1. Update prompt: 30 minutes
2. Add validation: 1 hour
3. Test thoroughly: 1-2 hours

---

## Related Files

- `src/agentic_bookkeeper/llm/llm_provider.py` - Prompt definition
- `src/agentic_bookkeeper/core/document_processor.py` - Validation logic
- `test_llm_providers_realworld.py` - Testing script

---

**Status**: 🔴 Issue Identified, Fix Pending
**Created by**: Stephen Bogner, P.Eng.
**Date**: 2025-10-27
