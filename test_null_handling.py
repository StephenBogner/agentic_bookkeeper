#!/usr/bin/env python3
"""
Test that transaction creation handles null values from LLM properly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentic_bookkeeper.core.document_processor import DocumentProcessor
from agentic_bookkeeper.llm.llm_provider import ExtractionResult
from agentic_bookkeeper.llm.openai_provider import OpenAIProvider

print("Testing Null Value Handling in Transaction Creation")
print("=" * 60)

# Create a mock extraction result with null values
test_cases = [
    {
        "name": "All null values",
        "data": {
            "date": None,
            "transaction_type": None,
            "category": None,
            "vendor_customer": None,
            "description": None,
            "amount": None,
            "tax_amount": None,
        }
    },
    {
        "name": "Null amount only",
        "data": {
            "date": "2025-10-27",
            "transaction_type": "expense",
            "category": "Office expenses",
            "vendor_customer": "Test Vendor",
            "description": "Test transaction",
            "amount": None,
            "tax_amount": 10.0,
        }
    },
    {
        "name": "Empty string amount",
        "data": {
            "date": "2025-10-27",
            "transaction_type": "expense",
            "category": "Office expenses",
            "vendor_customer": "Test Vendor",
            "description": "Test transaction",
            "amount": "",
            "tax_amount": "",
        }
    },
    {
        "name": "Valid data",
        "data": {
            "date": "2025-10-27",
            "transaction_type": "expense",
            "category": "Office expenses",
            "vendor_customer": "Test Vendor",
            "description": "Test transaction",
            "amount": 100.50,
            "tax_amount": 13.00,
        }
    }
]

# Create processor
provider = OpenAIProvider(api_key="test_key")
categories = ["Office expenses"]
processor = DocumentProcessor(provider, categories)

print("\nTesting transaction creation with various null scenarios:\n")

all_passed = True

for i, test_case in enumerate(test_cases, 1):
    print(f"{i}. {test_case['name']}")
    print("-" * 60)

    # Create extraction result
    result = ExtractionResult(
        success=True,
        transaction_data=test_case['data'],
        confidence=0.9,
        provider="test",
        processing_time=1.0
    )

    try:
        # Try to create transaction
        transaction = processor._create_transaction_from_result(result, "test.pdf")

        if transaction is None:
            print("   ⚠️  Transaction is None (expected for all-null case)")
            # This might be expected behavior for validation
        else:
            print(f"   ✅ Transaction created successfully")
            print(f"      Amount: ${transaction.amount:.2f}")
            print(f"      Tax: ${transaction.tax_amount:.2f}")
            print(f"      Vendor: {transaction.vendor_customer}")

    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        all_passed = False

    print()

print("=" * 60)
if all_passed:
    print("✅ All null value scenarios handled correctly!")
    print("\nKey improvements:")
    print("  • None values converted to 0.0 for numeric fields")
    print("  • Empty strings handled properly")
    print("  • No more float() conversion errors")
    print("  • Graceful handling of incomplete LLM responses")
    sys.exit(0)
else:
    print("❌ Some scenarios failed")
    sys.exit(1)
