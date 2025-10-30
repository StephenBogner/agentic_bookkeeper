# User Acceptance Test Scenarios

**Document Version:** 1.0
**Created:** 2025-10-29
**Author:** Agentic Bookkeeper Team
**Status:** Ready for Testing

---

## Purpose

This document defines comprehensive User Acceptance Test (UAT) scenarios for the
Agentic Bookkeeper application. These scenarios validate that the system meets
user requirements and operates correctly in real-world conditions.

---

## Test Environment Specifications

### System Requirements

- **Operating System:** Windows 10/11 or Linux (Ubuntu 20.04+)
- **Python Version:** 3.8+
- **Display Resolution:** 1920x1080 minimum
- **Memory:** 4GB RAM minimum
- **Disk Space:** 500MB free space

### Required Resources

- **LLM API Keys:** At least one provider (OpenAI, Anthropic, XAI, or Google)
- **Test Documents:** Sample receipts and invoices (PDF/image formats)
- **Test Data:** Sample transactions for reporting

### Pre-Test Setup

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Verify dependencies are installed
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify application starts
python -m agentic_bookkeeper --version
```

---

## UAT Scenarios

### Category 1: First-Time Setup

---

#### Scenario 1: Fresh Installation and Initial Configuration

**Objective:** Validate that a new user can successfully install and configure
the application for first use.

**Preconditions:**

- Python 3.8+ is installed
- No previous installation of Agentic Bookkeeper exists
- User has at least one LLM provider API key

**Test Steps:**

1. Clone or download the project repository
2. Create a virtual environment: `python -m venv venv`
3. Activate virtual environment
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env`
6. Edit `.env` file and add API key for at least one LLM provider
7. Run application: `python -m agentic_bookkeeper`
8. Observe first-run initialization

**Expected Results:**

- Virtual environment creates successfully
- All dependencies install without errors
- `.env` file is properly configured
- Application launches and shows main window
- First-run dialog appears with welcome message
- Default directories are created (data/, logs/, config/)
- Default database is initialized
- Settings dialog shows configured API key

**Success Criteria:**

- [x] Application starts without errors
- [x] Database file created at correct location
- [x] Configuration files are properly initialized
- [x] Main window displays with all tabs accessible
- [x] First-run experience is user-friendly

---

#### Scenario 2: Environment Setup Validation

**Objective:** Verify that all environment components are properly configured
and operational.

**Preconditions:**

- Scenario 1 completed successfully
- At least one LLM provider API key configured

**Test Steps:**

1. Open application
2. Navigate to Settings dialog
3. Verify API key configuration section
4. Click "Test Connection" for configured provider
5. Verify watch directory configuration
6. Verify database file location
7. Check tax jurisdiction setting (default: CRA)
8. Check currency setting (default: CAD)
9. Check default categories list

**Expected Results:**

- Settings dialog displays all configuration sections
- API key is masked but shows last 4 characters
- "Test Connection" succeeds with success message
- Watch directory path is valid and accessible
- Database file exists at specified location
- Tax jurisdiction shows "CRA (Canada)" as default
- Currency shows "CAD" as default
- Default categories are populated (8-10 categories)

**Success Criteria:**

- [x] All settings are accessible and editable
- [x] LLM provider connection test succeeds
- [x] Directories and files exist at specified paths
- [x] Defaults are appropriate for target users
- [x] Settings persist across application restarts

---

### Category 2: Daily Operations

---

#### Scenario 3: Document Upload and Automatic Processing

**Objective:** Validate that users can upload documents and have them
automatically processed into transactions.

**Preconditions:**

- Application is running
- At least one LLM provider is configured
- Test receipt/invoice documents are available

**Test Steps:**

1. Navigate to Dashboard tab
2. Verify monitoring status shows "Stopped"
3. Place a test receipt (PDF or image) in the watch directory
4. Click "Start Monitoring" button
5. Wait for document to be processed
6. Check logs for processing activity
7. Navigate to Transactions tab
8. Verify new transaction appears in the list
9. Click on transaction to view details
10. Verify extracted data is accurate

**Expected Results:**

- Monitoring starts successfully
- Document is detected within 5 seconds
- Processing completes within 15 seconds (depending on LLM provider)
- Transaction appears in Transactions table
- Extracted data includes: date, vendor, amount, category, description
- Accuracy is >80% for clear, well-formatted documents
- Document path is stored and accessible

