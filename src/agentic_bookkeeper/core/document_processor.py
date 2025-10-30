"""
Document processor for extracting transaction data.

This module coordinates document reading and LLM extraction.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
from PIL import Image
import pypdf

try:
    import fitz  # PyMuPDF

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from ..llm.llm_provider import LLMProvider, ExtractionResult
from ..models.transaction import Transaction
from ..utils.exceptions import DocumentError, ValidationError
from ..utils.error_handler import log_error_with_context, create_error_context
from ..utils.logger import log_operation_start, log_operation_success, log_operation_failure
import time

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Process financial documents and extract transaction data.

    Handles document type detection, preprocessing, and LLM extraction.
    """

    SUPPORTED_FORMATS = {".pdf", ".png", ".jpg", ".jpeg"}

    def __init__(self, llm_provider: LLMProvider, categories: List[str]):
        """
        Initialize document processor.

        Args:
            llm_provider: LLM provider instance
            categories: List of valid tax categories
        """
        self.llm_provider = llm_provider
        self.categories = categories
        logger.info(f"Document processor initialized with {llm_provider.provider_name}")

    def process_document(self, document_path: str, validate: bool = True) -> Optional[Transaction]:
        """
        Process a document and extract transaction data.

        Args:
            document_path: Path to document file
            validate: Whether to validate the extracted data

        Returns:
            Transaction object or None if extraction fails

        Raises:
            DocumentError: If document processing fails
        """
        start_time = time.time()
        context = create_error_context(
            operation="process_document",
            file_path=document_path,
        )

        try:
            path = Path(document_path)

            # Validate file exists
            if not path.exists():
                error = DocumentError(
                    user_message=f"Document not found: {path.name}",
                    document_path=document_path,
                    tech_message=f"FileNotFoundError: {document_path}",
                    recovery_suggestions=[
                        "Verify the file path is correct",
                        "Check that the file hasn't been moved or deleted",
                        "Ensure you have permission to access the file",
                        "Try browsing to the file location manually",
                    ],
                )
                log_error_with_context(error, context, severity="warning")
                raise error

            # Validate file format
            if path.suffix.lower() not in self.SUPPORTED_FORMATS:
                supported = ", ".join(self.SUPPORTED_FORMATS)
                error = DocumentError(
                    user_message=f"Unsupported file format: {path.suffix}",
                    document_path=document_path,
                    document_format=path.suffix,
                    tech_message=f"File format {path.suffix} not in supported formats: {supported}",
                    recovery_suggestions=[
                        f"Use a supported format: {supported}",
                        "Convert the document to PDF, PNG, or JPEG",
                        "Try re-scanning the document in a supported format",
                    ],
                )
                log_error_with_context(error, context, severity="warning")
                raise error

            log_operation_start(
                logger,
                "document_processing",
                document=path.name,
                provider=self.llm_provider.provider_name,
            )

            # Detect and preprocess document
            preprocessed_path = self._preprocess_document(document_path)

            # Extract transaction data using LLM
            result = self.llm_provider.extract_transaction(preprocessed_path, self.categories)

            # Check if extraction was successful
            if not result.success:
                error = DocumentError(
                    user_message=f"Failed to extract data from {path.name}",
                    document_path=document_path,
                    tech_message=f"LLM extraction failed: {result.error_message}",
                    recovery_suggestions=[
                        "Ensure the document is clear and readable",
                        "Try re-scanning the document with better quality",
                        "Check that the document contains financial information",
                        "Manually enter the transaction if automated extraction fails",
                    ],
                )
                log_error_with_context(error, context, severity="warning")
                raise error

            # Validate document type vs transaction type consistency
            self._validate_document_transaction_consistency(result.transaction_data)

            # Convert to Transaction object
            transaction = self._create_transaction_from_result(result, path.name)

            # Validate if requested
            if validate and transaction:
                try:
                    transaction.validate()
                except ValueError as e:
                    error = ValidationError(
                        user_message=f"Extracted transaction data is invalid: {str(e)}",
                        field="transaction",
                        value=transaction,
                        tech_message=str(e),
                        recovery_suggestions=[
                            "Review the extracted data in the document review dialog",
                            "Correct any incorrect values before saving",
                            "Ensure the document contains all required information (date, amount, vendor)",
                        ],
                    )
                    log_error_with_context(error, context, severity="warning")
                    raise error

            duration_ms = (time.time() - start_time) * 1000
            log_operation_success(
                logger,
                "document_processing",
                duration_ms=duration_ms,
                document=path.name,
                confidence=f"{result.confidence:.2f}",
            )

            return transaction

        except (DocumentError, ValidationError) as e:
            # Re-raise our custom exceptions after logging
            duration_ms = (time.time() - start_time) * 1000
            log_operation_failure(
                logger,
                "document_processing",
                e,
                document=Path(document_path).name,
                duration_ms=duration_ms,
            )
            raise
        except Exception as e:
            # Wrap unexpected errors
            duration_ms = (time.time() - start_time) * 1000
            log_operation_failure(
                logger,
                "document_processing",
                e,
                document=Path(document_path).name,
                duration_ms=duration_ms,
            )
            error = DocumentError(
                user_message=f"An unexpected error occurred while processing {Path(document_path).name}",
                document_path=document_path,
                tech_message=f"Unexpected error: {type(e).__name__}: {str(e)}",
                recovery_suggestions=[
                    "Try processing the document again",
                    "Restart the application if the problem persists",
                    "Check the log file for detailed error information",
                    "Contact support if you need assistance",
                ],
            )
            log_error_with_context(error, context, severity="error")
            raise error from e

    def _preprocess_document(self, document_path: str) -> str:
        """
        Preprocess document for extraction.

        For PDFs: Convert first page to image
        For images: Validate and optionally resize

        Args:
            document_path: Path to document

        Returns:
            Path to preprocessed document (will be an image file)

        Raises:
            Exception: If preprocessing fails
        """
        path = Path(document_path)
        suffix = path.suffix.lower()

        try:
            if suffix == ".pdf":
                # Convert PDF to image
                if not PYMUPDF_AVAILABLE:
                    raise ImportError(
                        "PyMuPDF (fitz) is required for PDF processing. "
                        "Install with: pip install pymupdf"
                    )

                logger.debug(f"Converting PDF to image: {path.name}")

                # Open PDF and get first page
                pdf_document = fitz.open(document_path)
                if len(pdf_document) == 0:
                    raise ValueError(f"PDF has no pages: {path.name}")

                # Render first page to pixmap (optimized resolution)
                page = pdf_document[0]
                # Use 200 DPI for good quality with better performance (matrix zoom factor = 200/72)
                # This provides a good balance between quality and file size
                # LLM vision models work well with 2048x2048 or smaller images
                mat = fitz.Matrix(2.78, 2.78)  # 200 DPI
                pix = page.get_pixmap(matrix=mat)

                # Create temporary file for the converted image
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".png", prefix=f"pdf_convert_{path.stem}_"
                )
                temp_path = temp_file.name
                temp_file.close()

                # Save the pixmap as PNG to the temporary file
                pix.save(temp_path)
                pdf_document.close()

                logger.debug(
                    f"Converted PDF {path.name} to image: {temp_path} "
                    f"(size: {pix.width}x{pix.height})"
                )

                return temp_path

            elif suffix in {".png", ".jpg", ".jpeg"}:
                # Validate and optimize image
                with Image.open(document_path) as img:
                    width, height = img.size
                    logger.debug(f"Image document: {path.name} ({width}x{height})")

                    # Optimize if image is too large (reduces memory and API payload)
                    max_dimension = 2048  # Max dimension for LLM vision models
                    if width > max_dimension or height > max_dimension:
                        # Calculate scaling factor to fit within max_dimension
                        scale = min(max_dimension / width, max_dimension / height)
                        new_width = int(width * scale)
                        new_height = int(height * scale)

                        # Resize image
                        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                        # Create temporary file for optimized image
                        temp_file = tempfile.NamedTemporaryFile(
                            delete=False, suffix=".jpg", prefix=f"img_optimized_{path.stem}_"
                        )
                        temp_path = temp_file.name
                        temp_file.close()

                        # Save as JPEG with quality 85 (good balance of quality/size)
                        img_resized.save(temp_path, "JPEG", quality=85, optimize=True)

                        logger.debug(
                            f"Optimized image {path.name}: "
                            f"{width}x{height} → {new_width}x{new_height} (saved to {temp_path})"
                        )

                        return temp_path

                # Image is already optimal size, use as-is
                return document_path

            else:
                raise ValueError(f"Unsupported format: {suffix}")

        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            raise

    def _create_transaction_from_result(
        self, result: ExtractionResult, document_filename: str
    ) -> Optional[Transaction]:
        """
        Create Transaction object from extraction result.

        Args:
            result: ExtractionResult from LLM
            document_filename: Original document filename

        Returns:
            Transaction object or None if creation fails
        """
        try:
            data = result.transaction_data

            # Helper function to safely convert to float, handling None values
            def safe_float(value, default=0.0):
                """Convert value to float, handling None and empty strings."""
                if value is None or value == "":
                    return default
                try:
                    return float(value)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert '{value}' to float, using default {default}")
                    return default

            # Create transaction with safe type conversion
            transaction = Transaction(
                date=data.get("date"),
                type=data.get("transaction_type"),
                category=data.get("category", "Other expenses"),
                vendor_customer=data.get("vendor_customer"),
                description=data.get("description"),
                amount=safe_float(data.get("amount"), 0.0),
                tax_amount=safe_float(data.get("tax_amount"), 0.0),
                document_filename=document_filename,
            )

            return transaction

        except Exception as e:
            logger.error(f"Failed to create transaction from result: {e}")
            return None

    def _validate_document_transaction_consistency(self, transaction_data: Dict[str, Any]) -> None:
        """
        Validate that document type matches expected transaction type.

        Invoices should be income, receipts should be expense.
        Logs warnings for inconsistencies but doesn't fail the extraction.

        Args:
            transaction_data: Extracted transaction data from LLM
        """
        if not transaction_data:
            return

        document_type = transaction_data.get("document_type", "").lower()
        transaction_type = transaction_data.get("transaction_type", "").lower()

        # Check for inconsistencies
        if document_type == "invoice" and transaction_type != "income":
            logger.warning(
                f"⚠️  INCONSISTENT CLASSIFICATION: Document is an INVOICE but "
                f"transaction type is '{transaction_type}'. "
                f"Invoices should typically be INCOME transactions. "
                f"This may indicate an extraction error."
            )

        elif document_type == "receipt" and transaction_type != "expense":
            logger.warning(
                f"⚠️  INCONSISTENT CLASSIFICATION: Document is a RECEIPT but "
                f"transaction type is '{transaction_type}'. "
                f"Receipts should typically be EXPENSE transactions. "
                f"This may indicate an extraction error."
            )

        # Log successful consistent classification
        elif document_type in ["invoice", "receipt"]:
            logger.debug(f"✓ Consistent classification: {document_type} → {transaction_type}")

    def extract_pdf_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF (fallback method).

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text
        """
        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = pypdf.PdfReader(file)
                text = ""

                for page in pdf_reader.pages:
                    text += page.extract_text()

                return text.strip()

        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            return ""

    def validate_extraction(
        self, transaction: Transaction, confidence_threshold: float = 0.7
    ) -> tuple:
        """
        Validate extracted transaction data.

        Args:
            transaction: Extracted transaction
            confidence_threshold: Minimum confidence score

        Returns:
            Tuple of (is_valid, validation_messages)
        """
        validation_messages = []
        is_valid = True

        # Check required fields
        if not transaction.date:
            validation_messages.append("Missing transaction date")
            is_valid = False

        if not transaction.amount or transaction.amount <= 0:
            validation_messages.append("Invalid or missing amount")
            is_valid = False

        if not transaction.category:
            validation_messages.append("Missing category")
            is_valid = False

        # Check category is valid
        if transaction.category and transaction.category not in self.categories:
            validation_messages.append(f"Category '{transaction.category}' not in valid categories")
            # Not a critical error, just a warning

        return is_valid, validation_messages

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported document formats.

        Returns:
            List of file extensions
        """
        return list(self.SUPPORTED_FORMATS)

    def change_provider(self, llm_provider: LLMProvider) -> None:
        """
        Change the LLM provider.

        Args:
            llm_provider: New LLM provider instance
        """
        self.llm_provider = llm_provider
        logger.info(f"LLM provider changed to {llm_provider.provider_name}")

    def get_provider_stats(self) -> Dict[str, Any]:
        """
        Get statistics from current LLM provider.

        Returns:
            Dictionary with provider statistics
        """
        return self.llm_provider.get_stats()
