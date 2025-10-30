"""
Unit tests for document monitor.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

import pytest
from pathlib import Path
import time
from unittest.mock import Mock

from agentic_bookkeeper.core.document_monitor import DocumentMonitor, DocumentHandler


@pytest.mark.unit
class TestDocumentHandler:
    """Test DocumentHandler class."""

    def test_initialization(self):
        """Test handler initialization."""
        callback = Mock()
        handler = DocumentHandler(callback)

        assert handler.callback == callback
        assert ".pdf" in handler.supported_extensions
        assert ".jpg" in handler.supported_extensions

    def test_custom_extensions(self):
        """Test handler with custom extensions."""
        callback = Mock()
        handler = DocumentHandler(callback, supported_extensions=[".pdf", ".png"])

        assert ".pdf" in handler.supported_extensions
        assert ".png" in handler.supported_extensions
        assert ".jpg" not in handler.supported_extensions


@pytest.mark.unit
class TestDocumentMonitor:
    """Test DocumentMonitor class."""

    def test_initialization(self, temp_dir):
        """Test monitor initialization."""
        watch_dir = temp_dir / "watch"
        processed_dir = temp_dir / "processed"
        callback = Mock()

        monitor = DocumentMonitor(
            watch_directory=str(watch_dir),
            processed_directory=str(processed_dir),
            on_document_callback=callback,
        )

        assert monitor.watch_directory == watch_dir
        assert monitor.processed_directory == processed_dir
        assert watch_dir.exists()
        assert processed_dir.exists()

    def test_archive_document(self, temp_dir):
        """Test archiving a document."""
        watch_dir = temp_dir / "watch"
        processed_dir = temp_dir / "processed"
        callback = Mock()

        monitor = DocumentMonitor(
            watch_directory=str(watch_dir),
            processed_directory=str(processed_dir),
            on_document_callback=callback,
        )

        # Create a test file
        test_file = watch_dir / "test_receipt.pdf"
        test_file.write_text("test content")

        # Archive it
        archive_path = monitor.archive_document(str(test_file))

        # Verify
        assert not test_file.exists()  # Original should be moved
        assert Path(archive_path).exists()  # Archive should exist
        assert Path(archive_path).parent == processed_dir
        assert "test_receipt.pdf" in archive_path

    def test_process_existing_files(self, temp_dir):
        """Test processing existing files in directory."""
        watch_dir = temp_dir / "watch"
        processed_dir = temp_dir / "processed"
        callback = Mock()

        # Ensure directories exist
        watch_dir.mkdir(parents=True, exist_ok=True)
        processed_dir.mkdir(parents=True, exist_ok=True)

        # Create test files
        test_pdf = watch_dir / "test1.pdf"
        test_jpg = watch_dir / "test2.jpg"
        test_txt = watch_dir / "test3.txt"  # Unsupported

        test_pdf.write_text("pdf content")
        test_jpg.write_text("jpg content")
        test_txt.write_text("txt content")

        monitor = DocumentMonitor(
            watch_directory=str(watch_dir),
            processed_directory=str(processed_dir),
            on_document_callback=callback,
        )

        # Process existing files
        processed = monitor.process_existing_files()

        # Should process PDF and JPG, but not TXT
        assert len(processed) == 2
        assert callback.call_count == 2

    def test_get_status(self, temp_dir):
        """Test getting monitor status."""
        watch_dir = temp_dir / "watch"
        processed_dir = temp_dir / "processed"
        callback = Mock()

        monitor = DocumentMonitor(
            watch_directory=str(watch_dir),
            processed_directory=str(processed_dir),
            on_document_callback=callback,
        )

        status = monitor.get_status()

        assert status["is_running"] is False
        assert status["watch_directory"] == str(watch_dir)
        assert status["processed_directory"] == str(processed_dir)
        assert ".pdf" in status["supported_extensions"]

    def test_start_stop_monitor(self, temp_dir):
        """Test starting and stopping the monitor."""
        watch_dir = temp_dir / "watch"
        processed_dir = temp_dir / "processed"
        callback = Mock()

        monitor = DocumentMonitor(
            watch_directory=str(watch_dir),
            processed_directory=str(processed_dir),
            on_document_callback=callback,
        )

        # Start
        monitor.start()
        assert monitor.is_running() is True

        # Stop
        monitor.stop()
        assert monitor.is_running() is False

    def test_context_manager(self, temp_dir):
        """Test using monitor as context manager."""
        watch_dir = temp_dir / "watch"
        processed_dir = temp_dir / "processed"
        callback = Mock()

        monitor = DocumentMonitor(
            watch_directory=str(watch_dir),
            processed_directory=str(processed_dir),
            on_document_callback=callback,
        )

        assert monitor.is_running() is False

        with monitor:
            assert monitor.is_running() is True

        assert monitor.is_running() is False
