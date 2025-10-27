# Agentic Bookkeeper - Product Plan

**Version**: 1.0
**Date**: 2025-10-24
**Author**: Stephen Bogner, P.Eng.
**Status**: Planning Phase

---

## Executive Summary

**Agentic Bookkeeper** is an AI-powered desktop application that automates bookkeeping for small businesses and sole
proprietors. The system eliminates manual data entry by monitoring a directory for financial documents, extracting
transaction data using LLM APIs, storing records in a local SQLite database, and generating tax-compliant financial
statements on demand.

**Vision**: Provide small business owners with effortless, accurate financial record-keeping without expensive
subscriptions or manual data entry.

**Value Proposition**: Drop documents in a folder, get organized financial records and professional statements
automatically.

---

## Product Overview

### Problem Statement

Small businesses and sole proprietors struggle with:

- Time-consuming manual data entry for bookkeeping
- Expensive accounting software subscriptions ($300-600/year)
- Complex accounting systems with steep learning curves
- Risk of errors in manual transaction recording
- Difficulty maintaining tax-compliant records

### Solution

Agentic Bookkeeper provides:

- **Automated Processing**: AI extracts data from invoices, receipts, and payments
- **Zero Manual Entry**: Just drop documents in a folder
- **Local & Private**: All data stored locally, no cloud dependencies
- **Tax Compliance**: Built-in CRA and IRS category support
- **Professional Reports**: Generate income statements and expense reports
- **Cost Effective**: One-time purchase, minimal ongoing costs (LLM API usage only)

### Target Users

**Primary Audience**:

- Sole proprietors and freelancers
- Small businesses (1-10 employees)
- Self-employed professionals (consultants, contractors)

**User Characteristics**:

- Limited accounting knowledge
- Budget-conscious
- Privacy-aware (prefer local storage)
- Process 10-100 transactions per month
- Need tax-compliant records for CRA or IRS filing

---

## Core Features

### MVP Features (Phase 1)

#### 1. Automated Document Monitoring

- Monitor designated directory for new financial documents
- Support formats: PDF, PNG, JPG, JPEG
- Automatic processing on file detection
- Archive processed documents with timestamps

#### 2. AI-Powered Data Extraction

- LLM API integration (OpenAI, Anthropic, XAI, Google)
- Extract transaction fields:
  - Date, vendor/customer, amount
  - Description, tax amounts
  - Document type (invoice/receipt/payment)
- Categorize using CRA or IRS tax categories
- User review and confirmation workflow

#### 3. Transaction Database

- SQLite local database
- Transaction records with full audit trail
- Configuration storage
- Data integrity and backup support

#### 4. Financial Statement Generation

- Income Statement (Profit & Loss)
- Expense Report by category
- Date range filtering (monthly, quarterly, annual, custom)
- Export formats: PDF, CSV, JSON
- Tax-compliant formatting

#### 5. User Interface

- PySide6 desktop GUI
- Dashboard: Recent transactions, quick stats
- Transactions view: Search, edit, delete
- Reports view: Generate and export
- Settings: Configure directories, LLM providers, tax jurisdiction

#### 6. Multi-Provider LLM Support

- Abstract provider interface
- OpenAI implementation
- Anthropic implementation
- XAI implementation
- Google implementation
- Easy provider switching

---

## Technical Architecture

### System Design

**Architecture Pattern**: Modular object-oriented design with clear separation of concerns

**Components**:

1. **Core Services**
   - Document Monitor (watchdog-based file system monitoring)
   - Document Processor (LLM API orchestration)
   - Transaction Manager (database operations)
   - Report Generator (statement creation)

2. **Data Layer**
   - Transaction model (data validation)
   - Database manager (SQLite connection, schema, migrations)

3. **LLM Integration**
   - Abstract LLM provider interface
   - Concrete provider implementations
   - Prompt engineering for financial document analysis
   - Response parsing and validation

