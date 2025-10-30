#!/usr/bin/env python3
"""
Real-world testing of LLM providers with actual documents.

This script tests all LLM providers (OpenAI, Anthropic, xAI, Google)
with the generated test documents to validate extraction accuracy.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-27
"""

import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agentic_bookkeeper.utils.config import Config
from agentic_bookkeeper.core.document_processor import DocumentProcessor
from agentic_bookkeeper.llm.openai_provider import OpenAIProvider
from agentic_bookkeeper.llm.anthropic_provider import AnthropicProvider
from agentic_bookkeeper.llm.xai_provider import XAIProvider
from agentic_bookkeeper.llm.google_provider import GoogleProvider


def test_provider(provider_name: str, provider, test_documents: list, categories: list):
    """
    Test a specific LLM provider with test documents.

    Args:
        provider_name: Name of the provider
        provider: Provider instance
        test_documents: List of test document paths
        categories: List of valid categories
    """
    print(f"\n{'='*80}")
    print(f"Testing {provider_name} Provider")
    print(f"{'='*80}\n")

    # Create document processor with this provider
    processor = DocumentProcessor(provider, categories)

    results = []
    total_time = 0

    for doc_path in test_documents:
        print(f"\n📄 Processing: {doc_path.name}")
        print("-" * 60)

        try:
            start_time = time.time()
            transaction = processor.process_document(str(doc_path))
            processing_time = time.time() - start_time
            total_time += processing_time

            if transaction:
                print(f"✅ SUCCESS ({processing_time:.2f}s)")
                print(f"   Date: {transaction.date}")
                print(f"   Type: {transaction.type}")
                print(f"   Category: {transaction.category}")
                print(f"   Vendor/Customer: {transaction.vendor_customer}")
                print(f"   Amount: ${transaction.amount:.2f}")
                if transaction.tax_amount > 0:
                    print(f"   Tax: ${transaction.tax_amount:.2f}")
                print(f"   Description: {transaction.description}")

                results.append({
                    'document': doc_path.name,
                    'success': True,
                    'time': processing_time,
                    'transaction': transaction
                })
            else:
                print(f"❌ FAILED: No transaction extracted")
                results.append({
                    'document': doc_path.name,
                    'success': False,
                    'time': processing_time,
                    'error': 'No transaction extracted'
                })

        except Exception as e:
            processing_time = time.time() - start_time
            print(f"❌ FAILED: {e}")
            results.append({
                'document': doc_path.name,
                'success': False,
                'time': processing_time,
                'error': str(e)
            })

    # Summary
    print(f"\n{'='*80}")
    print(f"{provider_name} Provider Summary")
    print(f"{'='*80}")

    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    print(f"\nDocuments Processed: {len(results)}")
    print(f"Successful: {successful} ({successful/len(results)*100:.1f}%)")
    print(f"Failed: {failed} ({failed/len(results)*100:.1f}%)")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Average Time: {total_time/len(results):.2f}s per document")

    if failed > 0:
        print(f"\nFailed Documents:")
        for result in results:
            if not result['success']:
                print(f"  - {result['document']}: {result['error']}")

    return results


def main():
    """Run real-world tests on all LLM providers."""
    print("\n" + "="*80)
    print("LLM Provider Real-World Testing")
    print("="*80)

    # Load configuration
    config = Config()
    categories = config.get_categories()

    # Get test documents
    test_dir = Path("samples/test_documents")
    if not test_dir.exists():
        print(f"\n❌ Error: Test documents directory not found: {test_dir}")
        print("   Run generate_test_documents.py first to create test documents.")
        return 1

    test_documents = sorted(test_dir.glob("*.pdf"))
    if not test_documents:
        print(f"\n❌ Error: No PDF test documents found in {test_dir}")
        return 1

    print(f"\nTest Documents Found: {len(test_documents)}")
    for doc in test_documents:
        print(f"  - {doc.name}")

    print(f"\nCategories: {len(categories)} loaded from config")

    # Test results storage
    all_results = {}

    # Test OpenAI Provider
    print("\n" + "="*80)
    print("1/4: Testing OpenAI Provider")
    print("="*80)

    api_key = config.get_api_key('openai')
    if api_key:
        try:
            provider = OpenAIProvider(api_key)
            all_results['openai'] = test_provider('OpenAI', provider, test_documents, categories)
        except Exception as e:
            print(f"\n❌ Failed to initialize OpenAI provider: {e}")
            all_results['openai'] = None
    else:
        print("\n⚠️ OpenAI API key not configured, skipping...")
        all_results['openai'] = None

    # Test Anthropic Provider
    print("\n" + "="*80)
    print("2/4: Testing Anthropic Provider")
    print("="*80)

    api_key = config.get_api_key('anthropic')
    if api_key:
        try:
            provider = AnthropicProvider(api_key)
            all_results['anthropic'] = test_provider('Anthropic', provider, test_documents, categories)
        except Exception as e:
            print(f"\n❌ Failed to initialize Anthropic provider: {e}")
            all_results['anthropic'] = None
    else:
        print("\n⚠️ Anthropic API key not configured, skipping...")
        all_results['anthropic'] = None

    # Test xAI Provider
    print("\n" + "="*80)
    print("3/4: Testing xAI Provider")
    print("="*80)

    api_key = config.get_api_key('xai')
    if api_key:
        try:
            provider = XAIProvider(api_key)
            all_results['xai'] = test_provider('xAI', provider, test_documents, categories)
        except Exception as e:
            print(f"\n❌ Failed to initialize xAI provider: {e}")
            all_results['xai'] = None
    else:
        print("\n⚠️ xAI API key not configured, skipping...")
        all_results['xai'] = None

    # Test Google Provider
    print("\n" + "="*80)
    print("4/4: Testing Google Provider")
    print("="*80)

    api_key = config.get_api_key('google')
    if api_key:
        try:
            provider = GoogleProvider(api_key)
            all_results['google'] = test_provider('Google', provider, test_documents, categories)
        except Exception as e:
            print(f"\n❌ Failed to initialize Google provider: {e}")
            all_results['google'] = None
    else:
        print("\n⚠️ Google API key not configured, skipping...")
        all_results['google'] = None

    # Final Summary
    print("\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80)

    print("\nProvider Comparison:")
    print(f"{'Provider':<15} {'Tested':<10} {'Success Rate':<15} {'Avg Time':<12}")
    print("-" * 60)

    for provider_name, results in all_results.items():
        if results:
            successful = sum(1 for r in results if r['success'])
            success_rate = f"{successful}/{len(results)} ({successful/len(results)*100:.1f}%)"
            avg_time = f"{sum(r['time'] for r in results)/len(results):.2f}s"
            print(f"{provider_name.capitalize():<15} {'Yes':<10} {success_rate:<15} {avg_time:<12}")
        else:
            print(f"{provider_name.capitalize():<15} {'No':<10} {'N/A':<15} {'N/A':<12}")

    print("\n✅ Real-world testing complete!")
    print(f"\nTest documents available in: {test_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
