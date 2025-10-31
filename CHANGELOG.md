# Changelog

All notable changes to Agentic Bookkeeper will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-10-30

### Added

- **Cash-Basis Tax Reporting**: All financial reports now display tax information separately
  - Income Statement shows pre-tax amounts, tax collected/paid, and cash totals
  - Expense Report includes tax breakdown by category
  - Tax amounts tracked separately from pre-tax business amounts

- **Tax Summary Report**: New report type specifically for GST/HST filing
  - Lists all transactions with tax collected (output tax)
  - Lists all transactions with tax paid (input tax credits)
  - Calculates net tax position (payable or refundable)
  - Includes professional disclaimer for tax filing purposes

- **Export Functionality**: All three export formats updated with full tax support
  - **PDF Export**: Professional PDFs with tax columns and color-coded net position
  - **CSV Export**: Excel-compatible CSVs with complete tax breakdown
  - **JSON Export**: Structured JSON with all tax information preserved

- **GUI Enhancements**: Reports tab now includes tax information
  - "Tax Summary" added to report type dropdown
  - Preview display shows cash-basis amounts with tax breakdown
  - Tax position prominently displayed in preview

### Changed

- Report data structure updated to nested format (revenue, expenses, net_income)
- Reports now show cash-basis accounting (pre-tax + tax = cash total)
- Percentages still calculated on pre-tax amounts for accuracy
- Net income now shows three views: pre-tax, cash, and tax position

### Technical

- Modified `report_generator.py` (~180 lines): Added tax tracking and tax summary generation
- Modified `reports_widget.py` (~120 lines): Updated GUI for tax reports
- Modified `pdf_exporter.py` (~180 lines): Added tax columns and tax summary PDF
- Modified `csv_exporter.py` (~150 lines): Added tax columns and tax summary CSV
- Modified `json_exporter.py` (~60 lines): Updated for new report structure
- Total: ~690 lines of changes across 5 files
- Implementation time: ~5 hours
- Maintains backward compatibility with legacy fields

### Documentation

- Added comprehensive tax reporting documentation
- Updated user guide with tax reporting instructions
- Added examples for GST/HST filing workflow
- Documented known limitations and future enhancements

## [0.1.0] - 2025-10-29

### Added

- Initial release of Agentic Bookkeeper
- Document processing with OCR and LLM extraction
- Transaction management with SQLite database
- Financial reporting (Income Statement, Expense Report)
- Multi-LLM provider support (OpenAI, Anthropic, Google)
- PySide6 GUI with modern interface
- File system monitoring for automatic processing
- PDF/CSV/JSON export functionality
- Secure API key management with encryption
- Comprehensive test suite
- User documentation and quick start guide

### Security

- API keys encrypted at rest using Fernet symmetric encryption
- Secure key derivation from user-provided master password
- Keys stored in encrypted format in user home directory

[0.2.0]: https://github.com/StephenBogner/agentic_bookkeeper/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/StephenBogner/agentic_bookkeeper/releases/tag/v0.1.0