4. **GUI Layer**
   - Main window (application shell)
   - Dashboard widget (overview)
   - Transactions widget (CRUD operations)
   - Reports widget (generation and export)
   - Settings dialog (configuration)

5. **Utilities**
   - Configuration management (dotenv, JSON)
   - Logging (structured logging)
   - Input validation
   - Error handling

### Technology Stack

**Core Technologies**:

- **Language**: Python 3.10+
- **GUI Framework**: PySide6 (Qt for Python)
- **Database**: SQLite3
- **LLM Integration**: Direct API calls (requests library)
- **Document Processing**: PyPDF2, Pillow, pytesseract
- **File Monitoring**: watchdog
- **Report Generation**: ReportLab (PDF), pandas (CSV)
- **Configuration**: python-dotenv, JSON
- **Testing**: pytest (>80% coverage target)
- **Logging**: Python logging module

**Development Tools**:

- **Version Control**: Git/GitHub
- **Code Quality**: black, flake8, mypy
- **Package Management**: pip, requirements.txt
- **Distribution**: PyInstaller (Windows exe), pip package (Linux)

### Data Models

**Transaction Schema**:

```python
{
    "id": int,                          # Auto-increment primary key
    "date": str,                        # YYYY-MM-DD format
    "type": str,                        # 'income' or 'expense'
    "category": str,                    # CRA/IRS compliant category
    "vendor_customer": str,             # Counterparty name
    "description": str,                 # Transaction details
    "amount": float,                    # Transaction amount
    "tax_amount": float,                # Tax component
    "document_filename": str,           # Reference to source document
    "created_at": str,                  # ISO timestamp
    "modified_at": str                  # ISO timestamp
}
```

**Configuration Schema**:

```python
{
    "watch_directory": str,             # Path to monitor
    "processed_directory": str,         # Archive location
    "llm_provider": str,                # openai|anthropic|xai|google
    "llm_api_key": str,                 # Encrypted API key
    "tax_jurisdiction": str,            # CRA|IRS
    "fiscal_year_start": str,           # MM-DD format
    "database_path": str,               # SQLite file location
    "log_level": str                    # DEBUG|INFO|WARNING|ERROR
}
```

### Security Considerations

- API keys stored encrypted in local config
- No cloud data transmission (except LLM API calls)
- Local SQLite database with file permissions
- Input validation on all user inputs
- Sanitization of file paths
- Rate limiting on LLM API calls

---

## Development Roadmap

### Phase 1: Core Functionality (Weeks 1-4)

**Goal**: Functional backend with CLI interface

**Deliverables**:

- SQLite database schema and migrations
- Transaction and Configuration models
- Document monitor service (watchdog integration)
- LLM provider abstraction and implementations (OpenAI, Anthropic)
- Document processor with extraction logic
- Transaction manager (CRUD operations)
- Command-line interface for testing
- Unit tests for core components (>80% coverage)

**Validation Criteria**:

- Successfully process test documents via CLI
- Extract data with >90% accuracy on sample documents
- Store and retrieve transactions from database
- Switch between LLM providers

### Phase 2: GUI Development (Weeks 5-8)

**Goal**: Complete desktop application with user interface

**Deliverables**:

- PySide6 main window framework
- Dashboard widget (recent transactions, stats, monitoring status)
- Transactions widget (table view, search, edit, delete, manual add)
- Reports widget (type selection, date range, format, preview)
- Settings dialog (directory config, LLM selection, API keys, tax jurisdiction)
- Application menu and navigation
- Start/stop monitoring controls
- User confirmation workflow for extracted data

**Validation Criteria**:

- User can complete full workflow: setup → drop document → review → generate report
- All UI components functional and responsive
- Settings persist across application restarts
- Monitoring service starts/stops reliably

### Phase 3: Reporting Engine (Weeks 9-10)

**Goal**: Professional financial statement generation

**Deliverables**:

