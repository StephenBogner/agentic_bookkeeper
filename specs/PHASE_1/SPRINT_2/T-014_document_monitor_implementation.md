# Task Specification: T-014

**Task Name:** Document Monitor Implementation
**Task ID:** T-014
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 2: LLM Integration & Document Processing
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 4 hours
**Dependencies:** T-012

---

## OBJECTIVE

Implement the document monitor that watches a directory for new financial documents, processes them automatically, and archives them after processing.

---

## REQUIREMENTS

### Functional Requirements
- Watch specified directory for new files
- Filter for supported file types (PDF, JPG, PNG, JPEG)
- Detect file creation and modification events
- Process documents automatically via DocumentProcessor
- Archive processed files to separate directory
- Maintain processing queue for multiple files
- Emit events for GUI updates
- Support start/stop monitoring
- Handle file system errors gracefully

### Non-Functional Requirements
- Detect new files within 1 second
- Process files in order of arrival
- Handle concurrent file arrivals
- Prevent processing same file twice
- Archive maintains original filename with timestamp

---

## ACCEPTANCE CRITERIA

- [ ] Detects new files in watch directory
- [ ] Filters for supported file types only
- [ ] Processes files automatically
- [ ] Archives processed files correctly
- [ ] Handles multiple files in sequence
- [ ] Start/stop monitoring works cleanly
- [ ] File system errors handled gracefully
- [ ] Events emitted for GUI integration
- [ ] Unit tests achieve >80% coverage

---

## EXPECTED DELIVERABLES

**Files to Create:**
- `src/agentic_bookkeeper/core/document_monitor.py`

**Files to Modify:**
- `src/agentic_bookkeeper/core/__init__.py` (export monitor)

---

## VALIDATION COMMANDS

```bash
# Test document monitor
pytest src/agentic_bookkeeper/tests/test_document_monitor.py -v

# Manual test
python -c "
from src.agentic_bookkeeper.core.document_monitor import DocumentMonitor
from pathlib import Path

watch_dir = Path('./test_watch')
archive_dir = Path('./test_archive')
watch_dir.mkdir(exist_ok=True)
archive_dir.mkdir(exist_ok=True)

monitor = DocumentMonitor(watch_dir, archive_dir)
monitor.start()

# Copy a test file to watch directory
# Monitor should process and archive it

input('Press Enter to stop monitoring...')
monitor.stop()
"
```

---

## IMPLEMENTATION NOTES

### Document Monitor Class Structure

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DocumentMonitor:
    """Monitor directory for new financial documents."""

    SUPPORTED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png']

    def __init__(self,
                 watch_directory: str,
                 archive_directory: str,
                 document_processor: DocumentProcessor):
        """Initialize monitor."""
        self.watch_dir = Path(watch_directory)
        self.archive_dir = Path(archive_directory)
        self.processor = document_processor
        self.observer = Observer()
        self.event_handler = DocumentEventHandler(self)

    def start(self) -> None:
        """Start monitoring directory."""
        pass

    def stop(self) -> None:
        """Stop monitoring directory."""
        pass

    def process_file(self, file_path: Path) -> None:
        """Process a single file."""
        pass

    def archive_file(self, file_path: Path) -> Path:
        """Archive processed file."""
        pass

    def _is_supported(self, file_path: Path) -> bool:
        """Check if file type is supported."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

class DocumentEventHandler(FileSystemEventHandler):
    """Handle file system events."""

    def on_created(self, event):
        """Handle file creation."""
        pass

    def on_modified(self, event):
        """Handle file modification."""
        pass
```

### Archive Filename Format

```python
# Original: receipt.pdf
# Archived: receipt_20250115_143022.pdf (with timestamp)

def archive_file(self, file_path: Path) -> Path:
    """Archive file with timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    stem = file_path.stem
    suffix = file_path.suffix
    archive_name = f"{stem}_{timestamp}{suffix}"
    return self.archive_dir / archive_name
```

### Event System for GUI

```python
from typing import Callable

class DocumentMonitor:
    def __init__(self, ...):
        self.on_file_detected: Optional[Callable] = None
        self.on_file_processed: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

    def emit_event(self, event_name: str, data: dict):
        """Emit event to subscribers."""
        if event_name == 'file_detected' and self.on_file_detected:
            self.on_file_detected(data)
        # etc.
```

---

## NOTES

- watchdog library provides cross-platform file monitoring
- Debounce file events to avoid duplicate processing
- Wait for file to finish writing before processing
- Handle locked files (file in use by another process)
- Archive directory should be separate from watch directory
- Consider processing queue for high volume scenarios
- Log all monitoring events for debugging
- Graceful shutdown: finish processing current file before stopping

### File Processing States

1. **Detected:** New file appears in watch directory
2. **Processing:** File being processed by DocumentProcessor
3. **Review:** Awaiting user review (GUI interaction)
4. **Archived:** File moved to archive directory
5. **Error:** Processing failed, file remains in watch directory

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-015 - CLI Interface for Testing
