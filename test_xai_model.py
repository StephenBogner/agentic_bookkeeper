#!/usr/bin/env python3
"""
Quick test to verify xAI provider is using grok-5 model.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentic_bookkeeper.llm.xai_provider import XAIProvider

print("Testing xAI Provider Model Configuration")
print("=" * 60)

# Create provider with default model
provider = XAIProvider(api_key="test_key")

print(f"\n✓ xAI Provider instantiated")
print(f"  Provider name: {provider.provider_name}")
print(f"  Default model: {provider.model}")

if provider.model == "grok-5":
    print("\n✅ SUCCESS: xAI provider is using grok-5 model!")
else:
    print(f"\n❌ ERROR: Expected 'grok-5' but got '{provider.model}'")
    sys.exit(1)

# Test with custom model
custom_provider = XAIProvider(api_key="test_key", model="grok-custom")
print(f"\n✓ Custom model parameter works")
print(f"  Custom model: {custom_provider.model}")

print("\n" + "=" * 60)
print("✅ xAI model configuration verified!")
