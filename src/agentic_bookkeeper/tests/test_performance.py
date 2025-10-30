"""
Module: test_performance
Purpose: Comprehensive performance testing suite for agentic_bookkeeper
Author: Stephen Bogner
Created: 2025-10-29
"""

import os
import time
import tempfile
import tracemalloc
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import pytest
from unittest.mock import Mock, patch

from agentic_bookkeeper.models.database import Database
from agentic_bookkeeper.models.transaction import Transaction
from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.core.document_processor import DocumentProcessor
from agentic_bookkeeper.core.report_generator import ReportGenerator
from agentic_bookkeeper.llm.llm_provider import LLMProvider


# Performance targets
MAX_DOCUMENT_PROCESSING_TIME = 30.0  # seconds
MAX_DATABASE_QUERY_TIME = 0.05  # seconds (50ms)
MAX_REPORT_GENERATION_TIME = 5.0  # seconds for 1000 transactions
MAX_MEMORY_USAGE = 200 * 1024 * 1024  # 200MB in bytes
MAX_UI_RESPONSE_TIME = 0.1  # seconds (100ms)


class PerformanceMetrics:
    """Container for performance metrics."""

    def __init__(self):
        self.execution_times: List[float] = []
        self.memory_usage: List[int] = []
        self.timestamps: List[datetime] = []

    def add_measurement(self, execution_time: float, memory_usage: int = 0) -> None:
        """Add a performance measurement."""
        self.execution_times.append(execution_time)
        self.memory_usage.append(memory_usage)
        self.timestamps.append(datetime.now())

    def average_time(self) -> float:
        """Calculate average execution time."""
        return sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0

    def max_time(self) -> float:
        """Get maximum execution time."""
        return max(self.execution_times) if self.execution_times else 0

    def min_time(self) -> float:
        """Get minimum execution time."""
        return min(self.execution_times) if self.execution_times else 0

    def average_memory(self) -> int:
        """Calculate average memory usage."""
        return sum(self.memory_usage) // len(self.memory_usage) if self.memory_usage else 0

    def max_memory(self) -> int:
        """Get maximum memory usage."""
        return max(self.memory_usage) if self.memory_usage else 0


