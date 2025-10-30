# Task Specification: T-017

**Task Name:** End-to-End Integration Testing
**Task ID:** T-017
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 3: Integration & Validation
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 4 hours
**Dependencies:** T-016

---

## OBJECTIVE

Create comprehensive integration tests that validate the complete workflow from document intake to storage, ensuring all components work together correctly.

---

## REQUIREMENTS

### Functional Requirements
- Test complete workflow: document → extraction → review → storage
- Test monitoring → processing → archiving pipeline
- Test provider switching between LLM providers
- Test error recovery scenarios
- Test concurrent document processing
- Test large transaction volumes (stress test)
- Validate data integrity throughout pipeline
- Test configuration changes during runtime

### Non-Functional Requirements
- Integration tests complete in <2 minutes
- Test realistic usage scenarios
- Use actual database (not mocks)
- Tests should be reproducible

---

## ACCEPTANCE CRITERIA

- [ ] Full workflow completes successfully
- [ ] All LLM providers work in integrated environment
- [ ] Data integrity maintained throughout pipeline
- [ ] Error recovery works as expected
- [ ] Concurrent processing handles race conditions
- [ ] Performance acceptable under load
- [ ] Configuration changes applied correctly
- [ ] Tests are stable and reproducible

---

## EXPECTED DELIVERABLES

**Files to Create:**
- `src/agentic_bookkeeper/tests/test_integration.py`

**Files to Modify:**
- None

---

## VALIDATION COMMANDS

```bash
# Run integration tests
pytest src/agentic_bookkeeper/tests/test_integration.py -v

# Run with coverage
pytest src/agentic_bookkeeper/tests/test_integration.py --cov=src/agentic_bookkeeper

# Run specific integration scenario
pytest src/agentic_bookkeeper/tests/test_integration.py::test_complete_workflow -v
```

---

## IMPLEMENTATION NOTES

### Integration Test Structure

```python
# test_integration.py
import pytest
from pathlib import Path
import shutil
from src.agentic_bookkeeper.models.database import Database
from src.agentic_bookkeeper.core.document_processor import DocumentProcessor
from src.agentic_bookkeeper.core.transaction_manager import TransactionManager
from src.agentic_bookkeeper.core.document_monitor import DocumentMonitor

class TestIntegration:
    """End-to-end integration tests."""

    @pytest.fixture
    def integration_env(self, tmp_path):
        """Set up complete integration environment."""
        # Create directories
        watch_dir = tmp_path / 'watch'
        archive_dir = tmp_path / 'archive'
        db_path = tmp_path / 'test.db'

        watch_dir.mkdir()
        archive_dir.mkdir()

        # Initialize components
        db = Database(str(db_path))
        db.initialize_schema()

        processor = DocumentProcessor(llm_provider='mock')
        manager = TransactionManager(db)
        monitor = DocumentMonitor(watch_dir, archive_dir, processor)

        yield {
            'watch_dir': watch_dir,
            'archive_dir': archive_dir,
            'db': db,
            'processor': processor,
            'manager': manager,
            'monitor': monitor
        }

        # Cleanup
        db.close()

    def test_complete_workflow(self, integration_env):
        """Test: document → extraction → storage."""
        # 1. Create sample document
        # 2. Process document
        # 3. Validate extraction
        # 4. Store transaction
        # 5. Verify database entry
        # 6. Verify archive
        pass

    def test_monitoring_pipeline(self, integration_env):
        """Test: monitoring → processing → archiving."""
        # 1. Start monitor
        # 2. Add document to watch directory
        # 3. Wait for processing
        # 4. Verify archived
        # 5. Verify transaction in database
        # 6. Stop monitor
        pass

    def test_provider_switching(self, integration_env):
        """Test switching between LLM providers."""
        # Test with OpenAI, then Anthropic
        pass

    def test_error_recovery(self, integration_env):
        """Test error scenarios and recovery."""
        # Test invalid document
        # Test API failure
        # Test database error
        # Verify graceful handling
        pass

    def test_concurrent_processing(self, integration_env):
        """Test processing multiple documents concurrently."""
        # Add multiple documents
        # Verify all processed correctly
        # Check for race conditions
        pass

    def test_large_volume(self, integration_env):
        """Test with large number of transactions."""
        # Create 1000+ transactions
        # Test query performance
        # Test filtering performance
        # Verify data integrity
        pass
```

### Test Scenarios

**Scenario 1: Happy Path**
```python
def test_happy_path(integration_env):
    """Test complete successful workflow."""
    # 1. Create sample receipt
    # 2. Process with document processor
    # 3. Validate extracted data
    # 4. Save to database
    # 5. Query transaction
    # 6. Verify all fields correct
    # 7. Check archived file exists
```

**Scenario 2: Error Handling**
```python
def test_error_scenarios(integration_env):
    """Test various error conditions."""
    # Corrupted PDF
    # Invalid image format
    # API timeout
    # Database locked
    # Disk full (archive)
```

**Scenario 3: Data Integrity**
```python
def test_data_integrity(integration_env):
    """Validate data integrity through pipeline."""
    # Process document
    # Compare extracted data with stored data
    # Verify no data loss
    # Verify no data corruption
    # Check timestamps
```

---

## NOTES

- Integration tests use real components (not mocks)
- Use temporary directories and databases
- Clean up after each test
- Use fixtures for setup/teardown
- Test realistic scenarios
- Include stress tests for performance validation
- Document any known limitations
- Consider timing issues in monitoring tests (use polling)

### Key Integration Points to Test

1. **Document Processor ↔ LLM Providers**
2. **Document Processor ↔ Transaction Manager**
3. **Document Monitor ↔ Document Processor**
4. **Transaction Manager ↔ Database**
5. **Configuration ↔ All Components**

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-018 - Performance Optimization
