# Agentic Bookkeeper - Master Project Specification

**Version:** 1.0.0
**Created:** 2025-10-29
**Last Updated:** 2025-10-29
**Project Type:** Desktop Application (CLI + GUI)
**Workflow Type:** Agile (Phases → Sprints → Tasks)

---

## Product Overview

**Product Name:** Agentic Bookkeeper
**Package Name:** agentic_bookkeeper
**Purpose:** Intelligent bookkeeping automation system that leverages LLM technology to automatically extract transaction data from financial documents (invoices, receipts) and generate tax-compliant reports for small business owners and freelancers.

**Target Users:**
- Small business owners
- Freelancers and independent contractors
- Self-employed individuals
- Anyone needing simplified bookkeeping and tax preparation

**Key Value Proposition:**
- Automated document processing using AI/LLM vision capabilities
- Multi-LLM provider support (OpenAI, Anthropic, XAI, Google)
- Tax jurisdiction support (CRA for Canada, IRS for United States)
- Automated report generation for tax filing
- User-friendly GUI with manual override capabilities

---

## Vision & Goals

### Strategic Objectives

1. **Automation**: Reduce manual data entry by 90% through intelligent document processing
2. **Accuracy**: Achieve >95% accuracy in transaction extraction with human review
3. **Compliance**: Ensure tax compliance for CRA (Canada) and IRS (United States)
4. **Usability**: Enable non-technical users to manage bookkeeping with minimal training
5. **Flexibility**: Support multiple LLM providers for cost optimization and reliability

### Success Metrics

- Document processing time: <30 seconds per document
- Transaction extraction accuracy: >95%
- User satisfaction: >4.5/5 stars
- Test coverage: >80%
- Time savings vs manual entry: >90%

---

## Architecture Overview

### High-Level Design