- Report generator class with template system
- Income Statement template (revenue, expenses, net income)
- Expense Report by category template
- PDF export using ReportLab (formatted, professional)
- CSV export with proper headers and formatting
- JSON export for data portability
- Date range filtering logic
- Report preview in GUI

**Validation Criteria**:

- Generate accurate Income Statement from transaction data
- Expense report correctly categorizes by CRA/IRS categories
- PDF output is professional and tax-filing ready
- CSV/JSON exports are valid and importable

### Phase 4: Testing & Documentation (Weeks 11-12)

**Goal**: Production-ready quality and documentation

**Deliverables**:

- Comprehensive pytest suite (>80% coverage)
- Integration tests with real document samples
- User Guide (installation, setup, daily use, troubleshooting)
- Developer documentation (architecture, API, contribution guide)
- Installation instructions (Windows, Linux)
- Sample documents for testing
- Error handling improvements
- Logging enhancements

**Validation Criteria**:

- All tests pass
- Test coverage >80%
- Documentation is complete and clear
- New user can install and use within 10 minutes

### Phase 5: Refinement & Distribution (Weeks 13-14)

**Goal**: Polished product ready for distribution

**Deliverables**:

- Performance optimization (document processing <30 seconds)
- Error handling refinements
- User feedback integration (if beta testing)
- Windows executable with PyInstaller
- Linux pip package
- Installation scripts
- README and LICENSE files
- GitHub repository setup
- Release notes

**Validation Criteria**:

- Meets all success metrics (see below)
- Passes user acceptance testing
- Windows exe installs and runs on clean system
- Linux package installs via pip

---

## Success Metrics

### Functional Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Extraction Accuracy | >90% | Manual validation on 100 test documents |
| Processing Speed | <30 seconds per document | Automated timing tests |
| Database Reliability | Zero data loss | Stress testing, crash recovery tests |
| Report Accuracy | 100% calculation accuracy | Automated validation against known data |
| Test Coverage | >80% | pytest coverage report |

### User Experience Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Setup Time | <10 minutes | Timed user testing |
| Time to First Report | <30 minutes | User testing (install to first report) |
| Error Rate | <5% manual corrections | Track corrections in usage |
| User Satisfaction | >4/5 rating | Beta user feedback |

### Performance Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| GUI Responsiveness | <100ms UI updates | Performance profiling |
| Database Query Time | <50ms average | Query logging |
| Memory Usage | <200MB | System monitoring |
| LLM API Response Time | <10 seconds | API timing logs |

---

## Risk Assessment & Mitigation

### Technical Risks

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|-----------|--------|-------------------|
| LLM extraction errors | Medium | Medium | User review/confirmation workflow; fallback to manual entry |
| API rate limits | Low | Low | Configurable providers; request throttling; offline queue |
| Document format variations | Medium | Medium | Multi-attempt extraction; OCR fallback; manual correction UI |
| Database corruption | Low | High | Automated backups; transaction logging; recovery procedures |
| API cost overruns | Low | Medium | Usage monitoring; cost alerts; provider switching |

### Business Risks

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|-----------|--------|-------------------|
| Low user adoption | Medium | High | Beta testing; user feedback; iteration |
| Competitive alternatives | Medium | Medium | Focus on simplicity and local-first approach |
| LLM provider changes | Medium | Medium | Multi-provider architecture; provider abstraction |
| Regulatory changes | Low | Medium | Modular category system; easy updates |

### Development Risks

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|-----------|--------|-------------------|
| Timeline overrun | Medium | Medium | Phased approach; MVP focus; scope management |
| Skill gaps | Low | Low | Research phase; proof of concepts; tutorials |
| Scope creep | Medium | Medium | Strict MVP definition; post-MVP roadmap |
| Technical blockers | Low | High | Early prototyping; technical spikes |

---

## Resource Requirements

### Development Resources

**Single Developer**:

- Python development expertise
- PySide6/Qt experience (or learning capacity)
- SQLite database knowledge
- LLM API integration experience
- Testing and documentation skills

**Estimated Effort**:

