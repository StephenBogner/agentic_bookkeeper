"""
Document monitor for watching directory for new files.

This module uses watchdog to monitor a directory for new financial documents.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

import logging
from pathlib import Path
from typing import Callable, List, Optional, Any
import shutil
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

logger = logging.getLogger(__name__)


class DocumentHandler(FileSystemEventHandler):
    """
    File system event handler for document monitoring.

    Handles new file creation events and filters for supported file types.
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}

    def __init__(
        self, callback: Callable[[str], None], supported_extensions: Optional[List[str]] = None
    ):
        """
        Initialize document handler.

        Args:
            callback: Function to call when new document is detected
            supported_extensions: List of supported file extensions
        """
        super().__init__()
        self.callback = callback

        if supported_extensions:
            self.supported_extensions = {ext.lower() for ext in supported_extensions}
        else:
            self.supported_extensions = self.SUPPORTED_EXTENSIONS

        logger.info(f"Document handler initialized for extensions: {self.supported_extensions}")

    def on_created(self, event: Any) -> None:
        """
        Handle file creation event.

        Args:
            event: File system event
        """
        if isinstance(event, FileCreatedEvent) and not event.is_directory:
            file_path = Path(event.src_path)

            # Check if file extension is supported
            if file_path.suffix.lower() in self.supported_extensions:
                logger.info(f"New document detected: {file_path.name}")
                try:
                    self.callback(str(file_path))
                except Exception as e:
                    logger.error(f"Error processing document {file_path.name}: {e}")


class DocumentMonitor:
    """
    Monitor directory for new financial documents.

    Uses watchdog to detect new files and trigger processing.
    """

    def __init__(
        self,
        watch_directory: str,
        processed_directory: str,
        on_document_callback: Callable[[str], None],
        supported_extensions: Optional[List[str]] = None,
    ):
        """
        Initialize document monitor.

        Args:
            watch_directory: Directory to monitor
            processed_directory: Directory to move processed files
            on_document_callback: Callback function for new documents
            supported_extensions: List of supported file extensions
        """
        self.watch_directory = Path(watch_directory)
        self.processed_directory = Path(processed_directory)
        self.on_document_callback = on_document_callback

        # Ensure directories exist
        self.watch_directory.mkdir(parents=True, exist_ok=True)
        self.processed_directory.mkdir(parents=True, exist_ok=True)

        # Create event handler
        self.event_handler = DocumentHandler(
            callback=self._handle_document, supported_extensions=supported_extensions
        )

        # Create observer
        self.observer = Observer()
        self.observer.schedule(self.event_handler, str(self.watch_directory), recursive=False)

        self._is_running = False
        logger.info(f"Document monitor initialized - watching: {self.watch_directory}")

    def _handle_document(self, file_path: str) -> None:
        """
        Handle a new document.

        Args:
            file_path: Path to the document
        """
        try:
            # Call user callback
            self.on_document_callback(file_path)

            # Archive document after processing
            self.archive_document(file_path)

        except Exception as e:
            logger.error(f"Error handling document {file_path}: {e}")
            # Don't archive if processing failed
            raise

    def start(self) -> None:
        """Start monitoring the directory."""
        if not self._is_running:
            self.observer.start()
            self._is_running = True
            logger.info("Document monitor started")
        else:
            logger.warning("Document monitor is already running")

    def stop(self) -> None:
        """Stop monitoring the directory."""
        if self._is_running:
            self.observer.stop()
            self.observer.join()
            self._is_running = False
            logger.info("Document monitor stopped")
        else:
            logger.warning("Document monitor is not running")

    def is_running(self) -> bool:
        """
        Check if monitor is running.

        Returns:
            True if monitoring, False otherwise
        """
        return self._is_running

    def archive_document(self, file_path: str) -> str:
        """
        Move processed document to archive directory.

        Args:
            file_path: Path to the document

        Returns:
            Path to archived file

        Raises:
            Exception: If archiving fails
        """
        try:
            source = Path(file_path)

            # Create archive filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{timestamp}_{source.name}"
            destination = self.processed_directory / archive_name

            # Move file
            shutil.move(str(source), str(destination))
            logger.info(f"Document archived: {archive_name}")

            return str(destination)

        except Exception as e:
            logger.error(f"Failed to archive document {file_path}: {e}")
            raise

    def process_existing_files(self) -> List[str]:
        """
        Process any existing files in the watch directory.

        Returns:
            List of processed file paths
        """
        processed = []

        try:
            for file_path in self.watch_directory.iterdir():
                if file_path.is_file():
                    # Check if supported extension
                    if file_path.suffix.lower() in self.event_handler.supported_extensions:
                        logger.info(f"Processing existing file: {file_path.name}")
                        try:
                            self._handle_document(str(file_path))
                            processed.append(str(file_path))
                        except Exception as e:
                            logger.error(f"Failed to process {file_path.name}: {e}")

        except Exception as e:
            logger.error(f"Error processing existing files: {e}")

        return processed

    def get_status(self) -> dict:
        """
        Get monitor status information.

        Returns:
            Dictionary with status information
        """
        return {
            "is_running": self._is_running,
            "watch_directory": str(self.watch_directory),
            "processed_directory": str(self.processed_directory),
            "supported_extensions": list(self.event_handler.supported_extensions),
            "observer_alive": self.observer.is_alive() if self._is_running else False,
        }

    def __enter__(self) -> "DocumentMonitor":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.stop()

    def __del__(self) -> None:
        """Cleanup on deletion."""
        if self._is_running:
            self.stop()
