#!/bin/bash
#
# CLI Test Script for Agentic Bookkeeper
# Tests all CLI commands with various scenarios
#
# Author: Stephen Bogner, P.Eng.
# Date: 2025-10-24
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test database path
TEST_DB="./data/test_bookkeeper.db"

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_test() {
    echo -e "${YELLOW}TEST:${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((TESTS_PASSED++))
}

print_error() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((TESTS_FAILED++))
}

run_command() {
    local description="$1"
    shift
    print_test "$description"

    if uv run python cli.py --db-path "$TEST_DB" "$@"; then
        print_success "$description"
        return 0
    else
        print_error "$description"
        return 1
    fi
}

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Cleaning up test database...${NC}"
    rm -f "$TEST_DB"
    rm -f "${TEST_DB}-shm"
    rm -f "${TEST_DB}-wal"
}

# Main test execution
main() {
    print_header "Agentic Bookkeeper CLI Test Suite"

    # Cleanup before starting
    cleanup

    # Ensure data directory exists
    mkdir -p ./data

    # Test 1: Help Command
    print_header "Test 1: Help and Basic Commands"
    run_command "Display help" --help || true

    # Test 2: Initialize Database
    print_header "Test 2: Database Initialization"
    run_command "Initialize database" init

    # Verify database file exists
    if [ -f "$TEST_DB" ]; then
        print_success "Database file created"
    else
        print_error "Database file not created"
    fi

    # Test 3: Configuration Display
    print_header "Test 3: Configuration Display"
    run_command "Show configuration" config

    # Test 4: Add Transactions - Various Scenarios
    print_header "Test 4: Add Transactions"

    run_command "Add expense transaction (Office Supplies)" \
        add --date 2025-10-24 --type expense --category "Office Supplies" \
        --amount 49.99 --vendor "Staples" --description "Paper and pens" \
        --tax-amount 6.50

    run_command "Add income transaction (Consulting)" \
        add --date 2025-10-23 --type income --category "Consulting Revenue" \
        --amount 1500.00 --vendor "ACME Corp" \
        --description "Software consulting services"

    run_command "Add expense transaction (Travel)" \
        add --date 2025-10-22 --type expense --category "Travel" \
        --amount 125.50 --vendor "Uber" --description "Client meeting transportation"

    run_command "Add expense transaction (Meals)" \
        add --date 2025-10-21 --type expense --category "Meals and Entertainment" \
        --amount 85.75 --vendor "Restaurant XYZ" \
        --description "Business lunch" --tax-amount 11.15

    run_command "Add income transaction (Product Sales)" \
        add --date 2025-10-20 --type income --category "Product Sales" \
        --amount 2500.00 --vendor "Client ABC" --description "Software license"

    # Test 5: List Transactions
    print_header "Test 5: List Transactions"

    run_command "List all transactions (default limit 20)" list

    run_command "List transactions with limit 3" list --limit 3

    run_command "List transactions with limit 10" list --limit 10

    # Test 6: Statistics Commands
    print_header "Test 6: Statistics and Reports"

    run_command "Show basic statistics" stats

    run_command "Show statistics with category breakdown" stats --categories

    # Test 7: Edge Cases and Validation
    print_header "Test 7: Input Validation"

    # Test invalid date format (should fail)
    print_test "Add transaction with invalid date (should fail)"
    if ! uv run python cli.py --db-path "$TEST_DB" add \
        --date "2025/10/24" --type expense --category "Test" \
        --amount 10.00 --vendor "Test" 2>/dev/null; then
        print_success "Invalid date correctly rejected"
    else
        print_error "Invalid date should have been rejected"
    fi

    # Test negative amount (should fail)
    print_test "Add transaction with negative amount (should fail)"
    if ! uv run python cli.py --db-path "$TEST_DB" add \
        --date "2025-10-24" --type expense --category "Test" \
        --amount -10.00 --vendor "Test" 2>/dev/null; then
        print_success "Negative amount correctly rejected"
    else
        print_error "Negative amount should have been rejected"
    fi

    # Test 8: Verify Final Database State
    print_header "Test 8: Verify Database State"

    # Count transactions (should be 5 successful adds)
    TRANSACTION_COUNT=$(uv run python -c "
import sys
sys.path.insert(0, 'src')
from agentic_bookkeeper.models.database import Database
db = Database('$TEST_DB')
db.initialize_schema()
stats = db.get_database_stats()
print(stats['transaction_count'])
db.close()
" 2>/dev/null)

    if [ "$TRANSACTION_COUNT" = "5" ]; then
        print_success "Correct number of transactions (5)"
    else
        print_error "Expected 5 transactions, found $TRANSACTION_COUNT"
    fi

    # Test 9: Command Line Help for Subcommands
    print_header "Test 9: Subcommand Help"

    for cmd in init list add process monitor stats config; do
        print_test "Display help for '$cmd' command"
        if uv run python cli.py "$cmd" --help >/dev/null 2>&1; then
            print_success "Help for '$cmd' command"
        else
            print_error "Help for '$cmd' command failed"
        fi
    done

    # Test 10: Database Operations After Restart
    print_header "Test 10: Database Persistence"

    run_command "List transactions after restart" list --limit 5

    # Final Summary
    print_header "Test Summary"
    echo -e "Tests Passed: ${GREEN}${TESTS_PASSED}${NC}"
    echo -e "Tests Failed: ${RED}${TESTS_FAILED}${NC}"
    echo -e "Total Tests:  $((TESTS_PASSED + TESTS_FAILED))"

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "\n${GREEN}All tests passed!${NC}"
        cleanup
        exit 0
    else
        echo -e "\n${RED}Some tests failed!${NC}"
        cleanup
        exit 1
    fi
}

# Run main function
main
