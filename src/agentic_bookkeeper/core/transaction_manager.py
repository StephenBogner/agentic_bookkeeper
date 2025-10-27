"""
Transaction manager for CRUD operations.

This module handles all database operations for transactions.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta

from ..models.database import Database
from ..models.transaction import Transaction

logger = logging.getLogger(__name__)


class TransactionManager:
    """
    Manager for transaction database operations.

    Handles create, read, update, delete, and query operations for transactions.
    """

    def __init__(self, database: Database):
        """
        Initialize transaction manager.

        Args:
            database: Database instance
        """
        self.database = database
        logger.info("Transaction manager initialized")

    def create_transaction(self, transaction: Transaction) -> int:
        """
        Create a new transaction in the database.

        Args:
            transaction: Transaction object to create

        Returns:
            ID of created transaction

        Raises:
            Exception: If creation fails
        """
        try:
            with self.database.get_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO transactions (
                        date, type, category, vendor_customer, description,
                        amount, tax_amount, document_filename, created_at, modified_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        transaction.date,
                        transaction.type,
                        transaction.category,
                        transaction.vendor_customer,
                        transaction.description,
                        transaction.amount,
                        transaction.tax_amount,
                        transaction.document_filename,
                        transaction.created_at,
                        transaction.modified_at
                    )
                )

                transaction_id = cursor.lastrowid
                logger.info(f"Created transaction with ID: {transaction_id}")
                return transaction_id

        except Exception as e:
            logger.error(f"Failed to create transaction: {e}")
            raise

    def get_transaction(self, transaction_id: int) -> Optional[Transaction]:
        """
        Get a transaction by ID.

        Args:
            transaction_id: Transaction ID

        Returns:
            Transaction object or None if not found
        """
        try:
            with self.database.get_cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM transactions WHERE id = ?",
                    (transaction_id,)
                )

                row = cursor.fetchone()
                if row:
                    return Transaction.from_db_row(row)
                return None

        except Exception as e:
            logger.error(f"Failed to get transaction {transaction_id}: {e}")
            return None

    def update_transaction(self, transaction: Transaction) -> bool:
        """
        Update an existing transaction.

        Args:
            transaction: Transaction object with updated data

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Update modified timestamp
            transaction.update_modified_timestamp()

            with self.database.get_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE transactions SET
                        date = ?,
                        type = ?,
                        category = ?,
                        vendor_customer = ?,
                        description = ?,
                        amount = ?,
                        tax_amount = ?,
                        document_filename = ?,
                        modified_at = ?
                    WHERE id = ?
                    """,
                    (
                        transaction.date,
                        transaction.type,
                        transaction.category,
                        transaction.vendor_customer,
                        transaction.description,
                        transaction.amount,
                        transaction.tax_amount,
                        transaction.document_filename,
                        transaction.modified_at,
                        transaction.id
                    )
                )

                if cursor.rowcount > 0:
                    logger.info(f"Updated transaction ID: {transaction.id}")
                    return True
                else:
                    logger.warning(f"Transaction ID {transaction.id} not found for update")
                    return False

        except Exception as e:
            logger.error(f"Failed to update transaction {transaction.id}: {e}")
            return False

    def delete_transaction(self, transaction_id: int) -> bool:
        """
        Delete a transaction.

        Args:
            transaction_id: Transaction ID to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            with self.database.get_cursor() as cursor:
                cursor.execute(
                    "DELETE FROM transactions WHERE id = ?",
                    (transaction_id,)
                )

                if cursor.rowcount > 0:
                    logger.info(f"Deleted transaction ID: {transaction_id}")
                    return True
                else:
                    logger.warning(f"Transaction ID {transaction_id} not found for deletion")
                    return False

        except Exception as e:
            logger.error(f"Failed to delete transaction {transaction_id}: {e}")
            return False

    def query_transactions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        transaction_type: Optional[str] = None,
        category: Optional[str] = None,
        vendor_customer: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: str = "date DESC"
    ) -> List[Transaction]:
        """
        Query transactions with filters.

        Args:
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            transaction_type: Type filter ('income' or 'expense')
            category: Category filter
            vendor_customer: Vendor/customer name filter (partial match)
            min_amount: Minimum amount filter
            max_amount: Maximum amount filter
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Order by clause (default: "date DESC")

        Returns:
            List of Transaction objects
        """
        try:
            query = "SELECT * FROM transactions WHERE 1=1"
            params = []

            # Build query with filters
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)

            if end_date:
                query += " AND date <= ?"
                params.append(end_date)

            if transaction_type:
                query += " AND type = ?"
                params.append(transaction_type)

            if category:
                query += " AND category = ?"
                params.append(category)

            if vendor_customer:
                query += " AND vendor_customer LIKE ?"
                params.append(f"%{vendor_customer}%")

            if min_amount is not None:
                query += " AND amount >= ?"
                params.append(min_amount)

            if max_amount is not None:
                query += " AND amount <= ?"
                params.append(max_amount)

            # Add ordering
            query += f" ORDER BY {order_by}"

            # Add limit and offset
            if limit is not None:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])

            with self.database.get_cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()

                transactions = [Transaction.from_db_row(row) for row in rows]
                logger.debug(f"Query returned {len(transactions)} transactions")
                return transactions

        except Exception as e:
            logger.error(f"Failed to query transactions: {e}")
            return []

    def search_transactions(self, search_term: str) -> List[Transaction]:
        """
        Search transactions by description or vendor/customer.

        Args:
            search_term: Search term

        Returns:
            List of matching transactions
        """
        try:
            with self.database.get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM transactions
                    WHERE description LIKE ? OR vendor_customer LIKE ?
                    ORDER BY date DESC
                    """,
                    (f"%{search_term}%", f"%{search_term}%")
                )

                rows = cursor.fetchall()
                transactions = [Transaction.from_db_row(row) for row in rows]
                logger.debug(f"Search found {len(transactions)} transactions")
                return transactions

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_all_transactions(self, limit: Optional[int] = None) -> List[Transaction]:
        """
        Get all transactions.

        Args:
            limit: Maximum number of transactions to return

        Returns:
            List of all transactions
        """
        return self.query_transactions(limit=limit, order_by="date DESC")

    def detect_duplicates(
        self,
        transaction: Transaction,
        time_window_days: int = 7
    ) -> List[Transaction]:
        """
        Detect potential duplicate transactions.

        Args:
            transaction: Transaction to check for duplicates
            time_window_days: Days before/after to search

        Returns:
            List of potential duplicate transactions
        """
        try:
            # Calculate date range
            trans_date = datetime.strptime(transaction.date, "%Y-%m-%d").date()
            start_date = (trans_date - timedelta(days=time_window_days)).isoformat()
            end_date = (trans_date + timedelta(days=time_window_days)).isoformat()

            # Query similar transactions
            candidates = self.query_transactions(
                start_date=start_date,
                end_date=end_date,
                transaction_type=transaction.type,
                min_amount=transaction.amount * 0.95,  # 5% tolerance
                max_amount=transaction.amount * 1.05
            )

            # Filter for exact or very similar matches
            duplicates = []
            for candidate in candidates:
                if candidate.id != transaction.id:
                    # Check if amounts are very close
                    if abs(candidate.amount - transaction.amount) < 0.01:
                        # Check if same vendor or similar description
                        if (candidate.vendor_customer == transaction.vendor_customer or
                            candidate.description == transaction.description):
                            duplicates.append(candidate)

            return duplicates

        except Exception as e:
            logger.error(f"Duplicate detection failed: {e}")
            return []

    def get_transaction_statistics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get transaction statistics for a date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Dictionary with statistics
        """
        try:
            query = """
                SELECT
                    type,
                    COUNT(*) as count,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount,
                    MIN(amount) as min_amount,
                    MAX(amount) as max_amount
                FROM transactions
                WHERE 1=1
            """
            params = []

            if start_date:
                query += " AND date >= ?"
                params.append(start_date)

            if end_date:
                query += " AND date <= ?"
                params.append(end_date)

            query += " GROUP BY type"

            with self.database.get_cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()

                stats = {
                    'income': {'count': 0, 'total': 0.0, 'avg': 0.0, 'min': 0.0, 'max': 0.0},
                    'expense': {'count': 0, 'total': 0.0, 'avg': 0.0, 'min': 0.0, 'max': 0.0}
                }

                for row in rows:
                    trans_type = row['type']
                    stats[trans_type] = {
                        'count': row['count'],
                        'total': round(row['total_amount'], 2),
                        'avg': round(row['avg_amount'], 2),
                        'min': round(row['min_amount'], 2),
                        'max': round(row['max_amount'], 2)
                    }

                # Calculate net
                stats['net'] = round(
                    stats['income']['total'] - stats['expense']['total'],
                    2
                )

                return stats

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

    def get_category_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        transaction_type: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Get summary of amounts by category.

        Args:
            start_date: Start date filter
            end_date: End date filter
            transaction_type: Type filter ('income' or 'expense')

        Returns:
            Dictionary mapping category to total amount
        """
        try:
            query = """
                SELECT category, SUM(amount) as total
                FROM transactions
                WHERE 1=1
            """
            params = []

            if start_date:
                query += " AND date >= ?"
                params.append(start_date)

            if end_date:
                query += " AND date <= ?"
                params.append(end_date)

            if transaction_type:
                query += " AND type = ?"
                params.append(transaction_type)

            query += " GROUP BY category ORDER BY total DESC"

            with self.database.get_cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()

                return {
                    row['category']: round(row['total'], 2)
                    for row in rows
                }

        except Exception as e:
            logger.error(f"Failed to get category summary: {e}")
            return {}
