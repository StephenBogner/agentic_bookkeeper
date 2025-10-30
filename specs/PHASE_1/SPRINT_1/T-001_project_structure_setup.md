# Task Specification: T-001

**Task Name:** Project Structure Setup
**Task ID:** T-001
**Phase:** Phase 1: Core Functionality
**Sprint:** Sprint 1: Project Setup & Database Foundation
**Created:** 2025-10-29
**Status:** Not Started
**Priority:** Critical
**Estimated Effort:** 2 hours
**Dependencies:** None

---

## OBJECTIVE

Set up the complete project structure, development environment, and initial configuration files to establish the foundation for the Agentic Bookkeeper application.

**Success Criteria:**

- Project directory structure matches specifications
- Virtual environment configured and working
- Git repository initialized with proper ignore rules
- All dependencies install without errors
- Environment configuration template created

---

## REQUIREMENTS

### Functional Requirements

1. **Virtual Environment Setup**
   - Create Python 3.10+ virtual environment
   - Activate and validate environment
   - Document activation commands

2. **Git Repository Initialization**
   - Initialize git repository
   - Create `.gitignore` for Python projects
   - Configure repository settings
   - Create initial commit

3. **Directory Structure Creation**
   - Create all required directories per project specification
   - Add `__init__.py` files in all Python packages
   - Verify directory structure is correct

4. **Dependency Management**
   - Create `requirements.txt` with production dependencies
   - Create `requirements-dev.txt` with development dependencies
   - Install all dependencies and verify

5. **Configuration Template**
   - Create `.env.example` template file
   - Document required environment variables
   - Add security notes for API keys

### Non-Functional Requirements

- Cross-platform compatibility (Windows, Linux)
- Documentation of setup process
- Reproducible environment setup

---

## DESIGN CONSIDERATIONS

### Directory Structure

```text
agentic_bookkeeper_module/
├── .venv/                      # Virtual environment (gitignored)
├── src/
│   └── agentic_bookkeeper/
│       ├── __init__.py
│       ├── core/
│       │   └── __init__.py
│       ├── models/
│       │   └── __init__.py
│       ├── llm/
│       │   └── __init__.py
│       ├── gui/
│       │   └── __init__.py
│       ├── utils/
│       │   └── __init__.py
│       └── tests/
│           └── __init__.py
├── tests/                      # Additional test directory if needed
├── config/                     # Configuration files (categories, etc.)
├── docs/                       # Documentation
├── specs/                      # Task specifications (already exists)
├── resources/                  # Images, icons, etc.
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── pyproject.toml             # Already exists
├── CLAUDE.md                  # Already exists
├── PROJECT_STATUS.md          # Already exists
├── CONTEXT.md                 # Already exists
└── README.md
```

### Dependencies to Include

**requirements.txt (Production):**

```text
PySide6>=6.6.0
pypdf>=3.17.0
Pillow>=10.1.0
openai>=1.3.0
anthropic>=0.7.0
google-generativeai>=0.3.0
python-dotenv>=1.0.0
watchdog>=3.0.0
cryptography>=41.0.0
```

**requirements-dev.txt (Development):**

```text
pytest>=7.4.0
pytest-qt>=4.2.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
black>=23.11.0
flake8>=6.1.0
mypy>=1.7.0
```

---

## ACCEPTANCE CRITERIA

### Must Have

- [ ] Virtual environment created with Python 3.10+
- [ ] Git repository initialized with .gitignore
- [ ] All directories created with **init**.py files
- [ ] requirements.txt created and dependencies install successfully
- [ ] requirements-dev.txt created and dev dependencies install successfully
- [ ] .env.example template created with required variables
- [ ] Project structure matches specification exactly

### Should Have

- [ ] README.md created with basic project information
- [ ] Initial git commit made with project structure
- [ ] Documentation of setup process in comments

### Nice to Have

- [ ] Setup script for automated environment creation
- [ ] Pre-commit hooks configured
- [ ] EditorConfig file for consistent formatting

---

## CONTEXT REQUIRED

### Information Needed

- Python version requirements (3.10+)
- Project name and package structure (from CLAUDE.md)
- Standard coding conventions (from CLAUDE.md)

### Artifacts from Previous Tasks

- None (this is the first task)

---

## EXPECTED DELIVERABLES

### Files to Create