**Success Criteria:**

- [x] Document processing is fully automated
- [x] Processing time is acceptable (<30 seconds)
- [x] Extracted data is reasonably accurate
- [x] User receives feedback on processing status
- [x] Errors are handled gracefully with clear messages

---

#### Scenario 4: Manual Transaction Entry and Editing

**Objective:** Verify that users can manually add and edit transactions.

**Preconditions:**

- Application is running
- Database has at least one existing transaction

**Test Steps:**

1. Navigate to Transactions tab
2. Click "Add Transaction" button
3. Fill in transaction form:
   - Transaction Type: Income
   - Date: Today's date
   - Vendor: "Test Consulting Inc."
   - Amount: 1500.00
   - Category: Professional Services
   - Description: "Consulting services for October"
4. Click "Save"
5. Verify transaction appears in table
6. Select the newly created transaction
7. Click "Edit" button
8. Change amount to 1750.00
9. Add note: "Adjusted per invoice correction"
10. Click "Save"
11. Verify changes are reflected

**Expected Results:**

- Add dialog opens with blank form
- All fields are editable and validated
- Date picker works correctly
- Amount accepts decimal values
- Category dropdown shows all available categories
- Save creates transaction successfully
- Transaction appears in table immediately
- Edit dialog pre-fills with existing data
- Changes save successfully
- Updated data displays correctly in table

**Success Criteria:**

- [x] Form validation prevents invalid data
- [x] All transaction fields are editable
- [x] Changes persist across sessions
- [x] User interface is intuitive and responsive
- [x] No data loss or corruption occurs

---

#### Scenario 5: Transaction Filtering and Searching

**Objective:** Test the transaction filtering and search functionality.

**Preconditions:**

- Database contains at least 20 transactions
- Transactions span multiple months
- Transactions include both income and expenses
- Multiple categories are represented

**Test Steps:**

1. Navigate to Transactions tab
2. Verify all transactions are displayed
3. Select "Income" from Transaction Type filter
4. Verify only income transactions are shown
5. Clear filter and select "Expense"
6. Verify only expense transactions are shown
7. Clear filter and select a specific category (e.g., "Office Supplies")
8. Verify only transactions in that category are shown
9. Clear category filter
10. Select date range: Last Month
11. Verify only transactions from last month are shown
12. Clear all filters
13. Enter search term in search box: "Amazon"
14. Verify only transactions with "Amazon" in vendor or description are shown
15. Test case-insensitive search with "AMAZON"

**Expected Results:**

- Type filter shows correct transactions
- Category filter shows correct transactions
- Date range filter shows correct transactions
- Search is case-insensitive
- Multiple filters can be combined
- Filter results update immediately
- Clear filter buttons work correctly
- Transaction count updates with filters

**Success Criteria:**

- [x] Filters work accurately for all criteria
- [x] Filter combinations work correctly
- [x] Search is fast (<1 second for 1000+ transactions)
- [x] UI clearly indicates active filters
- [x] Clearing filters restores all transactions

---

#### Scenario 6: Document Review and Approval Workflow

**Objective:** Validate the document review process for automatically processed
transactions.

**Preconditions:**

- Application has processed at least one document
- Transaction exists with associated document

**Test Steps:**

1. Navigate to Transactions tab
2. Identify transaction with document (shows document icon)
3. Right-click transaction and select "Review Document"
4. Verify Document Review dialog opens
5. Verify document image/PDF is displayed
6. Verify extracted data is shown alongside document
7. Review accuracy of extraction
8. If correct: Click "Approve"
9. If incorrect: Edit fields and click "Save Changes"
10. Verify dialog closes
11. Verify transaction status updates

**Expected Results:**

- Review dialog shows document clearly
- Zoom controls work for examining details
- Extracted data fields are editable
- Side-by-side view allows easy comparison
- Approve button marks transaction as reviewed
- Edit and save updates transaction data
- Dialog provides clear action buttons
- Changes persist in database

**Success Criteria:**

- [x] Document displays clearly and is readable
- [x] All extracted fields are accessible
- [x] Editing workflow is intuitive
- [x] Approval status is tracked
- [x] User can easily correct extraction errors

---

#### Scenario 7: Settings Modification

**Objective:** Test the ability to modify application settings and have changes
take effect.

**Preconditions:**

- Application is running
- Default settings are in place

**Test Steps:**

