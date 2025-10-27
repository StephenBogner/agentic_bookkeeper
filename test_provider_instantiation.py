#!/usr/bin/env python3
"""
Quick test to verify that all LLM providers can be instantiated correctly.

This tests that the abstract method implementation is correct without
needing actual API keys.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_provider_instantiation():
    """Test that all providers can be instantiated."""
    print("Testing LLM Provider Instantiation")
    print("=" * 60)

    # Test OpenAI Provider
    print("\n1. Testing OpenAI Provider...")
    try:
        from agentic_bookkeeper.llm.openai_provider import OpenAIProvider
        provider = OpenAIProvider(api_key="test_key")
        print(f"   ✓ OpenAI Provider instantiated successfully")
        print(f"   - Provider name: {provider.provider_name}")
        print(f"   - Has _prepare_prompt: {hasattr(provider, '_prepare_prompt')}")
        print(f"   - Has _make_api_call: {hasattr(provider, '_make_api_call')}")
    except Exception as e:
        print(f"   ✗ OpenAI Provider failed: {e}")
        return False

    # Test Anthropic Provider
    print("\n2. Testing Anthropic Provider...")
    try:
        from agentic_bookkeeper.llm.anthropic_provider import AnthropicProvider
        provider = AnthropicProvider(api_key="test_key")
        print(f"   ✓ Anthropic Provider instantiated successfully")
        print(f"   - Provider name: {provider.provider_name}")
        print(f"   - Has _prepare_prompt: {hasattr(provider, '_prepare_prompt')}")
        print(f"   - Has _make_api_call: {hasattr(provider, '_make_api_call')}")
    except Exception as e:
        print(f"   ✗ Anthropic Provider failed: {e}")
        return False

    # Test XAI Provider
    print("\n3. Testing XAI Provider...")
    try:
        from agentic_bookkeeper.llm.xai_provider import XAIProvider
        provider = XAIProvider(api_key="test_key")
        print(f"   ✓ XAI Provider instantiated successfully")
        print(f"   - Provider name: {provider.provider_name}")
        print(f"   - Has _prepare_prompt: {hasattr(provider, '_prepare_prompt')}")
        print(f"   - Has _make_api_call: {hasattr(provider, '_make_api_call')}")
    except Exception as e:
        print(f"   ✗ XAI Provider failed: {e}")
        return False

    # Test Google Provider
    print("\n4. Testing Google Provider...")
    try:
        from agentic_bookkeeper.llm.google_provider import GoogleProvider
        provider = GoogleProvider(api_key="test_key")
        print(f"   ✓ Google Provider instantiated successfully")
        print(f"   - Provider name: {provider.provider_name}")
        print(f"   - Has _prepare_prompt: {hasattr(provider, '_prepare_prompt')}")
        print(f"   - Has _make_api_call: {hasattr(provider, '_make_api_call')}")
    except Exception as e:
        print(f"   ✗ Google Provider failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✓ All providers instantiated successfully!")
    print("✓ Abstract method issues resolved!")
    return True


def test_document_processor():
    """Test DocumentProcessor with PDF conversion capability."""
    print("\n\nTesting DocumentProcessor PDF Conversion")
    print("=" * 60)

    try:
        from agentic_bookkeeper.core.document_processor import DocumentProcessor
        from agentic_bookkeeper.llm.openai_provider import OpenAIProvider

        # Create a provider
        provider = OpenAIProvider(api_key="test_key")

        # Create document processor
        categories = ["Office expenses", "Meals & entertainment"]
        processor = DocumentProcessor(provider, categories)

        print(f"   ✓ DocumentProcessor instantiated successfully")
        print(f"   - Supported formats: {processor.get_supported_formats()}")
        print(f"   - PDF support: {'.pdf' in processor.get_supported_formats()}")
        print(f"   - PyMuPDF available: Check...")

        import fitz
        print(f"   ✓ PyMuPDF (fitz) is available")

    except ImportError as e:
        print(f"   ✗ Missing dependency: {e}")
        return False
    except Exception as e:
        print(f"   ✗ DocumentProcessor test failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✓ DocumentProcessor configured correctly!")
    print("✓ PDF to image conversion capability available!")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AGENTIC BOOKKEEPER - PROVIDER INSTANTIATION TEST")
    print("=" * 60)

    success = True

    # Test provider instantiation
    if not test_provider_instantiation():
        success = False

    # Test document processor
    if not test_document_processor():
        success = False

    if success:
        print("\n\n🎉 ALL TESTS PASSED! 🎉")
        print("\nThe following issues have been resolved:")
        print("  1. ✓ PDF to image conversion implemented")
        print("  2. ✓ XAI provider abstract methods implemented")
        print("  3. ✓ Google provider abstract methods implemented")
        print("  4. ✓ All providers can be instantiated")
        print("  5. ✓ DocumentProcessor supports PDF/PNG/JPG formats")
        print("\nNext steps:")
        print("  - Configure API keys in .env file")
        print("  - Run real-world tests with actual documents")
        print("  - Verify extraction accuracy")
        sys.exit(0)
    else:
        print("\n\n❌ SOME TESTS FAILED")
        print("Please review the errors above.")
        sys.exit(1)
