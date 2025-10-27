"""
XAI (x.AI) provider implementation for document extraction.

This module implements the LLM provider interface using x.AI's Grok API.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-27
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
    create_standard_prompt
)

try:
    from openai import OpenAI  # xAI uses OpenAI-compatible API
    XAI_AVAILABLE = True
except ImportError:
    XAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class XAIProvider(LLMProvider):
    """
    xAI (Grok) implementation of LLM provider.

    Uses Grok's vision capabilities for document analysis and transaction extraction.
    The API is OpenAI-compatible but uses different base URL and models.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "grok-vision-beta",
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        Initialize xAI provider.

        Args:
            api_key: xAI API key
            model: Model to use (default: grok-vision-beta)
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        if not XAI_AVAILABLE:
            raise ImportError(
                "openai package is required for xAI provider. "
                "Install with: pip install openai"
            )

        super().__init__(api_key, max_retries, timeout)
        self.model = model

        # Initialize xAI client with OpenAI-compatible API
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            timeout=timeout
        )

        logger.info(f"Initialized xAI provider with model: {model}")

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "xAI"

    def extract_transaction(
        self,
        document_path: str,
        categories: List[str]
    ) -> ExtractionResult:
        """
        Extract transaction data from document using xAI Grok.

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
            response = self.retry_with_backoff(
                self._make_api_call,
                document_path,
                prompt
            )

            # Parse response
            transaction_data = self._parse_response(response)

            # Validate response
            if not self.validate_response(transaction_data):
                return ExtractionResult(
                    success=False,
                    error_message="Response validation failed",
                    provider=self.provider_name,
                    processing_time=time.time() - start_time
                )

            # Calculate confidence (simple heuristic based on field completeness)
            confidence = self._calculate_confidence(transaction_data)

            return ExtractionResult(
                success=True,
                transaction_data=transaction_data,
                confidence=confidence,
                provider=self.provider_name,
                processing_time=time.time() - start_time
            )

        except Exception as e:
            logger.error(f"xAI extraction failed: {e}")
            return ExtractionResult(
                success=False,
                error_message=str(e),
                provider=self.provider_name,
                processing_time=time.time() - start_time
            )

    def _prepare_prompt(self, categories: List[str]) -> str:
        """
        Prepare extraction prompt for xAI.

        Args:
            categories: List of valid categories

        Returns:
            Formatted prompt string
        """
        return create_standard_prompt(categories)

    def _make_api_call(
        self,
        document_path: str,
        prompt: str
    ) -> Dict[str, Any]:
        """
        Make API call to xAI.

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
            image_data = self._encode_image(document_path)

            # Prepare messages
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]

            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.0  # Deterministic output
            )

            return response

        except Exception as e:
            error_msg = str(e).lower()

            if "invalid" in error_msg and "api" in error_msg:
                raise APIKeyError(f"Invalid API key: {e}")
            elif "rate" in error_msg or "quota" in error_msg:
                raise RateLimitError(f"Rate limit exceeded: {e}")
            else:
                raise ExtractionError(f"API call failed: {e}")

    def _encode_image(self, image_path: str) -> str:
        """
        Encode image to base64.

        Args:
            image_path: Path to image file

        Returns:
            Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _parse_response(self, response) -> Dict[str, Any]:
        """
        Parse xAI API response to extract transaction data.

        Args:
            response: xAI API response

        Returns:
            Parsed transaction data

        Raises:
            ExtractionError: If parsing fails
        """
        try:
            # Get response content
            content = response.choices[0].message.content

            # Parse JSON from response
            # Sometimes the model adds markdown formatting, so we need to extract JSON
            content = content.strip()

            # Remove markdown code blocks if present
            if content.startswith("```"):
                # Find JSON content between code blocks
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
        # Fields and their weights
        fields = {
            'date': 0.2,
            'transaction_type': 0.15,
            'amount': 0.2,
            'vendor_customer': 0.15,
            'description': 0.1,
            'category': 0.15,
            'tax_amount': 0.05
        }

        score = 0.0

        for field, weight in fields.items():
            value = data.get(field)
            if value is not None and value != "":
                score += weight

        return round(score, 2)

    def test_connection(self) -> bool:
        """
        Test API connection and credentials.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Make a simple API call to test connection
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"xAI connection test failed: {e}")
            return False