```text
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌──────────────────┐  ┌─────────────────────────────────┐ │
│  │   CLI Interface  │  │      PySide6 GUI Application    │ │
│  │   (for testing)  │  │  (Dashboard, Transactions, etc) │ │
│  └──────────────────┘  └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Core Business Logic                       │
│  ┌──────────────────┐  ┌──────────────────────────────┐   │
│  │ Document         │  │ Transaction Manager          │   │
│  │ Processor        │  │ (CRUD operations)            │   │
│  └──────────────────┘  └──────────────────────────────┘   │
│  ┌──────────────────┐  ┌──────────────────────────────┐   │
│  │ Document         │  │ Report Generator             │   │
│  │ Monitor          │  │ (Income, Expense, Tax)       │   │
│  └──────────────────┘  └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    LLM Integration Layer                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────┐ ┌──────────┐ │
│  │   OpenAI    │ │  Anthropic  │ │   XAI   │ │  Google  │ │
│  │  Provider   │ │   Provider  │ │ Provider│ │ Provider │ │
│  └─────────────┘ └─────────────┘ └─────────┘ └──────────┘ │
│                  (Abstract LLMProvider base)                 │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         SQLite Database (transactions, config)       │  │
│  │  ┌──────────────────┐  ┌─────────────────────────┐  │  │
│  │  │ transactions     │  │ config                  │  │  │
│  │  │ table            │  │ table                   │  │  │
│  │  └──────────────────┘  └─────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Programming Language:**
- Python 3.10+ (type hints, modern syntax)

**GUI Framework:**
- PySide6 (Qt6 for Python)

**Database:**
- SQLite (embedded, file-based)

**LLM Providers:**
- OpenAI API (GPT-4 Vision)
- Anthropic API (Claude with vision)
- XAI API (Grok)
- Google API (Gemini with vision)

**Document Processing:**
- pypdf (PDF text extraction, formerly PyPDF2)
- Pillow (image preprocessing)
- LLM vision APIs (document understanding)

**Testing:**
- pytest (unit and integration testing)
- pytest-qt (GUI testing)
- pytest-cov (coverage reporting)

**Code Quality:**
- black (code formatting)
- flake8 (linting)
- mypy (type checking)

**Deployment:**
- PyInstaller (Windows executable)
- pip/wheel (Linux package)

---

## Phase Breakdown

### Phase 1: Core Functionality (Weeks 1-4) - 20 Tasks

**Goal:** Build foundational infrastructure and core document processing capabilities

**Sprints:**
- **Sprint 1: Project Setup & Database Foundation** (Week 1) - 6 tasks
  - Project structure, database schema, models, configuration, logging, tests
- **Sprint 2: LLM Integration & Document Processing** (Weeks 2-3) - 10 tasks
  - LLM provider abstraction, OpenAI/Anthropic/XAI/Google implementations, document processor, transaction manager, document monitor, CLI, tests
- **Sprint 3: Integration & Validation** (Week 4) - 4 tasks
  - End-to-end testing, performance optimization, error handling, documentation

**Key Deliverables:**
- Functional database with transaction storage
- Working LLM integration with 4 providers
- Document processing pipeline (PDF and images)
- CLI interface for testing
- Automated document monitoring

---

### Phase 2: GUI Development (Weeks 5-8) - 11 Tasks ✅ COMPLETE

**Goal:** Build user-friendly desktop GUI application

**Sprints:**
- **Sprint 4: GUI Foundation** (Weeks 5-6) - 5 tasks ✅
  - Main window, dashboard widget, settings dialog, application startup, GUI tests
- **Sprint 5: Transaction Management UI** (Weeks 7-8) - 6 tasks ✅
  - Transactions widget, edit dialog, add dialog, delete functionality, document review dialog, GUI tests

**Key Deliverables:**
- Main application window with navigation
- Dashboard with monitoring controls
- Settings management interface
- Transaction CRUD interface
- Document review workflow
- Comprehensive GUI test suite (128 tests, 86-100% coverage)

**Status:** ✅ All tasks completed with high test coverage

---

### Phase 3: Reporting Engine (Weeks 9-10) - 8 Tasks

**Goal:** Implement comprehensive reporting and export capabilities

**Sprints:**
- **Sprint 6: Report Generation** (Weeks 9-10) - 8 tasks
  - Report generator core, income statement template, expense report template, PDF/CSV/JSON exporters, reports widget, tests

**Key Deliverables:**
- Income statement generator
- Expense report by category
- Multi-format export (PDF, CSV, JSON)
- Report preview functionality
- Tax-jurisdiction-aware reporting

---

### Phase 4: Testing & Documentation (Weeks 11-12) - 10 Tasks

**Goal:** Comprehensive testing, quality assurance, and documentation

**Sprints:**
- **Sprint 7: Comprehensive Testing** (Week 11) - 5 tasks
  - Integration test expansion, UAT scenarios, performance testing, security testing, bug fixes
- **Sprint 8: Documentation** (Week 12) - 5 tasks
  - User guide, developer documentation, README, code documentation review, sample documents

**Key Deliverables:**
- Complete test suite with >80% coverage
- User guide with screenshots
- Developer documentation and API reference
- Sample documents and demo data
- Security review documentation

---

### Phase 5: Refinement & Distribution (Weeks 13-14) - 9 Tasks

**Goal:** Polish application and prepare for distribution

**Sprints:**
- **Sprint 9: Refinement** (Week 13) - 4 tasks
  - Performance optimization, error handling improvements, UI/UX polish, logging enhancements
- **Sprint 10: Distribution** (Week 14) - 5 tasks
  - Windows executable (PyInstaller), Linux package preparation, GitHub repository setup, license and legal, release checklist

**Key Deliverables:**
- Optimized performance (document processing <30s, queries <50ms)
- Windows installer (NSIS)
- Linux pip package
- GitHub repository with releases
- Complete license and attribution

---

## Technical Requirements

### Functional Requirements

1. **Document Processing**
   - Support PDF and image formats (JPG, PNG, JPEG)
   - Extract transaction data using LLM vision APIs
   - Validate and present for user review
   - Archive processed documents

2. **Transaction Management**
   - Create, read, update, delete transactions
   - Search and filter by date, category, type, amount
   - Support income and expense types
   - Track tax amounts
   - Store document references

3. **Configuration Management**
   - Multiple LLM provider support
   - Secure API key storage (encrypted)
   - Tax jurisdiction selection (CRA/IRS)
   - Category customization
   - Watch/archive folder configuration

4. **Reporting**
   - Income statement (revenue - expenses = net income)
   - Expense report by category
   - Date range filtering
   - Export to PDF, CSV, JSON
   - Tax-jurisdiction-specific formatting

5. **Automation**
   - Watch folder for new documents
   - Automatic processing on file detection
   - Background processing queue
   - User notification on completion

### Non-Functional Requirements

1. **Performance**
   - Document processing: <30 seconds
   - Database queries: <50ms average
   - Memory usage: <200MB
   - GUI responsiveness: <100ms UI updates

2. **Security**
   - API keys encrypted at rest
   - No sensitive data in logs
   - Input validation and sanitization
   - SQL injection prevention
   - File path validation

3. **Reliability**
   - Graceful error handling
   - Retry logic for transient failures
   - Data integrity validation
   - Transaction atomicity

4. **Usability**
   - Intuitive GUI for non-technical users
   - Clear error messages
   - Comprehensive help documentation
   - Keyboard shortcuts
   - Tooltips and inline help

5. **Maintainability**
   - >80% test coverage
   - Type hints throughout
   - Comprehensive docstrings
   - Code follows PEP 8
   - Maximum 500 lines per file

6. **Portability**
   - Cross-platform (Windows, Linux)
   - Python 3.10+ compatibility
   - Minimal system dependencies

---

## Integration Points

### External APIs

1. **OpenAI API**
   - Endpoint: https://api.openai.com/v1/chat/completions
   - Model: GPT-4 Vision
   - Authentication: API key (Bearer token)
   - Rate limits: Tier-based
   - Error handling: Retry with exponential backoff

2. **Anthropic API**
   - Endpoint: https://api.anthropic.com/v1/messages
   - Model: Claude (with vision)
   - Authentication: API key (x-api-key header)
   - Rate limits: Tier-based
   - Error handling: Retry with exponential backoff

3. **XAI API**
   - Endpoint: (XAI-specific endpoint)
   - Model: Grok
   - Authentication: API key
   - Rate limits: TBD
   - Error handling: Retry with exponential backoff

4. **Google API**
   - Endpoint: Google Vertex AI or Gemini API
   - Model: Gemini with vision
   - Authentication: API key or OAuth
   - Rate limits: Tier-based
   - Error handling: Retry with exponential backoff

### File System

- **Watch Directory:** User-configured path for incoming documents
- **Archive Directory:** User-configured path for processed documents
- **Database File:** SQLite database (default: ~/.agentic_bookkeeper/bookkeeper.db)
- **Config File:** JSON configuration (default: ~/.agentic_bookkeeper/config.json)
- **Log File:** Application logs (default: ~/.agentic_bookkeeper/logs/app.log)

---

## Risk Analysis

### Technical Risks

1. **LLM API Reliability**
   - **Risk:** API downtime or rate limiting
   - **Impact:** Cannot process documents
   - **Mitigation:** Multi-provider support, retry logic, user notification
   - **Likelihood:** Medium

2. **Extraction Accuracy**
   - **Risk:** LLM misreads document data
   - **Impact:** Incorrect transactions in database
   - **Mitigation:** User review workflow, validation rules, confidence scoring
   - **Likelihood:** Medium

3. **Performance on Large Documents**
   - **Risk:** Processing time exceeds 30 seconds
   - **Impact:** Poor user experience
   - **Mitigation:** Image optimization, pagination, background processing
   - **Likelihood:** Low

4. **Data Loss**
   - **Risk:** Database corruption or file loss
   - **Impact:** Loss of transaction data
   - **Mitigation:** Database backups, transaction archiving, data validation
   - **Likelihood:** Low

5. **API Cost**
   - **Risk:** High LLM API usage costs
   - **Impact:** User expense concerns
   - **Mitigation:** Cost tracking, provider selection, batch processing
   - **Likelihood:** Medium

### Mitigation Strategies

- Comprehensive error handling at all integration points
- Multi-provider fallback for LLM services
- Regular automated backups
- Thorough testing (unit, integration, performance)
- User documentation on cost management

---

## Timeline Estimate

**Total Project Duration:** 14 weeks

### By Phase

- **Phase 1: Core Functionality** - 4 weeks (70-90 hours)
- **Phase 2: GUI Development** - 4 weeks (45-55 hours) ✅ COMPLETE
- **Phase 3: Reporting Engine** - 2 weeks (35-45 hours)
- **Phase 4: Testing & Documentation** - 2 weeks (55-70 hours)
- **Phase 5: Refinement & Distribution** - 2 weeks (35-45 hours)

**Total Estimated Effort:** 260-330 hours

### Milestones

- **Week 4:** Core functionality complete, CLI working
- **Week 8:** GUI complete, full CRUD operations ✅ ACHIEVED
- **Week 10:** Reporting and export complete
- **Week 12:** Testing and documentation complete
- **Week 14:** Release 1.0.0 ready for distribution

---

## Quality Standards

### Testing Requirements

- **Unit Test Coverage:** >80%
- **Integration Tests:** All major workflows covered
- **GUI Tests:** All user interactions tested with pytest-qt
- **Performance Tests:** All performance targets validated
- **Security Tests:** Input validation and encryption verified

### Code Quality Standards

- **Style Guide:** PEP 8
- **Formatter:** black (100 character line length)
- **Linter:** flake8
- **Type Checking:** mypy with strict mode
- **Documentation:** Google-style docstrings for all public APIs
- **File Size:** Maximum 500 lines per file
- **Complexity:** Maximum cyclomatic complexity of 10

### Review Criteria

- All tests passing
- No linting errors
- Type checking passing
- Documentation complete
- Security review passed
- Performance targets met

---

## Success Criteria

### MVP (Minimum Viable Product) Criteria

- [ ] Process PDF and image documents automatically
- [ ] Extract transaction data with >90% accuracy
- [ ] Support 2+ LLM providers (OpenAI, Anthropic)
- [ ] Store transactions in SQLite database
- [ ] Provide GUI for transaction management
- [ ] Generate basic income and expense reports
- [ ] Export reports to PDF and CSV
- [ ] Support CRA tax categories (IRS as secondary)
- [ ] Achieve >80% test coverage
- [ ] Windows and Linux compatible

### Phase Completion Criteria

**Phase 1 Complete:**
- Core document processing working
- All 4 LLM providers implemented
- Database operations functional
- CLI interface operational
- Test coverage >80%

**Phase 2 Complete:** ✅ ACHIEVED
- GUI application launches successfully
- All CRUD operations working
- Settings management functional
- Document review workflow complete
- GUI test coverage >70%

**Phase 3 Complete:**
- Income and expense reports generating
- All export formats working (PDF, CSV, JSON)
- Reports preview functional
- Tax-jurisdiction formatting correct

**Phase 4 Complete:**
- All tests passing with >80% coverage
- User guide and developer docs complete
- Security review passed
- Performance targets met

**Phase 5 Complete:**
- Windows installer working on clean systems
- Linux package installable via pip
- GitHub repository live with releases
- License and attribution complete
- Release 1.0.0 published

---

## Reference Documents

- **Project Standards:** CLAUDE.md, DEVELOPER.md
- **Task Specifications:** specs/PHASE_X/SPRINT_Y/T-XXX_*.md
- **Project Status:** PROJECT_STATUS.md
- **Cross-Task Context:** CONTEXT.md
- **Original Task List:** specs/tasks/agentic-bookkeeper-implementation-tasks.md

---

## Version History

| Version | Date       | Author | Changes                                    |
|---------|------------|--------|--------------------------------------------|
| 1.0.0   | 2025-10-29 | Claude | Initial master specification created       |

---

**End of Master Project Specification**