- Part-time (20 hrs/week): 14 weeks
- Full-time (40 hrs/week): 7 weeks

### Infrastructure

**Development Environment**:

- Local machine (Windows or Ubuntu)
- Python 3.10+ development environment
- Git/GitHub account
- LLM API accounts (OpenAI, Anthropic, XAI, Google)

**Testing Resources**:

- Sample financial documents (invoices, receipts)
- Test LLM API credits
- Virtual machines for testing (Windows, Linux)

### Financial Budget

| Item | Estimated Cost |
|------|---------------|
| LLM API usage (development) | $50-100 |
| Domain name (optional) | $15/year |
| Code signing certificate (optional) | $0-200 |
| **Total Development Budget** | **$65-315** |

**Ongoing Costs (per user)**:

- LLM API usage: $2-5/month (typical usage)
- No infrastructure costs (local-only)

---

## User Workflows

### Initial Setup Workflow

1. Download and install application
2. Launch Agentic Bookkeeper
3. First-run setup wizard:
   - Select tax jurisdiction (CRA/IRS)
   - Set fiscal year start date
   - Choose LLM provider
   - Enter API key (encrypted storage)
   - Specify watch directory
   - Specify processed archive directory
4. Verify configuration
5. Start monitoring service

**Expected Time**: <10 minutes

### Daily Operation Workflow

1. User saves/scans financial document to watch directory
2. System detects new file (near real-time)
3. LLM processes document and extracts data
4. Notification shows extracted data for review
5. User confirms or edits categorization
6. Transaction saved to database
7. Document moved to processed archive
8. Dashboard updates with new transaction

**Expected Time**: <1 minute per document

### Report Generation Workflow

1. User navigates to Reports tab
2. Selects report type (Income Statement, Expense Report)
3. Chooses date range (preset or custom)
4. Previews report in application
5. Selects export format (PDF, CSV, JSON)
6. Saves report to desired location
7. Uses report for tax filing or analysis

**Expected Time**: <2 minutes

### Transaction Management Workflow

1. User navigates to Transactions tab
2. Searches/filters transactions (by date, vendor, category, amount)
3. Reviews transaction details
4. Edits incorrect extractions
5. Deletes duplicates
6. Manually adds missing transactions
7. Changes persist to database

**Expected Time**: Variable based on corrections needed

---

## Deployment Strategy

### Distribution Channels

**Windows Users**:

- Standalone executable (.exe) via PyInstaller
- GitHub Releases page for download
- Optional: Future Microsoft Store listing

**Linux Users**:

- Python package via pip
- GitHub repository with requirements.txt
- Optional: Future PyPI listing

### Installation Process

**Windows**:

1. Download `AgenticBookkeeper-Setup.exe`
2. Run installer
3. Follow installation wizard
4. Launch from Start Menu

**Linux**:

```bash
# Install via pip
pip install agentic-bookkeeper

# Or from source
git clone https://github.com/user/agentic-bookkeeper.git
cd agentic-bookkeeper
pip install -r requirements.txt
python main.py
```

### System Requirements

**Minimum Requirements**:

- OS: Windows 10/11 or Ubuntu 20.04+
- Python: 3.10+ (if not using standalone exe)
- RAM: 512MB available
- Disk: 100MB free space
- Internet: Required for LLM API calls

**Recommended**:

- RAM: 1GB available
- Disk: 500MB (for document archive)
- SSD for faster database operations

---

## Future Enhancements (Post-MVP)

### Phase 6: Advanced Features

- Bank statement import and reconciliation
- Multi-year comparison reports
- Budget tracking and alerts
- Recurring transaction support
- Multi-currency support
- Advanced search and filtering

### Phase 7: Integration & Export

- Export to QuickBooks format
- Export to Xero format
- Integration with banking APIs
- CRA/IRS direct filing support (if feasible)

### Phase 8: Enhanced User Experience

