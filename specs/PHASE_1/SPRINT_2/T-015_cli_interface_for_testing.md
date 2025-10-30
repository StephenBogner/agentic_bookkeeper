# Task Specification: T-015

**Task Name:** CLI Interface for Testing
**Task ID:** T-015
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 2: LLM Integration & Document Processing
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** High
**Estimated Effort:** 3 hours
**Dependencies:** T-012, T-013, T-014

---

## OBJECTIVE

Create a command-line interface for testing core functionality including document processing, transaction management, and monitoring before GUI implementation.

---

## REQUIREMENTS

### Functional Requirements

- Command to process single document
- Command to list transactions with filters
- Command to add/edit/delete transactions manually
- Command to start/stop directory monitoring
- Command to configure settings (API keys, directories)
- Command to test LLM providers
- Command to generate test reports
- Display help documentation for all commands
- Support for command arguments and options

### Non-Functional Requirements

- Clear, user-friendly output
- Colored output for better readability
- Error messages are helpful and actionable
- Support --help flag for all commands

---

## ACCEPTANCE CRITERIA

- [ ] CLI processes documents successfully
- [ ] All CRUD commands work for transactions
- [ ] Monitoring commands start/stop correctly
- [ ] Configuration commands update settings
- [ ] LLM provider test command validates setup
- [ ] Help documentation is clear
- [ ] Error messages are informative
- [ ] Can test full workflow via CLI
- [ ] Works from project root and as installed command

---

## EXPECTED DELIVERABLES

**Files to Create:**

- `cli.py` (in project root)

**Files to Modify:**

- `setup.py` or `pyproject.toml` (add CLI entry point)

---

## VALIDATION COMMANDS

```bash
# Test CLI commands
python cli.py --help
python cli.py process test_receipt.pdf
python cli.py list-transactions --type expense
python cli.py monitor start
python cli.py config set-api-key anthropic YOUR_KEY
python cli.py test-llm anthropic
```

---

## IMPLEMENTATION NOTES

### CLI Structure Using argparse

```python
#!/usr/bin/env python3
"""
Agentic Bookkeeper CLI
Command-line interface for testing and development.
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description='Agentic Bookkeeper CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Process command
    process_parser = subparsers.add_parser('process',
                                          help='Process a document')
    process_parser.add_argument('file', help='Path to document')
    process_parser.add_argument('--provider', default='anthropic',
                               help='LLM provider to use')

    # List transactions
    list_parser = subparsers.add_parser('list-transactions',
                                       help='List transactions')
    list_parser.add_argument('--type', choices=['income', 'expense'],
                            help='Filter by type')
    list_parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    list_parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')

    # Monitor command
    monitor_parser = subparsers.add_parser('monitor',
                                          help='Start/stop monitoring')
    monitor_parser.add_argument('action', choices=['start', 'stop'])

    # Config commands
    config_parser = subparsers.add_parser('config',
                                         help='Configuration management')
    config_parser.add_argument('action',
                              choices=['set-api-key', 'show', 'reset'])
    config_parser.add_argument('args', nargs='*', help='Arguments')

    # Test LLM
    test_parser = subparsers.add_parser('test-llm',
                                       help='Test LLM provider')
    test_parser.add_argument('provider',
                            choices=['openai', 'anthropic', 'xai', 'google'])

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == 'process':
        process_document(args.file, args.provider)
    elif args.command == 'list-transactions':
        list_transactions(args)
    # etc.

def process_document(file_path: str, provider: str):
    """Process a document."""
    print(f"Processing {file_path} with {provider}...")
    # Implementation

def list_transactions(args):
    """List transactions."""
    print("Transactions:")
    # Implementation

if __name__ == '__main__':
    main()
```

### Colored Output with colorama

```python
from colorama import Fore, Style, init

init(autoreset=True)

def print_success(msg: str):
    print(f"{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")

def print_error(msg: str):
    print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}")

def print_info(msg: str):
    print(f"{Fore.BLUE}ℹ {msg}{Style.RESET_ALL}")
```

### Command Examples

```bash
# Process document
python cli.py process documents/receipt.pdf --provider anthropic

# List transactions
python cli.py list-transactions --type expense --start-date 2025-01-01

# Add transaction manually
python cli.py add-transaction --date 2025-01-15 --type expense \
  --category "Office Supplies" --amount 45.99 --vendor "Staples"

# Start monitoring
python cli.py monitor start

# Configure API key
python cli.py config set-api-key anthropic sk-ant-xxxxx

# Test LLM provider
python cli.py test-llm anthropic

# Show configuration
python cli.py config show

# Generate test report
python cli.py report --type expense --start-date 2025-01-01
```

---

## NOTES

- CLI is for development and testing, not primary interface
- Use argparse for robust command parsing
- colorama provides cross-platform colored output
- Consider rich library for advanced formatting
- CLI should use same core classes as GUI
- Validate inputs before calling core functions
- Provide --verbose flag for detailed output
- Consider interactive mode for complex operations

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-016 - Unit Tests for LLM & Document Processing
