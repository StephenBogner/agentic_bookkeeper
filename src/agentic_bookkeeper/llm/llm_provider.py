"""
Abstract base class for LLM providers.

This module defines the interface that all LLM providers must implement
for document processing and transaction extraction.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time
import logging


logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """
    Result from document extraction.

    Attributes:
        success: Whether extraction was successful
        transaction_data: Extracted transaction data (if successful)
        confidence: Confidence score (0.0 to 1.0)
        error_message: Error message (if failed)
        provider: Name of LLM provider used
        processing_time: Time taken in seconds
    """
    success: bool
    transaction_data: Optional[Dict[str, Any]] = None
    confidence: float = 0.0
    error_message: Optional[str] = None
    provider: str = ""
    processing_time: float = 0.0


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All LLM provider implementations must inherit from this class
    and implement the required methods.
    """

    def __init__(self, api_key: str, max_retries: int = 3, timeout: int = 30):
        """
        Initialize LLM provider.

        Args:
            api_key: API key for the provider
            max_retries: Maximum number of retry attempts
            timeout: Timeout in seconds for API calls
        """
        if not api_key:
            raise ValueError("API key cannot be empty")

        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout = timeout
        self._request_count = 0
        self._error_count = 0

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the name of the provider."""
        pass

    @abstractmethod
    def extract_transaction(
        self,
        document_path: str,
        categories: List[str]
    ) -> ExtractionResult:
        """
        Extract transaction data from a document.

        Args:
            document_path: Path to the document (PDF or image)
            categories: List of valid tax categories

        Returns:
            ExtractionResult with transaction data
        """
        pass

    @abstractmethod
    def _prepare_prompt(self, categories: List[str]) -> str:
        """
        Prepare the extraction prompt.

        Args:
            categories: List of valid categories

        Returns:
            Formatted prompt string
        """
        pass

    @abstractmethod
    def _make_api_call(
        self,
        document_path: str,
        prompt: str
    ) -> Dict[str, Any]:
        """
        Make API call to LLM provider.

        Args:
            document_path: Path to document
            prompt: Extraction prompt

        Returns:
            Raw API response

        Raises:
            Exception: If API call fails
        """
        pass

    def validate_response(self, response_data: Dict[str, Any]) -> bool:
        """
        Validate that response contains required fields.

        Args:
            response_data: Extracted transaction data

        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            'date', 'transaction_type', 'amount'
        ]

        for field in required_fields:
            if field not in response_data or response_data[field] is None:
                logger.warning(f"Missing required field: {field}")
                return False

        # Validate transaction_type
        valid_types = ['income', 'expense']
        if response_data.get('transaction_type') not in valid_types:
            logger.warning(f"Invalid transaction type: {response_data.get('transaction_type')}")
            return False

        # Validate amount is numeric
        try:
            float(response_data['amount'])
        except (ValueError, TypeError):
            logger.warning(f"Invalid amount: {response_data.get('amount')}")
            return False

        return True

    def retry_with_backoff(self, func, *args, **kwargs):
        """
        Execute function with exponential backoff retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            Exception: If all retries fail
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                self._error_count += 1

                if attempt < self.max_retries - 1:
                    wait_time = (2 ** attempt) * 1  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries} failed: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {self.max_retries} attempts failed")

        raise last_exception

    def get_stats(self) -> Dict[str, Any]:
        """
        Get provider statistics.

        Returns:
            Dictionary with usage statistics
        """
        return {
            'provider': self.provider_name,
            'request_count': self._request_count,
            'error_count': self._error_count,
            'success_rate': (
                (self._request_count - self._error_count) / self._request_count
                if self._request_count > 0 else 0.0
            )
        }

    def reset_stats(self) -> None:
        """Reset usage statistics."""
        self._request_count = 0
        self._error_count = 0

    def __str__(self) -> str:
        """String representation."""
        return f"{self.provider_name}Provider(requests={self._request_count}, errors={self._error_count})"


class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    pass


class APIKeyError(LLMProviderError):
    """Exception raised for API key issues."""
    pass


class RateLimitError(LLMProviderError):
    """Exception raised when rate limit is exceeded."""
    pass


class ExtractionError(LLMProviderError):
    """Exception raised when extraction fails."""
    pass


def create_standard_prompt(categories: List[str]) -> str:
    """
    Create standard extraction prompt template.

    Args:
        categories: List of valid tax categories

    Returns:
        Formatted prompt string
    """
    categories_str = ", ".join(f'"{cat}"' for cat in categories)

    prompt = f"""You are a financial document analyzer. Extract transaction information from the provided document.

Document Type: Identify if this is an invoice, receipt, or payment record.

Extract the following information:
1. Date of transaction (YYYY-MM-DD format)
2. Vendor/Customer name
3. Total amount (numeric only, no currency symbols)
4. Tax amount if shown (numeric only)
5. Description of goods/services
6. Category from this list: {categories_str}

Return ONLY valid JSON in this exact format:
{{
  "document_type": "invoice|receipt|payment",
  "date": "YYYY-MM-DD",
  "transaction_type": "income|expense",
  "vendor_customer": "string",
  "amount": number,
  "tax_amount": number,
  "description": "string",
  "category": "string"
}}

If you cannot extract a field with confidence, use null.
Do not include any explanatory text, only the JSON object.
"""
    return prompt
