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
import PyPDF2

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from ..llm.llm_provider import LLMProvider, ExtractionResult
from ..models.transaction import Transaction

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Process financial documents and extract transaction data.

    Handles document type detection, preprocessing, and LLM extraction.
    """

    SUPPORTED_FORMATS = {'.pdf', '.png', '.jpg', '.jpeg'}

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

    def process_document(
        self,
        document_path: str,
        validate: bool = True
    ) -> Optional[Transaction]:
        """
        Process a document and extract transaction data.

        Args:
            document_path: Path to document file
            validate: Whether to validate the extracted data

        Returns:
            Transaction object or None if extraction fails
        """
        try:
            path = Path(document_path)

            # Validate file exists
            if not path.exists():
                logger.error(f"Document not found: {document_path}")
                return None

            # Validate file format
            if path.suffix.lower() not in self.SUPPORTED_FORMATS:
                logger.error(f"Unsupported format: {path.suffix}")
                return None

            logger.info(f"Processing document: {path.name}")

            # Detect and preprocess document
            preprocessed_path = self._preprocess_document(document_path)

            # Extract transaction data using LLM
            result = self.llm_provider.extract_transaction(
                preprocessed_path,
                self.categories
            )

            # Check if extraction was successful
            if not result.success:
                logger.error(f"Extraction failed: {result.error_message}")
                return None

            # Convert to Transaction object
            transaction = self._create_transaction_from_result(
                result,
                path.name
            )

            # Validate if requested
            if validate and transaction:
                try:
                    transaction.validate()
                except ValueError as e:
                    logger.error(f"Transaction validation failed: {e}")
                    return None

            logger.info(
                f"Successfully extracted transaction from {path.name} "
                f"(confidence: {result.confidence:.2f})"
            )

            return transaction

        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return None

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
            if suffix == '.pdf':
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

                # Render first page to pixmap (high resolution for OCR)
                page = pdf_document[0]
                # Use 300 DPI for good quality (matrix zoom factor of 4.17 = 300/72)
                mat = fitz.Matrix(4.17, 4.17)
                pix = page.get_pixmap(matrix=mat)

                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(tempfile.NamedTemporaryFile(delete=False, suffix='.png'))

                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix='.png',
                    prefix=f"pdf_convert_{path.stem}_"
                )
                temp_path = temp_file.name
                temp_file.close()

                # Save the pixmap as PNG
                pix.save(temp_path)
                pdf_document.close()

                logger.debug(
                    f"Converted PDF {path.name} to image: {temp_path} "
                    f"(size: {pix.width}x{pix.height})"
                )

                return temp_path

            elif suffix in {'.png', '.jpg', '.jpeg'}:
                # Validate image can be opened
                with Image.open(document_path) as img:
                    logger.debug(f"Image document: {path.name} ({img.size})")

                # Could add image preprocessing here (resize, enhance, etc.)
                return document_path

            else:
                raise ValueError(f"Unsupported format: {suffix}")

        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            raise

    def _create_transaction_from_result(
        self,
        result: ExtractionResult,
        document_filename: str
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

            # Create transaction
            transaction = Transaction(
                date=data.get('date'),
                type=data.get('transaction_type'),
                category=data.get('category', 'Other expenses'),
                vendor_customer=data.get('vendor_customer'),
                description=data.get('description'),
                amount=float(data.get('amount', 0)),
                tax_amount=float(data.get('tax_amount', 0)),
                document_filename=document_filename
            )

            return transaction

        except Exception as e:
            logger.error(f"Failed to create transaction from result: {e}")
            return None

    def extract_pdf_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF (fallback method).

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""

                for page in pdf_reader.pages:
                    text += page.extract_text()

                return text.strip()

        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            return ""

    def validate_extraction(
        self,
        transaction: Transaction,
        confidence_threshold: float = 0.7
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
            validation_messages.append(
                f"Category '{transaction.category}' not in valid categories"
            )
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
