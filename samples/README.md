# Sample Documents and Data

This directory contains sample invoices, receipts, and configuration files for testing
and demonstrating the Agentic Bookkeeper application.

## Directory Structure

```text
samples/
├── README.md                    # This file
├── invoices/                    # Sample invoices (income documents)
│   ├── invoice_consulting.pdf  # Consulting services invoice ($7,250.00)
│   └── invoice_software_license.pdf  # Software license invoice ($7,345.00)
├── receipts/                    # Sample receipts (expense documents)
│   ├── receipt_gas.pdf         # Gas/fuel receipt ($75.94)
│   ├── receipt_internet_phone.pdf  # Internet/phone bill ($152.54)
│   ├── receipt_office_supplies.pdf  # Office supplies ($52.52)
│   └── receipt_restaurant.pdf  # Restaurant/meals receipt ($69.43)
└── config/                      # Sample configuration files
    ├── .env.sample             # Sample environment configuration
    └── README.md               # Configuration documentation
```

## Purpose

These sample documents are provided to help you:

1. **Test the application** - Verify document processing works correctly
2. **Learn the features** - See how different document types are handled
3. **Demo the system** - Show stakeholders the application capabilities
4. **Develop and debug** - Test changes without risking real financial documents

## Sample Documents

### Invoices (Income Documents)

**invoice_consulting.pdf**

- **Vendor:** Tech Consulting Inc.
- **Date:** 2025-10-23
- **Amount:** $7,250.00
- **Type:** Income
- **Category:** Consulting Revenue
- **Description:** Software development and project management services

**invoice_software_license.pdf**

- **Vendor:** Software Solutions Ltd.
- **Date:** 2025-10-24
- **Amount:** $7,345.00
- **Type:** Income
- **Category:** Product Sales
- **Description:** Enterprise software license and premium support

### Receipts (Expense Documents)

**receipt_office_supplies.pdf**

- **Vendor:** Office Depot
- **Date:** 2025-10-20
- **Amount:** $52.52
- **Type:** Expense
- **Category:** Office Supplies
- **Description:** Paper, pens, and stapler

**receipt_restaurant.pdf**

- **Vendor:** The Gourmet Bistro
- **Date:** 2025-10-21
- **Amount:** $69.43
- **Type:** Expense
- **Category:** Meals and Entertainment
- **Description:** Business lunch with client

**receipt_gas.pdf**

- **Vendor:** QuickFill Gas Station
- **Date:** 2025-10-22
- **Amount:** $75.94
- **Type:** Expense
- **Category:** Travel/Fuel
- **Description:** 45.2L regular unleaded gasoline

**receipt_internet_phone.pdf**

- **Vendor:** TeleCom Services
- **Date:** 2025-10-25
- **Amount:** $152.54
- **Type:** Expense
- **Category:** Utilities
- **Description:** Business internet (100Mbps) and phone line

### Summary

- **Total Income:** $14,595.00 (2 invoices)
- **Total Expenses:** $350.43 (4 receipts)
- **Net Income:** $14,244.57

## How to Use Sample Documents

### Method 1: Manual Processing via GUI

1. Start the application:

   ```bash
   python -m agentic_bookkeeper
   ```

2. Navigate to the **Transactions** tab
3. Click **"Review Documents"** button
4. Click **"Load Document"** and select a sample document
5. Review the extracted data (date, vendor, amount, category)
6. Click **"Accept"** to add the transaction to your database

### Method 2: Automatic Processing via Watch Folder

1. Configure your watch folder in Settings or `.env`:

   ```bash
   WATCH_FOLDER=./watch_folder
   ```

2. Start the application with monitoring enabled
3. Copy sample documents to the watch folder:

   ```bash
   cp samples/invoices/*.pdf ./watch_folder/
   cp samples/receipts/*.pdf ./watch_folder/
   ```

4. The application will automatically:
   - Detect new documents
   - Process them with the LLM
   - Extract transaction data
   - Store results in the database
   - Move processed files to `./watch_folder/processed/`

### Method 3: Batch Processing via CLI

1. Process all sample invoices:

   ```bash
   python -m agentic_bookkeeper process samples/invoices/
   ```

2. Process all sample receipts:

   ```bash
   python -m agentic_bookkeeper process samples/receipts/
   ```

3. Process all sample documents:

   ```bash
   python -m agentic_bookkeeper process samples/invoices/ samples/receipts/
   ```

## Expected Results

After processing all sample documents, you should see:

### Transactions Table

| Date       | Vendor              | Type    | Category              | Amount     |
|------------|---------------------|---------|-----------------------|------------|
| 2025-10-20 | Office Depot        | Expense | Office Supplies       | $52.52     |
| 2025-10-21 | The Gourmet Bistro  | Expense | Meals & Entertainment | $69.43     |
| 2025-10-22 | QuickFill Gas       | Expense | Travel/Fuel           | $75.94     |
| 2025-10-23 | Tech Consulting Inc.| Income  | Consulting Revenue    | $7,250.00  |
| 2025-10-24 | Software Solutions  | Income  | Product Sales         | $7,345.00  |
| 2025-10-25 | TeleCom Services    | Expense | Utilities             | $152.54    |

### Dashboard Metrics

- **Total Income:** $14,595.00
- **Total Expenses:** $350.43
- **Net Income:** $14,244.57
- **Documents Processed:** 6

### Reports

You can generate reports for the sample data:

