"""
Anthropic provider implementation for document extraction.

This module implements the LLM provider interface using Anthropic's Claude API.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

import logging
import base64
import json
from pathlib import Path
from typing import Dict, Any, List
import time

from .llm_provider import (
    LLMProvider,
    ExtractionResult,
    APIKeyError,
    RateLimitError,
    ExtractionError,
    create_standard_prompt,
)

try:
    from anthropic import Anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """
    Anthropic implementation of LLM provider.

    Uses Claude with vision capabilities for document analysis.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_retries: int = 3,
        timeout: int = 30,
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-3-5-sonnet-20241022)
            max_retries: Maximum retry attempts
            timeout: Request timeout in seconds
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic package not installed. " "Install with: pip install anthropic"
            )

        super().__init__(api_key, max_retries, timeout)
        self.model = model
        self.client = Anthropic(api_key=api_key)
        logger.info(f"Anthropic provider initialized with model: {model}")

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "Anthropic"

    def extract_transaction(self, document_path: str, categories: List[str]) -> ExtractionResult:
        """
        Extract transaction data from document using Anthropic Claude.

        Args:
            document_path: Path to document file
            categories: List of valid categories

        Returns:
            ExtractionResult with extracted data
        """
        start_time = time.time()
        self._request_count += 1

        try:
            # Prepare prompt
            prompt = self._prepare_prompt(categories)

            # Make API call with retry logic
            response = self.retry_with_backoff(self._make_api_call, document_path, prompt)

            # Parse response
            transaction_data = self._parse_response(response)

            # Validate response
            if not self.validate_response(transaction_data):
                return ExtractionResult(
                    success=False,
                    error_message="Response validation failed",
                    provider=self.provider_name,
                    processing_time=time.time() - start_time,
                )

            # Calculate confidence
            confidence = self._calculate_confidence(transaction_data)

            return ExtractionResult(
                success=True,
                transaction_data=transaction_data,
                confidence=confidence,
                provider=self.provider_name,
                processing_time=time.time() - start_time,
            )

        except Exception as e:
            logger.error(f"Anthropic extraction failed: {e}")
            return ExtractionResult(
                success=False,
                error_message=str(e),
                provider=self.provider_name,
                processing_time=time.time() - start_time,
            )

    def _prepare_prompt(self, categories: List[str]) -> str:
        """
        Prepare extraction prompt for Anthropic.

        Args:
            categories: List of valid categories

        Returns:
            Formatted prompt string
        """
        return create_standard_prompt(categories)

    def _make_api_call(self, document_path: str, prompt: str) -> Dict[str, Any]:
        """
        Make API call to Anthropic.

        Args:
            document_path: Path to document
            prompt: Extraction prompt

        Returns:
            API response

        Raises:
            APIKeyError: If API key is invalid
            RateLimitError: If rate limit exceeded
            ExtractionError: If extraction fails
        """
        try:
            # Read and encode image
            image_data, media_type = self._encode_image(document_path)

            # Prepare messages
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )

            return message

        except Exception as e:
            error_msg = str(e).lower()

            if "authentication" in error_msg or "api_key" in error_msg:
                raise APIKeyError(f"Invalid API key: {e}")
            elif "rate_limit" in error_msg or "quota" in error_msg:
                raise RateLimitError(f"Rate limit exceeded: {e}")
            else:
                raise ExtractionError(f"API call failed: {e}")

    def _encode_image(self, image_path: str) -> tuple:
        """
        Encode image to base64 and determine media type.

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (base64_data, media_type)
        """
        path = Path(image_path)
        suffix = path.suffix.lower()

        # Determine media type
        media_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }

        media_type = media_types.get(suffix, "image/jpeg")

        # Encode image
        with open(image_path, "rb") as image_file:
            image_data = base64.standard_b64encode(image_file.read()).decode("utf-8")

        return image_data, media_type

    def _parse_response(self, response) -> Dict[str, Any]:
        """
        Parse Anthropic API response to extract transaction data.

        Args:
            response: Anthropic API response

        Returns:
            Parsed transaction data

        Raises:
            ExtractionError: If parsing fails
        """
        try:
            # Get text content from response
            content = response.content[0].text

            # Clean up content
            content = content.strip()

            # Remove markdown code blocks if present
            if content.startswith("```"):
                lines = content.split("\n")
                json_lines = []
                in_json = False

                for line in lines:
                    if line.strip().startswith("```"):
                        in_json = not in_json
                        continue
                    if in_json or (not line.strip().startswith("```")):
                        json_lines.append(line)

                content = "\n".join(json_lines).strip()

            # Parse JSON
            data = json.loads(content)

            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response content: {content}")
            raise ExtractionError(f"Invalid JSON in response: {e}")
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            raise ExtractionError(f"Response parsing failed: {e}")

    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on data completeness.

        Args:
            data: Extracted transaction data

        Returns:
            Confidence score (0.0 to 1.0)
        """
        fields = {
            "date": 0.2,
            "transaction_type": 0.15,
            "amount": 0.2,
            "vendor_customer": 0.15,
            "description": 0.1,
            "category": 0.15,
            "tax_amount": 0.05,
        }

        score = 0.0

        for field, weight in fields.items():
            value = data.get(field)
            if value is not None and value != "":
                score += weight

        return round(score, 2)
