#!/usr/bin/env python3
"""
Quick test to verify PDF to image conversion is working.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentic_bookkeeper.core.document_processor import DocumentProcessor
from agentic_bookkeeper.llm.openai_provider import OpenAIProvider

print("Testing PDF to Image Conversion")
print("=" * 60)

# Get a test PDF
test_pdf = Path("samples/test_documents/receipt_office_supplies.pdf")

if not test_pdf.exists():
    print(f"❌ Test PDF not found: {test_pdf}")
    sys.exit(1)

print(f"\n✓ Test PDF found: {test_pdf}")

# Create provider and processor
provider = OpenAIProvider(api_key="test_key")
categories = ["Office expenses", "Meals & entertainment"]
processor = DocumentProcessor(provider, categories)

print(f"✓ DocumentProcessor created")

# Test preprocessing
try:
    print(f"\nAttempting to preprocess PDF...")
    converted_path = processor._preprocess_document(str(test_pdf))
    print(f"✓ PDF converted successfully!")
    print(f"  Converted image: {converted_path}")

    # Check if file exists and is valid
    converted_file = Path(converted_path)
    if converted_file.exists():
        file_size = converted_file.stat().st_size
        print(f"  File size: {file_size:,} bytes")

        # Try to open with PIL to verify it's a valid image
        from PIL import Image
        with Image.open(converted_path) as img:
            print(f"  Image dimensions: {img.size[0]} x {img.size[1]}")
            print(f"  Image format: {img.format}")

        # Clean up
        converted_file.unlink()
        print(f"  ✓ Temporary file cleaned up")

        print("\n" + "=" * 60)
        print("✅ PDF to Image Conversion Working!")
        sys.exit(0)
    else:
        print(f"❌ Converted file does not exist: {converted_path}")
        sys.exit(1)

except Exception as e:
    print(f"❌ Conversion failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
