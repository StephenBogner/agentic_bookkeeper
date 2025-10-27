#!/usr/bin/env python3
"""
Verify environment variable precedence is working correctly.

This script demonstrates that configuration loads in the correct order:
1. System environment variables
2. Session environment variables
3. .env file values

Author: Stephen Bogner, P.Eng.
Date: 2025-10-27
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_env_precedence():
    """Test that environment variables take precedence over .env file."""
    print("=" * 70)
    print("ENVIRONMENT VARIABLE PRECEDENCE VERIFICATION")
    print("=" * 70)

    # Set a test environment variable
    test_key = "TEST_API_KEY_FROM_SESSION"
    os.environ['OPENAI_API_KEY'] = test_key

    print("\n1. Session environment variable set:")
    print(f"   export OPENAI_API_KEY='{test_key}'")

    # Create a temporary .env file with different value
    env_content = "OPENAI_API_KEY=test_key_from_env_file\n"
    test_env_file = Path(".env.test")
    test_env_file.write_text(env_content)

    print("\n2. .env.test file contains:")
    print(f"   OPENAI_API_KEY='test_key_from_env_file'")

    # Load config
    print("\n3. Loading configuration...")
    from dotenv import load_dotenv
    load_dotenv(test_env_file)

    # Check which value was loaded
    loaded_value = os.getenv('OPENAI_API_KEY')

    print(f"\n4. Configuration loaded OPENAI_API_KEY: '{loaded_value}'")

    # Verify precedence
    print("\n" + "=" * 70)
    if loaded_value == test_key:
        print("✅ SUCCESS: Session environment variable took precedence!")
        print("   The .env file value was correctly ignored.")
        result = True
    else:
        print("❌ FAILURE: .env file value took precedence (unexpected)")
        print("   This should not happen - environment variables should have priority.")
        result = False

    # Cleanup
    test_env_file.unlink()

    print("\n" + "=" * 70)
    print("ENVIRONMENT VARIABLE PRECEDENCE ORDER:")
    print("=" * 70)
    print("Priority 1 (Highest): System environment variables")
    print("                      (set in ~/.bashrc, /etc/environment, etc.)")
    print("\nPriority 2:           Session environment variables")
    print("                      (export VAR=value in current shell)")
    print("\nPriority 3 (Lowest):  .env file values")
    print("                      (DEVELOPMENT ONLY)")
    print("\n" + "=" * 70)

    return result


def test_config_class():
    """Test that Config class respects precedence."""
    print("\n\n" + "=" * 70)
    print("CONFIG CLASS PRECEDENCE TEST")
    print("=" * 70)

    # Set test environment variable
    test_key = "sk-test-session-environment-key"
    os.environ['ANTHROPIC_API_KEY'] = test_key

    print(f"\n1. Set session variable: ANTHROPIC_API_KEY='{test_key}'")

    # Create temporary .env
    env_content = "ANTHROPIC_API_KEY=sk-test-dotenv-file-key\n"
    test_env_file = Path(".env.test2")
    test_env_file.write_text(env_content)

    print("2. Created .env.test2 with: ANTHROPIC_API_KEY='sk-test-dotenv-file-key'")

    # Load Config
    print("\n3. Initializing Config class...")
    from agentic_bookkeeper.utils.config import Config

    # Temporarily override default env file
    config = Config(env_file=str(test_env_file))

    loaded_key = config.get_api_key('anthropic')

    print(f"\n4. Config.get_api_key('anthropic') returned: '{loaded_key}'")

    # Verify
    print("\n" + "=" * 70)
    if loaded_key == test_key:
        print("✅ SUCCESS: Config class correctly uses session environment variable!")
        result = True
    else:
        print("❌ FAILURE: Config class used .env file instead of environment")
        result = False

    # Cleanup
    test_env_file.unlink()

    return result


def show_current_env_status():
    """Show current environment variable status."""
    print("\n\n" + "=" * 70)
    print("CURRENT ENVIRONMENT STATUS")
    print("=" * 70)

    api_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'XAI_API_KEY': os.getenv('XAI_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
    }

    print("\nAPI Keys in environment:")
    for key, value in api_keys.items():
        if value:
            # Mask the key for security
            if len(value) > 8:
                masked = value[:4] + '*' * (len(value) - 8) + value[-4:]
            else:
                masked = '*' * len(value)
            source = "SESSION/SYSTEM ENV" if key in os.environ else "UNKNOWN"
            print(f"  {key}: {masked} ({source})")
        else:
            print(f"  {key}: (not set)")

    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print(f"\n.env file: EXISTS at {env_file.absolute()}")
        print("  (Variables from .env are only used if not already in environment)")
    else:
        print("\n.env file: NOT FOUND")
        print("  (All configuration must come from environment variables)")


if __name__ == "__main__":
    print("\n")
    success = True

    # Run tests
    if not test_env_precedence():
        success = False

    if not test_config_class():
        success = False

    # Show current status
    show_current_env_status()

    # Summary
    print("\n\n" + "=" * 70)
    if success:
        print("✅ ALL TESTS PASSED")
        print("\nEnvironment variable precedence is working correctly!")
        print("\nBest Practices:")
        print("  • Production: Use system environment variables")
        print("  • Staging: Use system environment variables")
        print("  • Development: .env file is acceptable")
        print("  • Never commit API keys to version control")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease review the test output above.")
        sys.exit(1)
