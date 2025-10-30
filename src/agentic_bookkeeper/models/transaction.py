"""
Transaction model for Agentic Bookkeeper.

This module defines the Transaction data class with validation and serialization.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
import logging


logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    """
    Represents a financial transaction.

    Attributes:
        id: Unique transaction ID (auto-generated)
        date: Transaction date (YYYY-MM-DD format)
        type: Transaction type ('income' or 'expense')
        category: Tax category (CRA or IRS compliant)
        vendor_customer: Vendor or customer name
        description: Transaction description
        amount: Transaction amount (must be >= 0)
        tax_amount: Tax amount (must be >= 0)
        document_filename: Original document filename
        created_at: Timestamp when record was created
        modified_at: Timestamp when record was last modified
    """

    date: str
    type: str
    category: str
    amount: float
    vendor_customer: Optional[str] = None
    description: Optional[str] = None
    tax_amount: float = 0.0
    document_filename: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate transaction data after initialization."""
        self.validate()

        # Set timestamps if not provided
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.modified_at is None:
            self.modified_at = datetime.now().isoformat()

    def validate(self) -> None:
        """
        Validate transaction data.

        Raises:
            ValueError: If any field contains invalid data
        """
        # Validate date format (YYYY-MM-DD)
        try:
            datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format: {self.date}. Expected YYYY-MM-DD")

        # Validate type
        if self.type not in ("income", "expense"):
            raise ValueError(
                f"Invalid transaction type: {self.type}. Must be 'income' or 'expense'"
            )

        # Validate category (non-empty string)
        if not self.category or not isinstance(self.category, str):
            raise ValueError("Category must be a non-empty string")

        # Validate amount (must be >= 0)
        if self.amount < 0:
            raise ValueError(f"Amount must be >= 0, got {self.amount}")

        # Validate tax_amount (must be >= 0)
        if self.tax_amount < 0:
            raise ValueError(f"Tax amount must be >= 0, got {self.tax_amount}")

        # Round amounts to 2 decimal places
        self.amount = round(self.amount, 2)
        self.tax_amount = round(self.tax_amount, 2)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert transaction to dictionary.

        Returns:
            Dictionary representation of transaction
        """
        return {
            "id": self.id,
            "date": self.date,
            "type": self.type,
            "category": self.category,
            "vendor_customer": self.vendor_customer,
            "description": self.description,
            "amount": self.amount,
            "tax_amount": self.tax_amount,
            "document_filename": self.document_filename,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        """
        Create transaction from dictionary.

        Args:
            data: Dictionary with transaction data

        Returns:
            Transaction instance
        """
        return cls(
            id=data.get("id"),
            date=data["date"],
            type=data["type"],
            category=data["category"],
            vendor_customer=data.get("vendor_customer"),
            description=data.get("description"),
            amount=float(data["amount"]),
            tax_amount=float(data.get("tax_amount", 0.0)),
            document_filename=data.get("document_filename"),
            created_at=data.get("created_at"),
            modified_at=data.get("modified_at"),
        )

    @classmethod
    def from_db_row(cls, row: Any) -> "Transaction":
        """
        Create transaction from database row (sqlite3.Row).

        Args:
            row: Database row object

        Returns:
            Transaction instance
        """
        return cls(
            id=row["id"],
            date=row["date"],
            type=row["type"],
            category=row["category"],
            vendor_customer=row["vendor_customer"],
            description=row["description"],
            amount=float(row["amount"]),
            tax_amount=float(row["tax_amount"]),
            document_filename=row["document_filename"],
            created_at=row["created_at"],
            modified_at=row["modified_at"],
        )

    def update_modified_timestamp(self) -> None:
        """Update the modified_at timestamp to current time."""
        self.modified_at = datetime.now().isoformat()

    def __str__(self) -> str:
        """Return string representation of transaction.

        Returns:
            Human-readable string
        """
        return (
            f"Transaction(id={self.id}, date={self.date}, type={self.type}, "
            f"category={self.category}, amount=${self.amount:.2f})"
        )

    def __repr__(self) -> str:
        """
        Detailed string representation for debugging.

        Returns:
            Detailed string representation
        """
        return (
            f"Transaction(id={self.id}, date='{self.date}', type='{self.type}', "
            f"category='{self.category}', vendor_customer='{self.vendor_customer}', "
            f"amount={self.amount:.2f}, tax_amount={self.tax_amount:.2f}, "
            f"document='{self.document_filename}')"
        )

    def __eq__(self, other: Any) -> bool:
        """
        Compare transactions for equality (excluding timestamps).

        Args:
            other: Another transaction

        Returns:
            True if transactions are equal (excluding id and timestamps)
        """
        if not isinstance(other, Transaction):
            return False

        return (
            self.date == other.date
            and self.type == other.type
            and self.category == other.category
            and self.vendor_customer == other.vendor_customer
            and self.description == other.description
            and abs(self.amount - other.amount) < 0.01  # Float comparison tolerance
            and abs(self.tax_amount - other.tax_amount) < 0.01
            and self.document_filename == other.document_filename
        )

    def __lt__(self, other: Any) -> bool:
        """
        Compare transactions for sorting (by date, then amount).

        Args:
            other: Another transaction

        Returns:
            True if this transaction is "less than" other
        """
        if not isinstance(other, Transaction):
            return NotImplemented

        if self.date != other.date:
            return self.date < other.date
        return self.amount < other.amount

    def is_income(self) -> bool:
        """Check if transaction is income."""
        return self.type == "income"

    def is_expense(self) -> bool:
        """Check if transaction is expense."""
        return self.type == "expense"

    def get_total_with_tax(self) -> float:
        """
        Get total amount including tax.

        Returns:
            Amount + tax_amount
        """
        return round(self.amount + self.tax_amount, 2)


# Valid CRA and IRS categories
CRA_CATEGORIES = [
    "Advertising",
    "Business tax, fees, licenses",
    "Insurance",
    "Interest and bank charges",
    "Meals and entertainment (50% deductible)",
    "Motor vehicle expenses",
    "Office expenses",
    "Supplies",
    "Legal and professional fees",
    "Rent",
    "Salaries and wages",
    "Telephone and utilities",
    "Travel",
    "Other expenses",
]

IRS_CATEGORIES = [
    "Advertising",
    "Car and truck expenses",
    "Commissions and fees",
    "Contract labor",
    "Depletion",
    "Depreciation",
    "Employee benefit programs",
    "Insurance",
    "Interest (mortgage/other)",
    "Legal and professional services",
    "Office expense",
    "Pension and profit-sharing plans",
    "Rent or lease",
    "Repairs and maintenance",
    "Supplies",
    "Taxes and licenses",
    "Travel and meals",
    "Utilities",
    "Wages",
    "Other expenses",
]


def validate_category(category: str, jurisdiction: str) -> bool:
    """
    Validate that a category is valid for the given tax jurisdiction.

    Args:
        category: Category name
        jurisdiction: Tax jurisdiction ('CRA' or 'IRS')

    Returns:
        True if category is valid

    Raises:
        ValueError: If jurisdiction is invalid
    """
    if jurisdiction == "CRA":
        return category in CRA_CATEGORIES
    elif jurisdiction == "IRS":
        return category in IRS_CATEGORIES
    else:
        raise ValueError(f"Invalid jurisdiction: {jurisdiction}. Must be 'CRA' or 'IRS'")


def get_categories_for_jurisdiction(jurisdiction: str) -> list:
    """
    Get list of valid categories for a tax jurisdiction.

    Args:
        jurisdiction: Tax jurisdiction ('CRA' or 'IRS')

    Returns:
        List of category names

    Raises:
        ValueError: If jurisdiction is invalid
    """
    if jurisdiction == "CRA":
        return CRA_CATEGORIES.copy()
    elif jurisdiction == "IRS":
        return IRS_CATEGORIES.copy()
    else:
        raise ValueError(f"Invalid jurisdiction: {jurisdiction}. Must be 'CRA' or 'IRS'")