- `.gitignore` - Python-specific git ignore rules
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies
- `.env.example` - Environment variable template
- `src/agentic_bookkeeper/__init__.py` - Package initialization
- `src/agentic_bookkeeper/core/__init__.py`
- `src/agentic_bookkeeper/models/__init__.py`
- `src/agentic_bookkeeper/llm/__init__.py`
- `src/agentic_bookkeeper/gui/__init__.py`
- `src/agentic_bookkeeper/utils/__init__.py`
- `src/agentic_bookkeeper/tests/__init__.py`
- `config/` directory
- `docs/` directory
- `resources/` directory

### Directories to Create

- `src/agentic_bookkeeper/core/`
- `src/agentic_bookkeeper/models/`
- `src/agentic_bookkeeper/llm/`
- `src/agentic_bookkeeper/gui/` (may already exist)
- `src/agentic_bookkeeper/utils/`
- `src/agentic_bookkeeper/tests/` (may already exist)
- `config/`
- `docs/`
- `resources/`

---

## VALIDATION COMMANDS

```bash
# Verify virtual environment
python --version  # Should show 3.10+
which python      # Should show .venv path

# Verify directory structure
ls -R src/agentic_bookkeeper/

# Verify git repository
git status

# Verify dependencies install
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip list

# Verify imports work
python -c "import agentic_bookkeeper; print('Package imports successfully')"

# Run tests (should find no tests yet but should not error)
pytest --collect-only
```

---

## IMPLEMENTATION NOTES

### Step-by-Step Execution

1. **Create Virtual Environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or .venv\Scripts\activate  # Windows
   ```

2. **Initialize Git** (if not already done)

   ```bash
   git init
   ```

3. **Create Directory Structure**

   ```bash
   mkdir -p src/agentic_bookkeeper/{core,models,llm,gui,utils,tests}
   mkdir -p config docs resources
   touch src/agentic_bookkeeper/__init__.py
   touch src/agentic_bookkeeper/core/__init__.py
   touch src/agentic_bookkeeper/models/__init__.py
   touch src/agentic_bookkeeper/llm/__init__.py
   touch src/agentic_bookkeeper/gui/__init__.py
   touch src/agentic_bookkeeper/utils/__init__.py
   touch src/agentic_bookkeeper/tests/__init__.py
   ```

4. **Create Dependency Files**
   - Create requirements.txt with production dependencies
   - Create requirements-dev.txt with development dependencies

5. **Create Configuration Template**
   - Create .env.example with placeholders for API keys

6. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

7. **Verify Setup**
   - Run validation commands above
   - Ensure no errors occur

---

## NOTES

### Important Considerations

- Some directories may already exist from previous work (gui/, tests/)
- pyproject.toml already exists - verify it has correct dependencies
- CLAUDE.md, PROJECT_STATUS.md, CONTEXT.md already exist
- specs/ directory already exists with task specifications
- Do NOT overwrite existing files without checking content first

### Potential Issues

- **Issue:** Virtual environment activation syntax differs on Windows/Linux
  - **Solution:** Document both activation methods

- **Issue:** Some directories may already exist
  - **Solution:** Use `mkdir -p` to avoid errors on existing directories

- **Issue:** Dependency conflicts
  - **Solution:** Use specific version requirements, test installations

### Environment Variables Template

```bash
# .env.example

# LLM Provider API Keys (choose one or more)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
XAI_API_KEY=your_xai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Application Configuration
DEFAULT_LLM_PROVIDER=openai
TAX_JURISDICTION=CRA  # or IRS
FISCAL_YEAR_START=01-01

# Directory Paths
WATCH_DIRECTORY=./documents/incoming
ARCHIVE_DIRECTORY=./documents/archive
DATABASE_PATH=./data/bookkeeper.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

---

## COMPLETION CHECKLIST

- [ ] Virtual environment created and activated
- [ ] All directories created with correct structure
- [ ] All **init**.py files created
- [ ] requirements.txt created with production dependencies
- [ ] requirements-dev.txt created with dev dependencies
- [ ] .env.example created with all required variables
- [ ] .gitignore created with Python patterns
- [ ] All dependencies installed successfully
- [ ] Package imports successfully (basic smoke test)
- [ ] Git repository initialized with initial commit
- [ ] Documentation updated in CONTEXT.md

---

## REVISION HISTORY

| Version | Date       | Author | Changes                         |
|---------|------------|--------|---------------------------------|
| 1.0     | 2025-10-29 | Claude | Initial task specification      |

---

**Next Task:** T-002 - Database Schema Implementation