- Mobile companion app for receipt capture
- Cloud backup option (encrypted)
- Multi-user support (shared databases)
- Custom category definitions
- Audit trail and compliance reporting

### Phase 9: AI Enhancements

- Learn from user corrections
- Auto-categorization improvements
- Anomaly detection (duplicate payments, unusual amounts)
- Predictive analytics (expense forecasting)

---

## Agent OS Installation

**Status**: Optional - Not required for MVP

**Decision**: Defer Agent OS installation until project demonstrates need for advanced AI-assisted development
workflows. Current development scope is manageable with standard Python tooling.

**Rationale**:

- MVP is well-defined and straightforward
- Single developer with clear architecture
- Standard Python development practices sufficient
- Can add Agent OS later if project scales

---

## Next Steps

### Immediate Actions

1. **Finalize Development Environment**
   - Set up Python 3.10+ virtual environment
   - Install development dependencies
   - Configure Git repository
   - Set up testing framework

2. **Create Initial Project Structure**
   - Generate directory structure
   - Create placeholder files
   - Set up configuration files (.env.example, requirements.txt)
   - Initialize version control

3. **Technical Spike: LLM Integration**
   - Test document extraction with OpenAI API
   - Validate prompt engineering approach
   - Measure accuracy on sample documents
   - Estimate API costs

4. **Begin Phase 1 Development**
   - Implement database schema
   - Create transaction models
   - Build document monitor service
   - Develop LLM provider abstraction

### Sprint Planning

**Sprint 1 (Week 1-2)**: Database & Models

- SQLite schema
- Transaction CRUD
- Configuration management
- Unit tests

**Sprint 2 (Week 3-4)**: Document Processing

- File monitoring
- LLM integration
- Extraction pipeline
- CLI interface

**Sprint 3 (Week 5-6)**: GUI Foundation

- Main window
- Dashboard widget
- Basic navigation
- Settings dialog

**Sprint 4 (Week 7-8)**: Transaction Management UI

- Transaction list view
- Edit/delete functionality
- Search and filter
- Manual entry

**Sprint 5 (Week 9-10)**: Reporting

- Report generator
- Income statement
- Expense report
- Export functionality

**Sprint 6 (Week 11-12)**: Testing & Documentation

- Test suite completion
- User guide
- API documentation
- Bug fixes

**Sprint 7 (Week 13-14)**: Polish & Release

- Performance optimization
- Distribution packaging
- Release preparation
- Beta testing

---

## Success Criteria for Launch

**MVP is ready for launch when**:

- ✅ All Phase 1-5 deliverables complete
- ✅ Test coverage >80%
- ✅ All success metrics met
- ✅ User documentation complete
- ✅ Windows executable installs and runs
- ✅ Linux package installs via pip
- ✅ No critical bugs
- ✅ Beta testing feedback incorporated
- ✅ GitHub repository public and documented

---

## Monitoring & Iteration

**Post-Launch**:

- Monitor user feedback and bug reports
- Track actual LLM extraction accuracy
- Measure API costs in production
- Gather feature requests
- Prioritize post-MVP enhancements
- Release updates quarterly

**Continuous Improvement**:

- Refine LLM prompts based on errors
- Add support for new document formats
- Improve UI based on user feedback
- Optimize performance bottlenecks
- Expand test coverage

---

## Conclusion

Agentic Bookkeeper is a well-scoped, achievable product that solves a real problem for small businesses and sole
proprietors. The technology stack is proven, the architecture is modular, and the development roadmap is realistic for
a single developer.

By focusing on the MVP features and maintaining strict scope control, the project can deliver significant value within
the 14-week timeline. The multi-provider LLM architecture provides flexibility, and the local-first approach addresses
privacy concerns while minimizing ongoing costs.

Success depends on maintaining focus on the core value proposition: **effortless, automated bookkeeping through simple
document dropping**. Every feature should support this primary goal.

---

**Document Version**: 1.0
**Last Updated**: 2025-10-24
**Next Review**: Start of Phase 1 Development
