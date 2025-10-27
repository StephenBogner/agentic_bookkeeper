"""
Unit tests for document processor.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from agentic_bookkeeper.core.document_processor import DocumentProcessor
from agentic_bookkeeper.llm.llm_provider import ExtractionResult
from agentic_bookkeeper.models.transaction import CRA_CATEGORIES


@pytest.mark.unit
class TestDocumentProcessor:
    """Test DocumentProcessor class."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock LLM provider."""
        provider = Mock()
        provider.provider_name = "MockProvider"
        provider.extract_transaction = Mock()
        return provider

    @pytest.fixture
    def processor(self, mock_provider):
        """Create a document processor with mock provider."""
        return DocumentProcessor(mock_provider, CRA_CATEGORIES)

    @pytest.fixture
    def successful_extraction_result(self):
        """Create a successful extraction result."""
        return ExtractionResult(
            success=True,
            transaction_data={
                'date': '2025-01-15',
                'transaction_type': 'expense',
                'category': 'Office expenses',
                'vendor_customer': 'Office Depot',
                'amount': 125.50,
                'tax_amount': 16.32,
                'description': 'Office supplies'
            },
            confidence=0.95,
            provider="MockProvider",
            processing_time=1.5
        )

    def test_initialization(self, mock_provider):
        """Test processor initialization."""
        processor = DocumentProcessor(mock_provider, CRA_CATEGORIES)

        assert processor.llm_provider == mock_provider
        assert processor.categories == CRA_CATEGORIES

    def test_supported_formats(self, processor):
        """Test getting supported formats."""
        formats = processor.get_supported_formats()

        assert '.pdf' in formats
        assert '.png' in formats
        assert '.jpg' in formats
        assert '.jpeg' in formats

    def test_process_document_success(
        self,
        processor,
        mock_provider,
        successful_extraction_result,
        temp_dir
    ):
        """Test successful document processing."""
        # Create a small valid image file (1x1 pixel PNG)
        from PIL import Image as PILImage
        test_image = temp_dir / "test_receipt.jpg"
        img = PILImage.new('RGB', (1, 1))
        img.save(str(test_image))

        # Mock provider to return successful result
        mock_provider.extract_transaction.return_value = successful_extraction_result

        # Process document
        transaction = processor.process_document(str(test_image))

        # Verify
        assert transaction is not None
        assert transaction.date == '2025-01-15'
        assert transaction.type == 'expense'
        assert transaction.amount == 125.50
        assert transaction.document_filename == 'test_receipt.jpg'

        # Verify provider was called
        mock_provider.extract_transaction.assert_called_once()

    def test_process_document_nonexistent_file(self, processor):
        """Test processing non-existent file."""
        transaction = processor.process_document("/nonexistent/file.jpg")

        assert transaction is None

    def test_process_document_unsupported_format(self, processor, temp_dir):
        """Test processing unsupported file format."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("not an image")

        transaction = processor.process_document(str(test_file))

        assert transaction is None

    def test_process_document_extraction_failure(
        self,
        processor,
        mock_provider,
        temp_dir
    ):
        """Test document processing when extraction fails."""
        # Create test file
        from PIL import Image as PILImage
        test_image = temp_dir / "test.jpg"
        img = PILImage.new('RGB', (1, 1))
        img.save(str(test_image))

        # Mock provider to return failed result
        mock_provider.extract_transaction.return_value = ExtractionResult(
            success=False,
            error_message="Extraction failed",
            provider="MockProvider",
            processing_time=1.0
        )

        transaction = processor.process_document(str(test_image))

        assert transaction is None

    def test_process_document_invalid_data(
        self,
        processor,
        mock_provider,
        temp_dir
    ):
        """Test processing when extracted data is invalid."""
        from PIL import Image as PILImage
        test_image = temp_dir / "test.jpg"
        img = PILImage.new('RGB', (1, 1))
        img.save(str(test_image))

        # Return result with invalid transaction type
        mock_provider.extract_transaction.return_value = ExtractionResult(
            success=True,
            transaction_data={
                'date': '2025-01-15',
                'transaction_type': 'invalid_type',  # Invalid
                'category': 'Office',
                'amount': 100.00
            },
            confidence=0.9,
            provider="MockProvider",
            processing_time=1.0
        )

        # Should fail validation
        transaction = processor.process_document(str(test_image), validate=True)

        assert transaction is None

    def test_validate_extraction(self, processor):
        """Test extraction validation."""
        from agentic_bookkeeper.models.transaction import Transaction

        # Valid transaction
        valid_trans = Transaction(
            date='2025-01-15',
            type='expense',
            category='Office expenses',
            amount=100.00
        )

        is_valid, messages = processor.validate_extraction(valid_trans)

        assert is_valid is True
        assert len(messages) == 0

    def test_validate_extraction_missing_fields(self, processor):
        """Test validation with missing fields."""
        from agentic_bookkeeper.models.transaction import Transaction

        # Create a valid transaction with some missing optional fields
        # but test that validation notices when amount is zero
        trans = Transaction(
            date='2025-01-15',
            type='expense',
            category='Office',
            amount=0.0  # Zero amount - should be flagged
        )

        is_valid, messages = processor.validate_extraction(trans)

        # Should detect zero amount
        assert is_valid is False
        assert len(messages) > 0
        assert any('amount' in msg.lower() for msg in messages)

    def test_change_provider(self, processor):
        """Test changing LLM provider."""
        new_provider = Mock()
        new_provider.provider_name = "NewProvider"

        processor.change_provider(new_provider)

        assert processor.llm_provider == new_provider
        assert processor.llm_provider.provider_name == "NewProvider"

    def test_get_provider_stats(self, processor, mock_provider):
        """Test getting provider statistics."""
        # Mock stats
        mock_provider.get_stats.return_value = {
            'provider': 'MockProvider',
            'request_count': 10,
            'error_count': 1,
            'success_rate': 0.9
        }

        stats = processor.get_provider_stats()

        assert stats['provider'] == 'MockProvider'
        assert stats['request_count'] == 10
        assert stats['success_rate'] == 0.9
