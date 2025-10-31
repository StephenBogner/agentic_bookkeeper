#!/usr/bin/env python3
"""Quick verification script for category filtering functionality."""

from src.agentic_bookkeeper.models.transaction import (
    get_categories_for_jurisdiction,
    CRA_INCOME_CATEGORIES,
    CRA_EXPENSE_CATEGORIES,
    IRS_INCOME_CATEGORIES,
    IRS_EXPENSE_CATEGORIES,
)

def test_category_filtering():
    """Test that category filtering works correctly."""

    print("Testing CRA category filtering...")

    # Test income filtering
    income_cats = get_categories_for_jurisdiction("CRA", "income")
    print(f"✓ CRA income categories ({len(income_cats)}): {income_cats[:3]}...")
    assert income_cats == CRA_INCOME_CATEGORIES, "Income categories mismatch!"

    # Test expense filtering
    expense_cats = get_categories_for_jurisdiction("CRA", "expense")
    print(f"✓ CRA expense categories ({len(expense_cats)}): {expense_cats[:3]}...")
    assert expense_cats == CRA_EXPENSE_CATEGORIES, "Expense categories mismatch!"

    # Test no filtering (all categories)
    all_cats = get_categories_for_jurisdiction("CRA")
    print(f"✓ CRA all categories ({len(all_cats)}): {all_cats[:3]}...")
    assert len(all_cats) == len(income_cats) + len(expense_cats), "Combined categories count mismatch!"

    print("\nTesting IRS category filtering...")

    # Test income filtering
    income_cats = get_categories_for_jurisdiction("IRS", "income")
    print(f"✓ IRS income categories ({len(income_cats)}): {income_cats[:3]}...")
    assert income_cats == IRS_INCOME_CATEGORIES, "Income categories mismatch!"

    # Test expense filtering
    expense_cats = get_categories_for_jurisdiction("IRS", "expense")
    print(f"✓ IRS expense categories ({len(expense_cats)}): {expense_cats[:3]}...")
    assert expense_cats == IRS_EXPENSE_CATEGORIES, "Expense categories mismatch!"

    # Test no filtering (all categories)
    all_cats = get_categories_for_jurisdiction("IRS")
    print(f"✓ IRS all categories ({len(all_cats)}): {all_cats[:3]}...")
    assert len(all_cats) == len(income_cats) + len(expense_cats), "Combined categories count mismatch!"

    print("\n✅ All category filtering tests passed!")

    # Display income categories
    print("\n" + "="*60)
    print("INCOME CATEGORIES")
    print("="*60)
    print("\nCRA Income Categories:")
    for cat in CRA_INCOME_CATEGORIES:
        print(f"  - {cat}")
    print(f"\nIRS Income Categories:")
    for cat in IRS_INCOME_CATEGORIES:
        print(f"  - {cat}")

    print("\n" + "="*60)
    print("EXPENSE CATEGORIES (sample)")
    print("="*60)
    print(f"\nCRA Expense Categories: {len(CRA_EXPENSE_CATEGORIES)} total")
    print(f"IRS Expense Categories: {len(IRS_EXPENSE_CATEGORIES)} total")

if __name__ == "__main__":
    test_category_filtering()