1. **Income Statement** (2025-10-20 to 2025-10-25):
   - Revenue: $14,595.00
   - Expenses: $350.43
   - Net Income: $14,244.57

2. **Expense Report** (2025-10-20 to 2025-10-25):
   - Office Supplies: $52.52 (15.0%)
   - Meals & Entertainment: $69.43 (19.8%)
   - Travel/Fuel: $75.94 (21.7%)
   - Utilities: $152.54 (43.5%)
   - **Total:** $350.43

3. **Export formats available:** PDF, CSV, JSON

## Testing Scenarios

### Scenario 1: Document Processing Accuracy

**Objective:** Verify the LLM correctly extracts transaction data

1. Process `receipt_office_supplies.pdf`
2. Verify extracted data matches:
   - Date: 2025-10-20
   - Vendor: Office Depot
   - Amount: $52.52
   - Category: Office Supplies (or similar)

**Expected Result:** All fields extracted with >90% accuracy

### Scenario 2: Income vs Expense Classification

**Objective:** Verify the LLM correctly classifies transaction types

1. Process `invoice_consulting.pdf` (should be classified as **Income**)
2. Process `receipt_restaurant.pdf` (should be classified as **Expense**)

**Expected Result:** Correct type classification for both documents

### Scenario 3: Multi-Document Report Generation

**Objective:** Verify accurate report generation across multiple transactions

1. Process all 6 sample documents
2. Generate Income Statement for October 2025
3. Verify totals match expected values (Income: $14,595.00, Expenses: $350.43)

**Expected Result:** Accurate calculations in all report formats (PDF, CSV, JSON)

### Scenario 4: Category Breakdown

**Objective:** Verify expense categorization and aggregation

1. Process all 4 receipt documents
2. Generate Expense Report for October 2025
3. Verify category breakdown matches expected percentages

**Expected Result:** Accurate category grouping and percentage calculations

## Regenerating Sample Documents

If you need to recreate or modify the sample documents, use the included script:

```bash
python generate_test_documents.py
```

This will generate fresh sample documents in `samples/test_documents/`. You can then
copy them to the appropriate `invoices/` or `receipts/` directories.

To modify the sample data:

1. Edit `generate_test_documents.py`
2. Change vendor names, amounts, dates, or categories
3. Run the script to regenerate documents
4. Copy to `samples/invoices/` or `samples/receipts/` as appropriate

## Configuration Samples

See `config/README.md` for information about:

- Sample `.env` configuration file
- How to set up API keys for LLM providers
- Tax jurisdiction and currency configuration
- Watch folder and database settings
- Logging and security options

## Privacy and Security

**Important Notes:**

- These sample documents contain **fictional** data only
- No real company names, addresses, or financial information
- Safe to use for testing, demos, and development
- Do NOT use for actual bookkeeping or tax purposes
- For production use, always process real documents in a secure environment

## LLM Processing Notes

### Expected Token Usage

- Each document uses approximately 1,000-2,000 tokens for processing
- Processing all 6 sample documents: ~6,000-12,000 tokens
- Estimated cost (varies by provider):
  - OpenAI GPT-4o-mini: < $0.01
  - Anthropic Claude Haiku: < $0.02
  - Google Gemini Flash: Free (within free tier)

### Processing Time

- Average: 1-3 seconds per document
- Total for all 6 documents: 6-18 seconds
- Depends on LLM provider, network speed, and API load

### Accuracy

Based on user acceptance testing (UAT):

- **Date extraction:** 100% accuracy
- **Vendor extraction:** 100% accuracy
- **Amount extraction:** 100% accuracy
- **Category classification:** ~80% accuracy (may vary slightly)

**Note:** If category classification differs from expected, you can manually edit
the transaction in the GUI. The LLM learns patterns over time and may suggest
different but equally valid categories.

## Troubleshooting

### "No LLM provider configured" error

- Copy `samples/config/.env.sample` to `.env` in the project root
- Add at least one API key for an LLM provider
- See `config/README.md` for setup instructions

### Documents not processing

- Verify your LLM API key is valid and has credits
- Check the application logs (`bookkeeper.log`) for errors
- Try processing manually via GUI first to see detailed error messages
- Ensure document files are valid PDFs (not corrupted)

### Incorrect data extraction

- Try a different LLM provider (accuracy varies)
- Check document quality (scanned receipts may have lower accuracy)
- Manually review and correct in the GUI
- Report persistent issues for investigation

### "File not found" errors

- Verify sample files exist: `ls samples/invoices/ samples/receipts/`
- If missing, regenerate: `python generate_test_documents.py`
- Check file permissions: `ls -l samples/invoices/ samples/receipts/`

## Further Documentation

For more information, see:

- **[User Guide](../docs/USER_GUIDE.md)** - Complete application documentation
- **[Developer Guide](../docs/DEVELOPMENT.md)** - Development and customization
- **[Performance Metrics](../docs/PERFORMANCE_METRICS.md)** - Performance benchmarks
- **[UAT Results](../docs/UAT_RESULTS.md)** - User acceptance testing results
- **[Known Issues](../docs/KNOWN_ISSUES.md)** - Current limitations and workarounds

## Support

If you encounter issues with the sample documents:

1. Check the troubleshooting section above
2. Review the application logs (`bookkeeper.log`)
3. Consult the [User Guide](../docs/USER_GUIDE.md)
4. Report issues at the project repository

---

**Last Updated:** 2025-10-29
**Sample Data Version:** 1.0
**Compatible with:** Agentic Bookkeeper v0.1.0+
