# CLI Test Script Documentation

## Overview

The `test_cli.sh` script provides comprehensive testing of all CLI commands for the Agentic Bookkeeper application. It ensures that all functionality works correctly and validates input handling.

## Running the Test Script

```bash
# Make the script executable (if needed)
chmod +x test_cli.sh

# Run the tests
./test_cli.sh

# Or run with bash explicitly
bash test_cli.sh
```

## Test Coverage

The test script covers the following areas:

### 1. Help and Basic Commands
- Display main help
- Verify CLI is operational

### 2. Database Initialization
- Initialize test database
- Verify database file creation
- Check schema version

### 3. Configuration Display
- Show current configuration
- Display API key status

### 4. Add Transactions
Tests adding various transaction types:
- Expense with tax (Office Supplies)
- Income (Consulting Revenue)
- Expense (Travel)
- Expense (Meals and Entertainment)
- Income (Product Sales)

### 5. List Transactions
- List all transactions (default limit)
- List with custom limit (3 records)
- List with custom limit (10 records)

### 6. Statistics and Reports
- Basic database statistics
- Statistics with category breakdown
- Income/expense summary
- Net calculation

### 7. Input Validation
Tests error handling for:
- Invalid date format (should fail)
- Negative amounts (should fail)

### 8. Database State Verification
- Verifies correct number of transactions
- Checks data persistence

### 9. Subcommand Help
Tests help for all subcommands:
- init
- list
- add
- process
- monitor
- stats
- config

### 10. Database Persistence
- Verifies data persists across CLI invocations
- Tests database reopening

## Test Results

The script provides:
- Color-coded output (green for pass, red for fail, yellow for info)
- Individual test status
- Final summary with pass/fail counts
- Exit code 0 for success, 1 for failure

## Expected Output

When all tests pass, you should see:
```
Tests Passed: 25
Tests Failed: 0
Total Tests:  25

All tests passed!
```

## Test Database

- The script uses a separate test database: `./data/test_bookkeeper.db`
- The test database is cleaned up after each run
- No impact on your production database

## Troubleshooting

### Line Ending Issues (Windows/WSL)

If you see errors like `$'\r': command not found`, fix line endings:

```bash
dos2unix test_cli.sh
# or
sed -i 's/\r$//' test_cli.sh
```

### Permission Issues

Make sure the script is executable:

```bash
chmod +x test_cli.sh
```

### Missing Dependencies

Ensure all dependencies are installed:

```bash
uv pip install -r requirements.txt -r requirements-dev.txt
```

## Integration with CI/CD

This test script can be integrated into continuous integration pipelines:

```yaml
# Example GitHub Actions step
- name: Run CLI Tests
  run: bash test_cli.sh
```

## Manual CLI Testing

You can also test individual commands manually:

```bash
# Initialize database
uv run python cli.py init

# Add a transaction
uv run python cli.py add --date 2025-10-24 --type expense \
  --category "Office Supplies" --amount 49.99 --vendor "Staples"

# List transactions
uv run python cli.py list

# Show statistics
uv run python cli.py stats --categories

# Show configuration
uv run python cli.py config
```

## Contributing

When adding new CLI commands:
1. Add corresponding tests to `test_cli.sh`
2. Update this documentation
3. Ensure all tests pass before committing
