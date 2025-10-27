"""
Google AI (Gemini) provider implementation for document extraction.

This module implements the LLM provider interface using Google's Gemini API.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-27
"""

import logging
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
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

logger = logging.getLogger(__name__)


class GoogleProvider(LLMProvider):
    """
    Google Gemini implementation of LLM provider.

    Uses Gemini's vision capabilities for document analysis and transaction extraction.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-pro",
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        Initialize Google Gemini provider.

        Args:
            api_key: Google API key
            model: Model to use (default: gemini-1.5-pro)
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        if not GOOGLE_AVAILABLE:
            raise ImportError(
                "google-generativeai package is required for Google provider. "
                "Install with: pip install google-generativeai"
            )

        super().__init__(api_key, max_retries, timeout)
        self.model = model

        # Configure Google AI
        genai.configure(api_key=api_key)

        # Initialize model with safety settings
        self.client = genai.GenerativeModel(
            model_name=model,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        logger.info(f"Initialized Google Gemini provider with model: {model}")

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "Google"

    def extract_transaction(
        self,
        document_path: str,
        categories: List[str]
    ) -> ExtractionResult:
        """
        Extract transaction data from document using Google Gemini.

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
            logger.error(f"Google extraction failed: {e}")
            return ExtractionResult(
                success=False,
                error_message=str(e),
                provider=self.provider_name,
                processing_time=time.time() - start_time
            )

    def _prepare_prompt(self, categories: List[str]) -> str:
        """
        Prepare extraction prompt for Google.

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
        Make API call to Google Gemini.

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
            # Read image data
            with open(document_path, "rb") as image_file:
                image_data = image_file.read()

            # Prepare image part
            image_part = {
                "mime_type": "image/png",
                "data": image_data
            }

            # Make API call
            response = self.client.generate_content(
                [prompt, image_part],
                generation_config={
                    "temperature": 0.0,  # Deterministic output
                    "max_output_tokens": 1000,
                }
            )

            return response

        except Exception as e:
            error_msg = str(e).lower()

            if "api_key" in error_msg or "invalid" in error_msg or "401" in error_msg:
                raise APIKeyError(f"Invalid API key: {e}")
            elif "quota" in error_msg or "rate" in error_msg or "429" in error_msg:
                raise RateLimitError(f"Rate limit exceeded: {e}")
            else:
                raise ExtractionError(f"API call failed: {e}")

    def _parse_response(self, response) -> Dict[str, Any]:
        """
        Parse Google Gemini API response to extract transaction data.

        Args:
            response: Google Gemini API response

        Returns:
            Parsed transaction data

        Raises:
            ExtractionError: If parsing fails
        """
        try:
            # Get response content
            content = response.text

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
            response = self.client.generate_content(
                "Test",
                generation_config={"max_output_tokens": 10}
            )
            return True
        except Exception as e:
            logger.error(f"Google connection test failed: {e}")
            return False