1. Open Settings dialog
2. Navigate to "Tax Jurisdiction" section
3. Change from "CRA (Canada)" to "IRS (United States)"
4. Click "Save"
5. Close and reopen Settings dialog
6. Verify jurisdiction is now IRS
7. Navigate to "Currency" section
8. Change from "CAD" to "USD"
9. Click "Save"
10. Navigate to Transactions tab
11. Verify currency symbols show as $ (USD)
12. Navigate to "Categories" section
13. Add new category: "Marketing"
14. Click "Save"
15. Go to Add Transaction dialog
16. Verify "Marketing" appears in category dropdown

**Expected Results:**

- Settings changes save successfully
- Changes persist after dialog close/reopen
- Tax jurisdiction change affects report templates
- Currency change affects display throughout application
- New categories are immediately available
- Application does not require restart for settings changes
- Settings file is updated on disk

**Success Criteria:**

- [x] All settings are modifiable
- [x] Changes take effect immediately
- [x] No data corruption from settings changes
- [x] Settings persist across application restarts
- [x] UI reflects new settings consistently

---

#### Scenario 8: Dashboard Monitoring and Status Checks

**Objective:** Verify dashboard provides accurate monitoring and status
information.

**Preconditions:**

- Application is running
- Database contains sample transactions

**Test Steps:**

1. Navigate to Dashboard tab
2. Verify summary statistics:
   - Total Income (This Month)
   - Total Expenses (This Month)
   - Net Income (This Month)
   - Transaction Count
3. Compare statistics with Transactions tab data
4. Start monitoring
5. Verify status indicator changes to "Running"
6. Stop monitoring
7. Verify status indicator changes to "Stopped"
8. Check last processed document timestamp
9. Review recent activity log

**Expected Results:**

- Dashboard displays accurate summary statistics
- Statistics match manual calculations from Transactions
- Statistics update in real-time when transactions added
- Monitoring status indicator is clear and accurate
- Status changes are reflected immediately
- Last processed timestamp shows correct date/time
- Activity log shows recent operations
- Dashboard is responsive and updates quickly

**Success Criteria:**

- [x] Summary statistics are accurate
- [x] Status indicators are clear and reliable
- [x] Dashboard updates reflect current state
- [x] Performance is acceptable (no lag)
- [x] Information is helpful for daily use

---

### Category 3: Report Generation

---

#### Scenario 9: Income Statement Generation for Monthly Period

**Objective:** Validate generation of accurate income statements for a specified
month.

**Preconditions:**

- Database contains transactions for at least one complete month
- Transactions include both income and expenses
- Multiple categories are represented

**Test Steps:**

1. Navigate to Reports tab
2. Select report type: "Income Statement"
3. Select date range preset: "Last Month"
4. Click "Generate Preview"
5. Review preview showing:
   - Report header with date range
   - Income section with categories and totals
   - Expense section with categories and totals
   - Net Income calculation
6. Verify calculations are correct
7. Select export format: "PDF"
8. Click "Export Report"
9. Choose save location
10. Open exported PDF
11. Verify formatting and content

**Expected Results:**

- Preview generates within 2 seconds
- Income section shows all income categories with amounts
- Expense section shows all expense categories with amounts
- Category breakdowns show percentages
- Net Income = Total Income - Total Expenses
- PDF exports successfully
- PDF is professionally formatted
- PDF includes metadata (date range, generation date, jurisdiction)
- Currency symbols are correct

**Success Criteria:**

- [x] Report calculations are 100% accurate
- [x] Preview is clear and readable
- [x] Export completes without errors
- [x] PDF is suitable for tax filing
- [x] Generation is fast (<5 seconds for 1000 transactions)

---

#### Scenario 10: Expense Report Generation with Tax Codes

**Objective:** Validate expense report generation with jurisdiction-specific tax
codes.

**Preconditions:**

- Tax jurisdiction is set (CRA or IRS)
- Database contains expense transactions
- Multiple expense categories exist

**Test Steps:**

1. Navigate to Reports tab
2. Select report type: "Expense Report"
3. Select date range: "This Year"
4. Click "Generate Preview"
5. Review preview showing:
   - Report header with date range and jurisdiction
   - Expense categories with amounts and percentages
   - Tax codes for each category (CRA T2125 or IRS Schedule C)
   - Total expenses
6. Verify tax codes are appropriate for jurisdiction
7. Select export format: "CSV"
8. Click "Export Report"
9. Open exported CSV in Excel
10. Verify structure and formatting

