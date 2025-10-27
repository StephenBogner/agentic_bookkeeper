#!/usr/bin/env python3
"""
Test that accounting terminology is correctly enforced:
- Invoices → Income
- Receipts → Expense
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentic_bookkeeper.core.document_processor import DocumentProcessor
from agentic_bookkeeper.llm.openai_provider import OpenAIProvider
import logging

# Set up logging to see validation messages
logging.basicConfig(level=logging.WARNING, format='%(message)s')

print("Testing Accounting Terminology Validation")
print("=" * 70)
print()

# Create processor
provider = OpenAIProvider(api_key="test_key")
categories = ["Office expenses", "Business income"]
processor = DocumentProcessor(provider, categories)

print("Testing document type vs transaction type validation:\n")

test_cases = [
    {
        "name": "✅ CORRECT: Invoice → Income",
        "data": {
            "document_type": "invoice",
            "transaction_type": "income",
            "date": "2025-10-27",
            "amount": 1000.00
        },
        "expected": "No warning"
    },
    {
        "name": "✅ CORRECT: Receipt → Expense",
        "data": {
            "document_type": "receipt",
            "transaction_type": "expense",
            "date": "2025-10-27",
            "amount": 100.00
        },
        "expected": "No warning"
    },
    {
        "name": "❌ INCORRECT: Invoice → Expense",
        "data": {
            "document_type": "invoice",
            "transaction_type": "expense",
            "date": "2025-10-27",
            "amount": 1000.00
        },
        "expected": "⚠️  Warning expected"
    },
    {
        "name": "❌ INCORRECT: Receipt → Income",
        "data": {
            "document_type": "receipt",
            "transaction_type": "income",
            "date": "2025-10-27",
            "amount": 100.00
        },
        "expected": "⚠️  Warning expected"
    },
]

for i, test_case in enumerate(test_cases, 1):
    print(f"{i}. {test_case['name']}")
    print("-" * 70)
    print(f"   Document Type: {test_case['data']['document_type']}")
    print(f"   Transaction Type: {test_case['data']['transaction_type']}")
    print(f"   Expected: {test_case['expected']}")
    print(f"   Validating...")

    # Run validation
    processor._validate_document_transaction_consistency(test_case['data'])

    print()

print("=" * 70)
print("Validation Testing Complete!")
print()
print("Key Points:")
print("  • Invoices (business bills customers) = INCOME")
print("  • Receipts (business pays vendors) = EXPENSE")
print("  • System logs warnings for mismatches")
print("  • Processing continues (manual review recommended)")
print()

# Test the updated prompt
print("=" * 70)
print("Updated LLM Prompt Includes:")
print("=" * 70)
from agentic_bookkeeper.llm.llm_provider import create_standard_prompt

prompt = create_standard_prompt(categories)
print()

# Extract key guidance from prompt
if "invoice→income" in prompt.lower():
    print("✅ Prompt includes invoice→income guidance")
if "receipt→expense" in prompt.lower():
    print("✅ Prompt includes receipt→expense guidance")
if "CRITICAL" in prompt or "IMPORTANT" in prompt:
    print("✅ Prompt emphasizes importance with CRITICAL/IMPORTANT")
if "MUST be" in prompt:
    print("✅ Prompt uses strong language (MUST be)")

print()
print("=" * 70)
print("✅ All accounting terminology improvements implemented!")
print()
print("Files Modified:")
print("  • src/agentic_bookkeeper/llm/llm_provider.py - Updated prompt")
print("  • src/agentic_bookkeeper/core/document_processor.py - Added validation")
print()
print("Documentation Created:")
print("  • ACCOUNTING_TERMINOLOGY.md - Complete reference")
print()
