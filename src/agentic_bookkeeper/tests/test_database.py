"""
Unit tests for database module.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

import pytest
from pathlib import Path
from agentic_bookkeeper.models.database import Database


@pytest.mark.unit
class TestDatabase:
    """Test Database class."""

    def test_database_initialization(self, test_db_path):
        """Test database can be initialized."""
        db = Database(str(test_db_path))
        assert db.db_path == test_db_path
        assert test_db_path.parent.exists()
        db.close()

    def test_schema_initialization(self, database):
        """Test database schema is created correctly."""
        with database.get_cursor() as cursor:
            # Check transactions table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'"
            )
            assert cursor.fetchone() is not None

            # Check config table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='config'"
            )
            assert cursor.fetchone() is not None

            # Check schema version is set
            schema_version = database.get_config_value("schema_version")
            assert schema_version == "1"

    def test_config_operations(self, database):
        """Test config get/set operations."""
        # Set a config value
        database.set_config_value("test_key", "test_value")

        # Get the config value
        value = database.get_config_value("test_key")
        assert value == "test_value"

        # Get non-existent key
        value = database.get_config_value("non_existent_key")
        assert value is None

    def test_backup(self, database, temp_dir):
        """Test database backup."""
        # Create backup
        backup_path = database.backup(str(temp_dir / "backup.db"))

        # Verify backup exists
        assert Path(backup_path).exists()

        # Verify backup has same schema
        backup_db = Database(backup_path)
        backup_db.connect()
        assert backup_db.get_config_value("schema_version") == "1"
        backup_db.close()

    def test_vacuum(self, database):
        """Test database vacuum operation."""
        # Should not raise exception
        database.vacuum()

    def test_database_stats(self, database):
        """Test getting database statistics."""
        stats = database.get_database_stats()

        assert "db_path" in stats
        assert "db_size_mb" in stats
        assert "schema_version" in stats
        assert "transaction_count" in stats
        assert stats["transaction_count"] == 0  # Empty database

    def test_context_manager(self, test_db_path):
        """Test database context manager."""
        with Database(str(test_db_path)) as db:
            db.initialize_schema()
            assert db._connection is not None

        # Connection should be closed after context
        assert db._connection is None
