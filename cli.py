#!/usr/bin/env python3
"""
Command-line interface for Agentic Bookkeeper.

This CLI provides commands for testing and managing the bookkeeper system.

Author: Stephen Bogner, P.Eng.
Date: 2025-10-24
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from agentic_bookkeeper.models.database import Database
from agentic_bookkeeper.models.transaction import Transaction
from agentic_bookkeeper.core.transaction_manager import TransactionManager
from agentic_bookkeeper.core.document_processor import DocumentProcessor
from agentic_bookkeeper.core.document_monitor import DocumentMonitor
from agentic_bookkeeper.llm.openai_provider import OpenAIProvider
from agentic_bookkeeper.llm.anthropic_provider import AnthropicProvider
from agentic_bookkeeper.utils.config import Config
from agentic_bookkeeper.utils.logger import setup_logging


def cmd_init_db(args):
    """Initialize database."""
    db = Database(args.db_path)
    db.initialize_schema()
    print(f"✓ Database initialized: {args.db_path}")

    stats = db.get_database_stats()
    print(f"  Schema version: {stats['schema_version']}")
    print(f"  Transactions: {stats['transaction_count']}")
    db.close()


def cmd_list_transactions(args):
    """List transactions."""
    db = Database(args.db_path)
    db.initialize_schema()

    tm = TransactionManager(db)
    transactions = tm.get_all_transactions(limit=args.limit)

    if not transactions:
        print("No transactions found.")
    else:
        print(f"\n{'ID':<5} {'Date':<12} {'Type':<8} {'Amount':>10} {'Category':<20} {'Vendor':<20}")
        print("-" * 90)

        for trans in transactions:
            print(
                f"{trans.id:<5} {trans.date:<12} {trans.type:<8} "
                f"${trans.amount:>9.2f} {trans.category:<20} {trans.vendor_customer or 'N/A':<20}"
            )

        print(f"\nTotal: {len(transactions)} transactions")

    db.close()


def cmd_add_transaction(args):
    """Add a transaction manually."""
    db = Database(args.db_path)
    db.initialize_schema()

    try:
        trans = Transaction(
            date=args.date,
            type=args.type,
            category=args.category,
            vendor_customer=args.vendor,
            description=args.description,
            amount=args.amount,
            tax_amount=args.tax_amount or 0.0
        )

        tm = TransactionManager(db)
        trans_id = tm.create_transaction(trans)

        print(f"✓ Transaction created with ID: {trans_id}")
        print(f"  Date: {trans.date}")
        print(f"  Type: {trans.type}")
        print(f"  Amount: ${trans.amount:.2f}")

    except ValueError as e:
        print(f"✗ Error: {e}")
        return 1
    finally:
        db.close()


def cmd_process_document(args):
    """Process a single document."""
    # Load config
    config = Config()

    # Get API key for provider
    api_key = config.get_api_key(args.provider)
    if not api_key:
        print(f"✗ Error: No API key configured for {args.provider}")
        print("  Set API key in .env file")
        return 1

    # Create LLM provider
    if args.provider == 'openai':
        try:
            provider = OpenAIProvider(api_key)
        except ImportError:
            print("✗ Error: OpenAI package not installed")
            print("  Install with: pip install openai")
            return 1
    elif args.provider == 'anthropic':
        try:
            provider = AnthropicProvider(api_key)
        except ImportError:
            print("✗ Error: Anthropic package not installed")
            print("  Install with: pip install anthropic")
            return 1
    else:
        print(f"✗ Error: Unknown provider: {args.provider}")
        return 1

    # Get categories
    categories = config.get_categories()

    # Create processor
    processor = DocumentProcessor(provider, categories)

    # Process document
    print(f"Processing document: {args.document}")
    print(f"Provider: {provider.provider_name}")

    transaction = processor.process_document(args.document)

    if transaction:
        print("\n✓ Extraction successful!")
        print(f"  Date: {transaction.date}")
        print(f"  Type: {transaction.type}")
        print(f"  Category: {transaction.category}")
        print(f"  Vendor/Customer: {transaction.vendor_customer}")
        print(f"  Amount: ${transaction.amount:.2f}")
        print(f"  Tax Amount: ${transaction.tax_amount:.2f}")
        print(f"  Description: {transaction.description}")

        # Save to database if requested
        if args.save:
            db = Database(args.db_path)
            db.initialize_schema()
            tm = TransactionManager(db)
            trans_id = tm.create_transaction(transaction)
            print(f"\n✓ Saved to database with ID: {trans_id}")
            db.close()
    else:
        print("\n✗ Extraction failed")
        return 1


def cmd_start_monitor(args):
    """Start monitoring directory."""
    # Load config
    config = Config()

    watch_dir = args.watch_dir or str(config.get_watch_directory())
    processed_dir = args.processed_dir or str(config.get_processed_directory())

    print(f"Starting document monitor...")
    print(f"  Watch directory: {watch_dir}")
    print(f"  Processed directory: {processed_dir}")
    print(f"  Provider: {args.provider}")

    # Get API key
    api_key = config.get_api_key(args.provider)
    if not api_key:
        print(f"✗ Error: No API key configured for {args.provider}")
        return 1

    # Create provider
    if args.provider == 'openai':
        try:
            provider = OpenAIProvider(api_key)
        except ImportError:
            print("✗ Error: OpenAI package not installed")
            return 1
    elif args.provider == 'anthropic':
        try:
            provider = AnthropicProvider(api_key)
        except ImportError:
            print("✗ Error: Anthropic package not installed")
            return 1
    else:
        print(f"✗ Error: Unknown provider: {args.provider}")
        return 1

    # Initialize database
    db = Database(args.db_path)
    db.initialize_schema()
    tm = TransactionManager(db)

    # Create processor
    categories = config.get_categories()
    processor = DocumentProcessor(provider, categories)

    # Document callback
    def on_document(file_path):
        print(f"\n📄 New document: {Path(file_path).name}")
        transaction = processor.process_document(file_path)

        if transaction:
            print(f"  ✓ Extracted: {transaction.type} ${transaction.amount:.2f}")
            trans_id = tm.create_transaction(transaction)
            print(f"  ✓ Saved with ID: {trans_id}")
        else:
            print("  ✗ Extraction failed")

    # Create and start monitor
    monitor = DocumentMonitor(
        watch_directory=watch_dir,
        processed_directory=processed_dir,
        on_document_callback=on_document
    )

    print("\n✓ Monitor started. Press Ctrl+C to stop.")
    print("  Drop documents in the watch directory to process them.\n")

    try:
        monitor.start()

        # Process existing files
        if args.process_existing:
            print("Processing existing files...")
            monitor.process_existing_files()

        # Keep running
        import time
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nStopping monitor...")
        monitor.stop()
        print("✓ Monitor stopped")
    finally:
        db.close()


def cmd_stats(args):
    """Show database statistics."""
    db = Database(args.db_path)
    db.initialize_schema()

    # Database stats
    stats = db.get_database_stats()
    print("\nDatabase Statistics")
    print("=" * 50)
    print(f"Database: {stats['db_path']}")
    print(f"Size: {stats['db_size_mb']:.2f} MB")
    print(f"Schema version: {stats['schema_version']}")
    print(f"Total transactions: {stats['transaction_count']}")

    if stats['first_transaction_date']:
        print(f"First transaction: {stats['first_transaction_date']}")
        print(f"Last transaction: {stats['last_transaction_date']}")

    # Transaction stats
    tm = TransactionManager(db)
    trans_stats = tm.get_transaction_statistics()

    print("\nTransaction Summary")
    print("=" * 50)
    print(f"Income:   {trans_stats['income']['count']:>5} transactions, ${trans_stats['income']['total']:>10.2f}")
    print(f"Expense:  {trans_stats['expense']['count']:>5} transactions, ${trans_stats['expense']['total']:>10.2f}")
    print(f"Net:      {' ' * 5}                ${trans_stats['net']:>10.2f}")

    # Category summary
    if args.categories:
        print("\nExpense by Category")
        print("=" * 50)
        category_summary = tm.get_category_summary(transaction_type='expense')

        for category, total in sorted(category_summary.items(), key=lambda x: x[1], reverse=True):
            print(f"{category:<30} ${total:>10.2f}")

    db.close()


def cmd_config(args):
    """Show configuration."""
    config = Config()

    print("\nConfiguration")
    print("=" * 50)
    print(f"LLM Provider: {config.get('llm_provider')}")
    print(f"Tax Jurisdiction: {config.get('tax_jurisdiction')}")
    print(f"Fiscal Year Start: {config.get('fiscal_year_start')}")
    print(f"Watch Directory: {config.get_watch_directory()}")
    print(f"Processed Directory: {config.get_processed_directory()}")
    print(f"Database: {config.get_database_path()}")
    print(f"Log Level: {config.get_log_level()}")

    # API keys (masked)
    print("\nAPI Keys")
    print("=" * 50)
    for provider in ['openai', 'anthropic', 'xai', 'google']:
        key = config.get_api_key(provider)
        status = "✓ Configured" if key else "✗ Not set"
        print(f"{provider.capitalize():<15} {status}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Agentic Bookkeeper - CLI for testing and management",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Global arguments
    parser.add_argument(
        '--db-path',
        default='./data/bookkeeper.db',
        help='Database path (default: ./data/bookkeeper.db)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Init database command
    init_parser = subparsers.add_parser('init', help='Initialize database')

    # List transactions command
    list_parser = subparsers.add_parser('list', help='List transactions')
    list_parser.add_argument('--limit', type=int, default=20, help='Maximum transactions to show')

    # Add transaction command
    add_parser = subparsers.add_parser('add', help='Add transaction manually')
    add_parser.add_argument('--date', required=True, help='Transaction date (YYYY-MM-DD)')
    add_parser.add_argument('--type', required=True, choices=['income', 'expense'], help='Transaction type')
    add_parser.add_argument('--category', required=True, help='Category')
    add_parser.add_argument('--amount', type=float, required=True, help='Amount')
    add_parser.add_argument('--vendor', help='Vendor or customer name')
    add_parser.add_argument('--description', help='Description')
    add_parser.add_argument('--tax-amount', type=float, help='Tax amount')

    # Process document command
    process_parser = subparsers.add_parser('process', help='Process a document')
    process_parser.add_argument('document', help='Path to document')
    process_parser.add_argument('--provider', default='openai', choices=['openai', 'anthropic'], help='LLM provider')
    process_parser.add_argument('--save', action='store_true', help='Save to database')

    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Start monitoring directory')
    monitor_parser.add_argument('--provider', default='openai', choices=['openai', 'anthropic'], help='LLM provider')
    monitor_parser.add_argument('--watch-dir', help='Directory to watch')
    monitor_parser.add_argument('--processed-dir', help='Directory for processed files')
    monitor_parser.add_argument('--process-existing', action='store_true', help='Process existing files on startup')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.add_argument('--categories', action='store_true', help='Show category breakdown')

    # Config command
    config_parser = subparsers.add_parser('config', help='Show configuration')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Set up logging
    setup_logging(log_level='INFO', console_output=True)

    # Execute command
    commands = {
        'init': cmd_init_db,
        'list': cmd_list_transactions,
        'add': cmd_add_transaction,
        'process': cmd_process_document,
        'monitor': cmd_start_monitor,
        'stats': cmd_stats,
        'config': cmd_config
    }

    return commands[args.command](args) or 0


if __name__ == '__main__':
    sys.exit(main())
