"""
Database module for Agentic Bookkeeper.

This module provides SQLite database connection management, schema creation,
and basic database operations for the bookkeeping application.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

import sqlite3
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


logger = logging.getLogger(__name__)


class Database:
    """
    SQLite database manager for Agentic Bookkeeper.

    Handles database initialization, schema creation, connection management,
    and backup operations.
    """

    SCHEMA_VERSION = 1

    # SQL Schema Definitions
    TRANSACTIONS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
        category TEXT NOT NULL,
        vendor_customer TEXT,
        description TEXT,
        amount REAL NOT NULL CHECK(amount >= 0),
        tax_amount REAL DEFAULT 0 CHECK(tax_amount >= 0),
        document_filename TEXT,
        created_at TEXT NOT NULL,
        modified_at TEXT NOT NULL
    );
    """

    TRANSACTIONS_INDEXES_SQL = [
        "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);",
        "CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);",
        "CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);",
        "CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);"
    ]

    CONFIG_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    """

    def __init__(self, db_path: str = "./data/bookkeeper.db"):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._ensure_directory_exists()
        self._connection: Optional[sqlite3.Connection] = None
        logger.info(f"Database initialized at {self.db_path}")

    def _ensure_directory_exists(self) -> None:
        """Create database directory if it doesn't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        """
        Create and return a database connection.

        Returns:
            SQLite connection object
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON;")
            # Return rows as dictionaries
            self._connection.row_factory = sqlite3.Row
            logger.debug("Database connection established")

        return self._connection

    @contextmanager
    def get_cursor(self):
        """
        Context manager for database cursor.

        Yields:
            Database cursor

        Example:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM transactions")
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()

    def initialize_schema(self) -> None:
        """
        Create database schema if it doesn't exist.

        Creates:
            - transactions table with indexes
            - config table
            - schema version entry
        """
        try:
            with self.get_cursor() as cursor:
                # Create transactions table
                cursor.execute(self.TRANSACTIONS_TABLE_SQL)
                logger.info("Transactions table created/verified")

                # Create indexes
                for index_sql in self.TRANSACTIONS_INDEXES_SQL:
                    cursor.execute(index_sql)
                logger.info("Transaction table indexes created/verified")

                # Create config table
                cursor.execute(self.CONFIG_TABLE_SQL)
                logger.info("Config table created/verified")

                # Set schema version
                cursor.execute(
                    "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                    ("schema_version", str(self.SCHEMA_VERSION))
                )

                logger.info("Database schema initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise

    def get_config_value(self, key: str) -> Optional[str]:
        """
        Get a configuration value from the database.

        Args:
            key: Configuration key

        Returns:
            Configuration value or None if not found
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "SELECT value FROM config WHERE key = ?",
                    (key,)
                )
                result = cursor.fetchone()
                return result["value"] if result else None
        except Exception as e:
            logger.error(f"Failed to get config value for {key}: {e}")
            return None

    def set_config_value(self, key: str, value: str) -> None:
        """
        Set a configuration value in the database.

        Args:
            key: Configuration key
            value: Configuration value
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                    (key, value)
                )
                logger.debug(f"Config value set: {key}")
        except Exception as e:
            logger.error(f"Failed to set config value for {key}: {e}")
            raise

    def backup(self, backup_path: Optional[str] = None) -> str:
        """
        Create a backup of the database.

        Args:
            backup_path: Optional custom backup path

        Returns:
            Path to backup file
        """
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = str(self.db_path.parent / f"bookkeeper_backup_{timestamp}.db")

        try:
            shutil.copy2(str(self.db_path), backup_path)
            logger.info(f"Database backup created at {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}")
            raise

    def vacuum(self) -> None:
        """
        Optimize database by reclaiming unused space.

        This should be run periodically to optimize database performance.
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("VACUUM;")
                logger.info("Database vacuumed successfully")
        except Exception as e:
            logger.error(f"Failed to vacuum database: {e}")
            raise

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with database statistics
        """
        stats = {
            "db_path": str(self.db_path),
            "db_size_mb": self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0,
            "schema_version": self.get_config_value("schema_version"),
        }

        try:
            with self.get_cursor() as cursor:
                # Count transactions
                cursor.execute("SELECT COUNT(*) as count FROM transactions")
                stats["transaction_count"] = cursor.fetchone()["count"]

                # Get date range
                cursor.execute(
                    "SELECT MIN(date) as first_date, MAX(date) as last_date FROM transactions"
                )
                result = cursor.fetchone()
                stats["first_transaction_date"] = result["first_date"]
                stats["last_transaction_date"] = result["last_date"]

        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            stats["error"] = str(e)

        return stats

    def close(self) -> None:
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