**Expected Results:**

- Expense categories are grouped correctly
- Tax codes match jurisdiction (CRA: T2125, IRS: Schedule C)
- Percentages sum to 100%
- CSV is Excel-compatible (UTF-8 BOM encoding)
- CSV includes metadata section
- Currency formatting is correct
- Tax codes are in dedicated column
- Data is ready for tax software import

**Success Criteria:**

- [x] Tax codes are accurate for jurisdiction
- [x] Report structure matches tax forms
- [x] CSV format is suitable for tax preparation
- [x] No formula injection vulnerabilities
- [x] Special characters are handled correctly

---

#### Scenario 11: Multi-Format Export (PDF, CSV, JSON)

**Objective:** Test the ability to export the same report in all three supported
formats.

**Preconditions:**

- Database contains sufficient transaction data
- User has generated a report preview

**Test Steps:**

1. Navigate to Reports tab
2. Select report type: "Income Statement"
3. Select date range: "Last Quarter"
4. Click "Generate Preview"
5. Export as PDF:
   - Select format: PDF
   - Click "Export Report"
   - Save to test directory
6. Verify PDF exports successfully
7. Export as CSV:
   - Select format: CSV
   - Click "Export Report"
   - Save to test directory
8. Verify CSV exports successfully
9. Export as JSON:
   - Select format: JSON
   - Click "Export Report"
   - Save to test directory
10. Verify JSON exports successfully
11. Compare data across all three formats

**Expected Results:**

- All three exports complete successfully
- PDF is professionally formatted and readable
- CSV opens correctly in Excel
- JSON is valid and well-formed
- All three formats contain the same data
- Metadata is included in all formats
- File sizes are reasonable
- Export process is fast (<3 seconds each)

**Success Criteria:**

- [x] All formats export without errors
- [x] Data consistency across formats
- [x] Each format is suitable for its use case
- [x] No data loss or corruption
- [x] User can choose format based on needs

---

#### Scenario 12: Custom Date Range Reporting

**Objective:** Verify the ability to generate reports for custom date ranges.

**Preconditions:**

- Database contains transactions spanning at least 6 months
- Transactions are distributed across multiple months

**Test Steps:**

1. Navigate to Reports tab
2. Select report type: "Income Statement"
3. Select date range preset: "Custom"
4. Date picker controls appear
5. Set start date: January 1, 2025
6. Set end date: March 31, 2025 (Q1)
7. Click "Generate Preview"
8. Verify preview shows only Q1 transactions
9. Check total amounts against filtered Transactions tab
10. Change end date to February 28, 2025
11. Regenerate preview
12. Verify only Jan-Feb transactions are included
13. Test edge case: Same start and end date
14. Verify single-day report generates correctly

**Expected Results:**

- Custom date picker is intuitive and easy to use
- Date range can be set to any valid period
- Preview updates immediately after date change
- Only transactions within date range are included
- Edge cases are handled correctly:
  - Single day reports
  - Year boundaries
  - Leap years
- Date validation prevents invalid ranges (end before start)
- Custom range is used for export

**Success Criteria:**

- [x] Custom date selection works correctly
- [x] Date filtering is accurate to the day
- [x] Edge cases are handled gracefully
- [x] UI prevents invalid date ranges
- [x] Custom ranges work for all report types

---

### Category 4: Error Handling

---

#### Scenario 13: Invalid Document Upload Handling

**Objective:** Verify graceful handling of invalid or corrupted documents.

**Preconditions:**

- Application is running with monitoring enabled
- Watch directory is accessible

**Test Steps:**

1. Place a text file (.txt) in watch directory
2. Observe application behavior
3. Place a corrupted PDF file in watch directory
4. Observe application behavior
5. Place an empty file in watch directory
6. Observe application behavior
7. Place an image file with no text/numbers in watch directory
8. Observe application behavior
9. Check error logs for appropriate error messages
10. Verify application remains stable

**Expected Results:**

- Unsupported file types are ignored with warning
- Corrupted PDFs are logged as errors
- Empty files are handled gracefully
- Images with no extractable data generate warnings
- Error messages are clear and helpful
- Errors are logged with timestamps
- Application does not crash
- User is notified of processing failures
- Failed documents can be reviewed manually

**Success Criteria:**

