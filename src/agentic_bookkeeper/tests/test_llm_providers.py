"""
Unit tests for LLM providers.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from agentic_bookkeeper.llm.llm_provider import (
    LLMProvider,
    ExtractionResult,
    create_standard_prompt,
    APIKeyError,
    RateLimitError
)


@pytest.mark.unit
class TestLLMProviderBase:
    """Test LLMProvider base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that abstract base class cannot be instantiated."""
        with pytest.raises(TypeError):
            LLMProvider("test_api_key")

    def test_validate_response_valid(self):
        """Test response validation with valid data."""
        # Create a concrete implementation for testing
        class TestProvider(LLMProvider):
            @property
            def provider_name(self):
                return "Test"

            def extract_transaction(self, document_path, categories):
                pass

            def _prepare_prompt(self, categories):
                pass

            def _make_api_call(self, document_path, prompt):
                pass

        provider = TestProvider("test_key")

        valid_response = {
            'date': '2025-01-15',
            'transaction_type': 'expense',
            'amount': 100.00,
            'category': 'Office'
        }

        assert provider.validate_response(valid_response) is True

    def test_validate_response_missing_fields(self):
        """Test validation with missing required fields."""
        class TestProvider(LLMProvider):
            @property
            def provider_name(self):
                return "Test"

            def extract_transaction(self, document_path, categories):
                pass

            def _prepare_prompt(self, categories):
                pass

            def _make_api_call(self, document_path, prompt):
                pass

        provider = TestProvider("test_key")

        # Missing 'amount'
        invalid_response = {
            'date': '2025-01-15',
            'transaction_type': 'expense'
        }

        assert provider.validate_response(invalid_response) is False

    def test_validate_response_invalid_type(self):
        """Test validation with invalid transaction type."""
        class TestProvider(LLMProvider):
            @property
            def provider_name(self):
                return "Test"

            def extract_transaction(self, document_path, categories):
                pass

            def _prepare_prompt(self, categories):
                pass

            def _make_api_call(self, document_path, prompt):
                pass

        provider = TestProvider("test_key")

        invalid_response = {
            'date': '2025-01-15',
            'transaction_type': 'invalid',  # Not 'income' or 'expense'
            'amount': 100.00
        }

        assert provider.validate_response(invalid_response) is False

    def test_get_stats(self):
        """Test getting provider statistics."""
        class TestProvider(LLMProvider):
            @property
            def provider_name(self):
                return "Test"

            def extract_transaction(self, document_path, categories):
                pass

            def _prepare_prompt(self, categories):
                pass

            def _make_api_call(self, document_path, prompt):
                pass

        provider = TestProvider("test_key")
        provider._request_count = 10
        provider._error_count = 2

        stats = provider.get_stats()

        assert stats['provider'] == 'Test'
        assert stats['request_count'] == 10
        assert stats['error_count'] == 2
        assert stats['success_rate'] == 0.8  # (10-2)/10

    def test_reset_stats(self):
        """Test resetting provider statistics."""
        class TestProvider(LLMProvider):
            @property
            def provider_name(self):
                return "Test"

            def extract_transaction(self, document_path, categories):
                pass

            def _prepare_prompt(self, categories):
                pass

            def _make_api_call(self, document_path, prompt):
                pass

        provider = TestProvider("test_key")
        provider._request_count = 10
        provider._error_count = 2

        provider.reset_stats()

        assert provider._request_count == 0
        assert provider._error_count == 0


@pytest.mark.unit
class TestCreateStandardPrompt:
    """Test standard prompt creation."""

    def test_create_prompt_with_categories(self):
        """Test creating prompt with categories."""
        categories = ["Office expenses", "Travel", "Advertising"]
        prompt = create_standard_prompt(categories)

        assert "Office expenses" in prompt
        assert "Travel" in prompt
        assert "Advertising" in prompt
        assert "JSON" in prompt
        assert "YYYY-MM-DD" in prompt

    def test_prompt_includes_required_fields(self):
        """Test that prompt includes all required fields."""
        categories = ["Office"]
        prompt = create_standard_prompt(categories)

        required_fields = [
            'date',
            'transaction_type',
            'amount',
            'vendor_customer',
            'category',
            'description',
            'tax_amount'
        ]

        for field in required_fields:
            assert field in prompt


@pytest.mark.unit
class TestOpenAIProvider:
    """Test OpenAI provider (with mocking)."""

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        with patch('agentic_bookkeeper.llm.openai_provider.OpenAI') as mock:
            yield mock

    def test_provider_name(self, mock_openai_client):
        """Test provider name."""
        try:
            from agentic_bookkeeper.llm.openai_provider import OpenAIProvider
            provider = OpenAIProvider("test_key")
            assert provider.provider_name == "OpenAI"
        except ImportError:
            pytest.skip("OpenAI package not installed")

    def test_initialization(self, mock_openai_client):
        """Test provider initialization."""
        try:
            from agentic_bookkeeper.llm.openai_provider import OpenAIProvider
            provider = OpenAIProvider("test_key", model="gpt-4-vision-preview")
            assert provider.model == "gpt-4-vision-preview"
        except ImportError:
            pytest.skip("OpenAI package not installed")


@pytest.mark.unit
class TestAnthropicProvider:
    """Test Anthropic provider (with mocking)."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Mock Anthropic client."""
        with patch('agentic_bookkeeper.llm.anthropic_provider.Anthropic') as mock:
            yield mock

    def test_provider_name(self, mock_anthropic_client):
        """Test provider name."""
        try:
            from agentic_bookkeeper.llm.anthropic_provider import AnthropicProvider
            provider = AnthropicProvider("test_key")
            assert provider.provider_name == "Anthropic"
        except ImportError:
            pytest.skip("Anthropic package not installed")

    def test_initialization(self, mock_anthropic_client):
        """Test provider initialization."""
        try:
            from agentic_bookkeeper.llm.anthropic_provider import AnthropicProvider
            provider = AnthropicProvider("test_key", model="claude-3-5-sonnet-20241022")
            assert provider.model == "claude-3-5-sonnet-20241022"
        except ImportError:
            pytest.skip("Anthropic package not installed")