@pytest.fixture
def perf_database():
    """Create a temporary database for performance testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db = Database(db_path)
    db.initialize_schema()  # Initialize database schema
    yield db

    # Cleanup
    db.close()
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def perf_transaction_manager(perf_database):
    """Create a transaction manager for performance testing."""
    return TransactionManager(perf_database)


@pytest.fixture
def large_transaction_dataset(perf_transaction_manager):
    """Create a large dataset of transactions for testing."""
    transactions = []
    start_date = datetime(2024, 1, 1)

    categories = ["Meals", "Travel", "Supplies", "Utilities", "Marketing", "Software"]
    vendors = ["Vendor A", "Vendor B", "Vendor C", "Vendor D", "Vendor E"]

    for i in range(1000):
        transaction_date = start_date + timedelta(days=i % 365)
        transaction = Transaction(
            date=transaction_date.strftime("%Y-%m-%d"),
            type="expense" if i % 10 != 0 else "income",
            category=categories[i % len(categories)],
            amount=round(10.0 + (i % 500), 2),
            vendor_customer=vendors[i % len(vendors)],
            description=f"Test transaction {i}",
            document_filename=f"doc_{i}.pdf",
        )
        transaction_id = perf_transaction_manager.create_transaction(transaction)
        saved_transaction = perf_transaction_manager.get_transaction(transaction_id)
        transactions.append(saved_transaction)

    return transactions


@pytest.fixture
def mock_llm_provider():
    """Create a mock LLM provider for consistent testing."""
    from agentic_bookkeeper.llm.llm_provider import ExtractionResult

    mock_provider = Mock(spec=LLMProvider)
    mock_provider.extract_transaction.return_value = ExtractionResult(
        success=True,
        transaction_data={
            "date": "2024-01-15",
            "vendor_customer": "Test Vendor",
            "amount": "123.45",
            "category": "Meals",
            "description": "Test transaction",
            "type": "expense",
        },
        confidence=0.95,
        provider="Mock",
        processing_time=0.1,
    )
    return mock_provider


class TestDocumentProcessingPerformance:
    """Test document processing performance."""

    @patch("agentic_bookkeeper.core.document_processor.fitz")
    def test_pdf_processing_time(self, mock_fitz, mock_llm_provider, perf_transaction_manager):
        """Test PDF processing completes within time limit."""
        # Mock PDF processing
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_pixmap.return_value.tobytes.return_value = b"mock image data"
        mock_doc.__len__ = Mock(return_value=1)
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        mock_fitz.open.return_value = mock_doc

        processor = DocumentProcessor(mock_llm_provider, ["Meals", "Travel", "Supplies"])

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = f.name

        try:
            start_time = time.time()
            processor.process_document(pdf_path)
            execution_time = time.time() - start_time

            assert (
                execution_time < MAX_DOCUMENT_PROCESSING_TIME
            ), f"PDF processing took {execution_time:.2f}s, target: {MAX_DOCUMENT_PROCESSING_TIME}s"
        finally:
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)

    @patch("agentic_bookkeeper.core.document_processor.Image")
    def test_image_processing_time(self, mock_image, mock_llm_provider, perf_transaction_manager):
        """Test image processing completes within time limit."""
        # Mock image processing
        mock_img = Mock()
        mock_image.open.return_value = mock_img

        processor = DocumentProcessor(mock_llm_provider, ["Meals", "Travel", "Supplies"])

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            image_path = f.name

        try:
            start_time = time.time()
            processor.process_document(image_path)
            execution_time = time.time() - start_time

            assert (
                execution_time < MAX_DOCUMENT_PROCESSING_TIME
            ), f"Image processing took {execution_time:.2f}s, target: {MAX_DOCUMENT_PROCESSING_TIME}s"
        finally:
            if os.path.exists(image_path):
                os.unlink(image_path)

    @patch("agentic_bookkeeper.core.document_processor.fitz")
    def test_batch_processing_performance(
        self, mock_fitz, mock_llm_provider, perf_transaction_manager
    ):
        """Test batch document processing performance."""
        # Mock PDF processing
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_pixmap.return_value.tobytes.return_value = b"mock image data"
        mock_doc.__len__ = Mock(return_value=1)
        mock_doc.__getitem__ = Mock(return_value=mock_page)
        mock_fitz.open.return_value = mock_doc

        processor = DocumentProcessor(mock_llm_provider, ["Meals", "Travel", "Supplies"])
        doc_paths = []

        try:
            # Create 10 mock documents
            for i in range(10):
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                    doc_paths.append(f.name)

            start_time = time.time()
            for doc_path in doc_paths:
                processor.process_document(doc_path)
            total_time = time.time() - start_time

            avg_time = total_time / len(doc_paths)
            assert (
                avg_time < MAX_DOCUMENT_PROCESSING_TIME
            ), f"Average processing time {avg_time:.2f}s exceeds target {MAX_DOCUMENT_PROCESSING_TIME}s"
        finally:
            for doc_path in doc_paths:
                if os.path.exists(doc_path):
                    os.unlink(doc_path)


class TestDatabaseQueryPerformance:
    """Test database query performance."""

    def test_single_transaction_query_time(
        self, perf_transaction_manager, large_transaction_dataset
    ):
        """Test single transaction retrieval speed."""
        transaction_id = large_transaction_dataset[500].id

        start_time = time.time()
        transaction = perf_transaction_manager.get_transaction(transaction_id)
        execution_time = time.time() - start_time

        assert transaction is not None
        assert (
            execution_time < MAX_DATABASE_QUERY_TIME
        ), f"Query took {execution_time*1000:.2f}ms, target: {MAX_DATABASE_QUERY_TIME*1000:.0f}ms"

    def test_filtered_query_performance(self, perf_transaction_manager, large_transaction_dataset):
        """Test filtered query performance."""
        start_time = time.time()
        transactions = perf_transaction_manager.query_transactions(transaction_type="expense")
        execution_time = time.time() - start_time

        assert len(transactions) > 0
        assert (
            execution_time < MAX_DATABASE_QUERY_TIME
        ), f"Filtered query took {execution_time*1000:.2f}ms, target: {MAX_DATABASE_QUERY_TIME*1000:.0f}ms"

    def test_date_range_query_performance(
        self, perf_transaction_manager, large_transaction_dataset
    ):
        """Test date range query performance."""
        start_date = "2024-01-01"
        end_date = "2024-12-31"

        start_time = time.time()
        transactions = perf_transaction_manager.query_transactions(
            start_date=start_date, end_date=end_date
        )
        execution_time = time.time() - start_time

        assert len(transactions) > 0
        assert (
            execution_time < MAX_DATABASE_QUERY_TIME
        ), f"Date range query took {execution_time*1000:.2f}ms, target: {MAX_DATABASE_QUERY_TIME*1000:.0f}ms"

    def test_all_transactions_query_performance(
        self, perf_transaction_manager, large_transaction_dataset
    ):
        """Test query all transactions performance."""
        start_time = time.time()
        transactions = perf_transaction_manager.get_all_transactions()
        execution_time = time.time() - start_time

        assert len(transactions) == 1000
        # Allow more time for large dataset retrieval
        assert (
            execution_time < MAX_DATABASE_QUERY_TIME * 5
        ), f"Query all took {execution_time*1000:.2f}ms, target: {MAX_DATABASE_QUERY_TIME*5*1000:.0f}ms"

    def test_category_aggregation_performance(
        self, perf_transaction_manager, large_transaction_dataset
    ):
        """Test category-based aggregation query performance."""
        # This tests the performance of filtering by category
        start_time = time.time()
        category = "Meals"
        meals_transactions = [
            t for t in perf_transaction_manager.get_all_transactions() if t.category == category
        ]
        execution_time = time.time() - start_time

        assert len(meals_transactions) > 0
        assert (
            execution_time < MAX_DATABASE_QUERY_TIME * 5
        ), f"Category aggregation took {execution_time*1000:.2f}ms"


class TestReportGenerationPerformance:
    """Test report generation performance."""

    def test_income_statement_generation_time(
        self, perf_transaction_manager, large_transaction_dataset
    ):
        """Test income statement generation with large dataset."""
        report_generator = ReportGenerator(perf_transaction_manager)
        start_date = "2024-01-01"
        end_date = "2024-12-31"

        start_time = time.time()
        report = report_generator.generate_income_statement(start_date, end_date)
        execution_time = time.time() - start_time

        assert report is not None
        assert "report_type" in report
        assert (
            execution_time < MAX_REPORT_GENERATION_TIME
        ), f"Income statement generation took {execution_time:.2f}s, target: {MAX_REPORT_GENERATION_TIME}s"

    def test_expense_report_generation_time(
        self, perf_transaction_manager, large_transaction_dataset
    ):
        """Test expense report generation with large dataset."""
        report_generator = ReportGenerator(perf_transaction_manager, jurisdiction="CRA")
        start_date = "2024-01-01"
        end_date = "2024-12-31"

        start_time = time.time()
        report = report_generator.generate_expense_report(start_date, end_date)
        execution_time = time.time() - start_time

        assert report is not None
        assert "report_type" in report
        assert (
            execution_time < MAX_REPORT_GENERATION_TIME
        ), f"Expense report generation took {execution_time:.2f}s, target: {MAX_REPORT_GENERATION_TIME}s"

    def test_multiple_report_generation_consistency(
        self, perf_transaction_manager, large_transaction_dataset
    ):
        """Test multiple report generations for performance consistency."""
        report_generator = ReportGenerator(perf_transaction_manager)
        start_date = "2024-01-01"
        end_date = "2024-12-31"

        metrics = PerformanceMetrics()

        # Generate 5 reports and measure consistency
        for _ in range(5):
            start_time = time.time()
            report_generator.generate_income_statement(start_date, end_date)
            execution_time = time.time() - start_time
            metrics.add_measurement(execution_time)

        avg_time = metrics.average_time()
        max_time = metrics.max_time()
        min_time = metrics.min_time()

        # Check consistency (max time should not be more than 5x min time for small operations)
        # First run often includes initialization overhead
        assert (
            max_time < min_time * 5
        ), f"Performance inconsistent: min={min_time:.2f}s, max={max_time:.2f}s"
        assert (
            avg_time < MAX_REPORT_GENERATION_TIME
        ), f"Average generation time {avg_time:.2f}s exceeds target {MAX_REPORT_GENERATION_TIME}s"


class TestMemoryUsage:
    """Test memory usage and detect memory leaks."""

    def test_baseline_memory_usage(self, perf_database):
        """Test baseline memory usage of application."""
        tracemalloc.start()

        # Create basic components
        transaction_manager = TransactionManager(perf_database)

        # Measure memory
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Baseline should be well under 200MB
        assert (
            current < MAX_MEMORY_USAGE
        ), f"Baseline memory {current / 1024 / 1024:.2f}MB exceeds target {MAX_MEMORY_USAGE / 1024 / 1024:.0f}MB"

    def test_memory_during_document_processing(self, mock_llm_provider, perf_transaction_manager):
        """Test memory usage during document processing."""
        tracemalloc.start()

        processor = DocumentProcessor(mock_llm_provider, ["Meals", "Travel", "Supplies"])

        # Process multiple documents
        with patch("agentic_bookkeeper.core.document_processor.fitz") as mock_fitz:
            mock_doc = Mock()
            mock_page = Mock()
            mock_page.get_pixmap.return_value.tobytes.return_value = b"mock image data"
            mock_doc.__len__ = Mock(return_value=1)
            mock_doc.__getitem__ = Mock(return_value=mock_page)
            mock_fitz.open.return_value = mock_doc

            for i in range(10):
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                    pdf_path = f.name
                try:
                    processor.process_document(pdf_path)
                finally:
                    if os.path.exists(pdf_path):
                        os.unlink(pdf_path)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        assert (
            peak < MAX_MEMORY_USAGE
        ), f"Peak memory {peak / 1024 / 1024:.2f}MB exceeds target {MAX_MEMORY_USAGE / 1024 / 1024:.0f}MB"

    def test_memory_during_report_generation(
        self, perf_transaction_manager, large_transaction_dataset
    ):
        """Test memory usage during report generation."""
        tracemalloc.start()

        report_generator = ReportGenerator(perf_transaction_manager)
        start_date = "2024-01-01"
        end_date = "2024-12-31"

        # Generate multiple reports
        for _ in range(10):
            report_generator.generate_income_statement(start_date, end_date)
            report_generator.generate_expense_report(start_date, end_date)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        assert (
            peak < MAX_MEMORY_USAGE
        ), f"Peak memory {peak / 1024 / 1024:.2f}MB exceeds target {MAX_MEMORY_USAGE / 1024 / 1024:.0f}MB"

    def test_memory_leak_detection(self, perf_transaction_manager, large_transaction_dataset):
        """Test for memory leaks during repeated operations."""
        tracemalloc.start()

        report_generator = ReportGenerator(perf_transaction_manager)
        start_date = "2024-01-01"
        end_date = "2024-12-31"

        memory_snapshots = []

        # Perform operations and track memory
        for i in range(5):
            report_generator.generate_income_statement(start_date, end_date)
            current, _ = tracemalloc.get_traced_memory()
            memory_snapshots.append(current)

        tracemalloc.stop()

        # Check that memory usage doesn't grow unbounded
        # Allow for some variance but not linear growth
        first_half_avg = sum(memory_snapshots[:2]) / 2
        second_half_avg = sum(memory_snapshots[3:]) / 2

        growth_factor = second_half_avg / first_half_avg if first_half_avg > 0 else 1

        # Allow for 2x growth factor due to Python garbage collection variability
        assert (
            growth_factor < 2.0
        ), f"Possible memory leak detected: memory grew by {(growth_factor - 1) * 100:.1f}%"


class TestPerformanceProfiler:
    """Test performance profiling utilities."""

    def test_profile_report_generation(self, perf_transaction_manager, large_transaction_dataset):
        """Profile report generation to identify bottlenecks."""
        import cProfile
        import pstats
        from io import StringIO

        report_generator = ReportGenerator(perf_transaction_manager)
        start_date = "2024-01-01"
        end_date = "2024-12-31"

        profiler = cProfile.Profile()
        profiler.enable()

        # Profile report generation
        report_generator.generate_income_statement(start_date, end_date)

        profiler.disable()

        # Capture profiling stats
        stream = StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats("cumulative")
        stats.print_stats(10)  # Top 10 functions

        profile_output = stream.getvalue()

        # Verify profiling worked
        assert len(profile_output) > 0
        assert "generate_income_statement" in profile_output or "cumulative" in profile_output

    def test_identify_slowest_operations(self, perf_transaction_manager, large_transaction_dataset):
        """Identify and document slowest operations."""
        operations = {}

        # Test various operations
        start_date = "2024-01-01"
        end_date = "2024-12-31"

        # Database operations
        start_time = time.time()
        perf_transaction_manager.get_all_transactions()
        operations["get_all_transactions"] = time.time() - start_time

        # Report generation
        report_generator = ReportGenerator(perf_transaction_manager)

        start_time = time.time()
        report_generator.generate_income_statement(start_date, end_date)
        operations["generate_income_statement"] = time.time() - start_time

        start_time = time.time()
        report_generator.generate_expense_report(start_date, end_date)
        operations["generate_expense_report"] = time.time() - start_time

        # Find slowest operation
        slowest = max(operations.items(), key=lambda x: x[1])

        # Document results
        print(f"\nPerformance Results:")
        for op, duration in sorted(operations.items(), key=lambda x: x[1], reverse=True):
            print(f"  {op}: {duration*1000:.2f}ms")
        print(f"Slowest operation: {slowest[0]} ({slowest[1]*1000:.2f}ms)")

        # All operations should still be reasonably fast
        assert (
            slowest[1] < MAX_REPORT_GENERATION_TIME
        ), f"Slowest operation {slowest[0]} took {slowest[1]:.2f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
