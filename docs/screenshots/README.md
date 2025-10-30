# Screenshots for User Guide

This directory is intended for screenshots to be used in the User Guide.

## Required Screenshots

The following screenshots should be captured and placed in this directory:

### 1. Main Application Window

**Filename:** `01_main_window.png`

**Description:** Full application window showing the tabbed interface

**Capture:** Main window with all tabs visible (Dashboard, Transactions, Reports, Settings)

---

### 2. Dashboard Tab

**Filename:** `02_dashboard.png`

**Description:** Dashboard view with monitoring controls and statistics

**Capture:** Dashboard showing:

- Start/Stop Monitoring button
- Current statistics (documents processed, transactions, etc.)
- Status indicators

---

### 3. Settings Dialog

**Filename:** `03_settings.png`

**Description:** Settings dialog with API keys and configuration

**Capture:** Settings tab showing (with API keys redacted/blurred):

- LLM provider selection
- API key fields
- Directory configuration
- Tax jurisdiction and currency settings
- Save/Cancel buttons

---

### 4. Transactions View

**Filename:** `04_transactions_list.png`

**Description:** Transactions table with sample data

**Capture:** Transactions tab showing:

- Transaction table with multiple entries
- Color-coded rows (green for income, red for expenses)
- Filter controls at top
- Action buttons (Add, Edit, Delete)

---

### 5. Add Transaction Dialog

**Filename:** `05_add_transaction.png`

**Description:** Dialog for adding a new transaction manually

**Capture:** Add Transaction dialog showing:

- All input fields (Date, Type, Vendor, Amount, Category, Description)
- Dropdown menus
- Save/Cancel buttons

---

### 6. Edit Transaction Dialog

**Filename:** `06_edit_transaction.png`

**Description:** Dialog for editing an existing transaction

**Capture:** Edit Transaction dialog with populated fields:

- All fields filled with sample data
- Same layout as Add Transaction dialog
- Save/Cancel buttons

---

### 7. Document Review Dialog

**Filename:** `07_document_review.png`

**Description:** Dialog showing original document and extracted data

**Capture:** Document Review dialog showing:

- Document image preview on left
- Extracted transaction details on right
- Close button

---

### 8. Reports Tab - Income Statement

**Filename:** `08_report_income_statement.png`

**Description:** Reports tab with income statement preview

**Capture:** Reports tab showing:

- Report type selector (Income Statement selected)
- Date range selector
- Export format selector
- Preview/Export buttons
- Preview text area showing formatted income statement

---

### 9. Reports Tab - Expense Report

**Filename:** `09_report_expense.png`

**Description:** Reports tab with expense report preview

**Capture:** Reports tab showing:

- Report type selector (Expense Report selected)
- Date range selector
- Export format selector
- Preview text area showing formatted expense report with tax codes

---

### 10. Export Dialog

**Filename:** `10_export_dialog.png`

**Description:** File save dialog for exporting reports

**Capture:** Native file save dialog showing:

- Format selected (PDF, CSV, or JSON)
- File name field
- Save location

---

### 11. Sample PDF Report

**Filename:** `11_sample_pdf_report.png`

**Description:** Generated PDF report (screenshot of opened PDF)

**Capture:** PDF viewer showing a generated income statement or expense report with:

- Professional formatting
- Header and footer
- Page numbers
- Table with data

---

### 12. Processing Indicator

**Filename:** `12_processing.png`

**Description:** Application during document processing

**Capture:** Dashboard or Transactions tab showing:

- Progress indicator
- "Processing..." message
- Status updates

---

## Screenshot Guidelines

### Technical Requirements

- **Resolution:** Minimum 1920x1080 display
- **Format:** PNG (lossless)
- **File Size:** Optimize to <500KB per image
- **Color Depth:** 24-bit RGB

### Capture Guidelines

1. **Clean Environment**:
   - Close unnecessary applications
   - Use sample data (no real financial information)
   - Use consistent sample data across screenshots

2. **Window Positioning**:
   - Center the application window
   - Ensure full window is visible
   - No window overlaps

3. **Redaction**:
   - Blur or redact any API keys
   - Use fake/sample data only
   - Redact any personal information

4. **Annotations** (optional):
   - Use red arrows or circles to highlight key features
   - Add text annotations to explain functionality
   - Keep annotations professional and minimal

### Sample Data

Use these consistent sample values across screenshots:

**Sample Transactions:**

1. 2025-10-15, Expense, Office Depot, $45.99, Office Expense, "Printer paper and pens"
2. 2025-10-18, Expense, Shell Gas Station, $52.30, Car and Truck Expenses, "Fuel for business trip"
3. 2025-10-20, Income, ABC Corporation, $1,500.00, Services, "Consulting services - October"
4. 2025-10-22, Expense, AT&T, $89.99, Utilities, "Business internet - October"
5. 2025-10-25, Expense, Amazon, $124.50, Supplies, "Office supplies and materials"

**Sample Configuration:**

- **LLM Provider:** XAI
- **Tax Jurisdiction:** IRS
- **Currency:** USD
- **Watch Directory:** `~/Documents/BookkeeperWatch`

### Tools for Screenshots

**Windows:**

- Snipping Tool (Windows 10+)
- Snip & Sketch (Windows 10+)
- ShareX (third-party, free)

**Linux:**

- GNOME Screenshot (`gnome-screenshot`)
- Flameshot (`flameshot gui`)
- Spectacle (KDE)

### Processing Screenshots

After capturing, optimize images:

```bash
# Using optipng (lossless compression)
optipng -o7 screenshot.png

# Using ImageMagick (resize if needed)
convert screenshot.png -resize 1920x1080 screenshot_resized.png
```

---

## Integration with User Guide

Once screenshots are captured, update `USER_GUIDE.md` to include them:

```markdown
![Main Window](screenshots/01_main_window.png)
*Figure 1: Main application window with tabbed interface*
```

Place screenshot references at relevant sections in the User Guide.

---

## Status

**Current Status:** Screenshots pending (requires GUI to be running)

**Next Steps:**

1. Launch the application with sample data
2. Capture all 12 required screenshots
3. Optimize and save to this directory
4. Update USER_GUIDE.md with screenshot references
5. Review and validate all images

---

**Last Updated:** 2025-10-29