- [x] Application handles errors gracefully
- [x] No crashes or data corruption
- [x] Error messages are clear and actionable
- [x] Failed documents are logged appropriately
- [x] User can recover from errors easily

---

#### Scenario 14: Missing API Key Recovery

**Objective:** Test application behavior when LLM provider API key is missing or
invalid.

**Preconditions:**

- Application is installed but not configured
- No API keys are set in .env file

**Test Steps:**

1. Start application with no API keys configured
2. Observe startup behavior
3. Attempt to process a document
4. Observe error handling
5. Open Settings dialog
6. Navigate to API Keys section
7. See warning message about missing keys
8. Add a valid API key for one provider
9. Click "Save"
10. Click "Test Connection"
11. Verify connection succeeds
12. Attempt to process a document
13. Verify processing now works

**Expected Results:**

- Application starts even without API keys
- Clear warning message on dashboard
- Document processing fails with clear error
- Error message directs user to Settings
- Settings dialog highlights missing API keys
- Adding API key is straightforward
- Test connection validates key immediately
- Processing works after key is added
- No restart required

**Success Criteria:**

- [x] Missing API key does not prevent application startup
- [x] Error messages guide user to resolution
- [x] API key configuration is user-friendly
- [x] Validation prevents invalid keys
- [x] Recovery is seamless and quick

---

#### Scenario 15: Database Integrity and Error Recovery

**Objective:** Verify application handles database issues gracefully.

**Preconditions:**

- Application is running normally
- Database file exists and is accessible

**Test Steps:**

1. Close application
2. Make database file read-only (chmod 444 or properties)
3. Start application
4. Attempt to add a transaction
5. Observe error handling
6. Close application
7. Restore database write permissions
8. Start application
9. Verify normal operations resume
10. Make a backup of database
11. Delete database file
12. Start application
13. Observe database recreation
14. Verify new database is initialized correctly

**Expected Results:**

- Read-only database is detected at startup
- Error message warns user about read-only status
- Application allows read operations but prevents writes
- Write attempts show clear error messages
- After fixing permissions, application recovers
- Missing database is recreated automatically
- New database has correct schema
- Application provides option to restore from backup
- No data corruption occurs

**Success Criteria:**

- [x] Database issues are detected early
- [x] Error messages are clear and actionable
- [x] Application remains stable despite database issues
- [x] Recovery is possible without data loss
- [x] User is guided through resolution steps

---

## Success Metrics

### Overall Success Criteria

For UAT to be considered successful, the following metrics must be achieved:

- **Scenario Pass Rate:** ≥90% (14 of 15 scenarios must pass)
- **Critical Path Success:** 100% (Scenarios 1, 3, 4, 9 must pass)
- **No P0/P1 Blockers:** Zero priority 0 or 1 issues
- **Performance Targets Met:** All performance criteria achieved
- **User Satisfaction:** Positive feedback on usability and functionality

### Priority Definitions

- **P0 (Critical):** Application crashes, data loss, security vulnerabilities
- **P1 (High):** Core functionality broken, major usability issues
- **P2 (Medium):** Minor feature issues, cosmetic problems
- **P3 (Low):** Enhancement requests, nice-to-have features

---

## Test Execution Guidelines

### Preparation

1. Review all scenarios before starting
2. Prepare test environment according to specifications
3. Gather all required test data and documents
4. Set up clean database for consistent results
5. Document environment details (OS version, Python version, etc.)

### During Testing

1. Follow scenario steps exactly as written
2. Document actual results for each step
3. Take screenshots of errors or unexpected behavior
4. Note performance observations (slow operations, delays)
5. Record timestamps for timed operations
6. Log all issues discovered with priority classification

### After Testing

1. Complete UAT_RESULTS.md with findings
2. Compile list of all issues discovered
3. Calculate success metrics
4. Provide recommendations for fixes
5. Identify any scenarios that need revision

---

## Notes

### Testing Tips

- Test in a realistic environment (not just developer machine)
- Use real documents when possible (anonymize sensitive data)
- Test with different LLM providers if multiple are available
- Vary test data to cover edge cases
- Test both happy paths and error conditions

### Known Limitations

- Document processing accuracy depends on LLM provider quality
- Processing time varies based on document complexity and provider
- Some features require specific API keys (provider-dependent)

### Future Enhancements

Scenarios may need updates for:

- Multi-user support
- Cloud storage integration
- Mobile app testing
- Localization testing (multiple languages)

---

## Document End
