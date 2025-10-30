# Task Specification: T-021

**Task Name:** PySide6 Main Window Setup
**Task ID:** T-021
**Phase:** Phase 2: GUI Development
**Sprint:** Sprint 4: GUI Foundation
**Created:** 2025-10-29
**Status:** Completed
**Completed:** 2025-10-27
**Priority:** Critical
**Estimated Effort:** 4 hours
**Dependencies:** T-020

---

## OBJECTIVE

Create the main application window using PySide6 with menu bar, tab widget, and basic navigation structure.

---

## REQUIREMENTS

### Functional Requirements

- Create main window with PySide6
- Implement menu bar (File, Help)
- Set up tab widget for main views
- Add application icon
- Add status bar
- Configure window size and layout
- Implement File menu (Exit)
- Implement Help menu (About)

### Non-Functional Requirements

- Window must be responsive
- Clean, professional appearance
- Proper resource management

---

## ACCEPTANCE CRITERIA

- [x] Main window opens successfully
- [x] Menus are functional
- [x] Window resizes properly
- [x] Application icon displays
- [x] Status bar shows information
- [x] Tab widget ready for content
- [x] Exit action closes application
- [x] About dialog displays

---

## EXPECTED DELIVERABLES

**Files Created:**

- `src/agentic_bookkeeper/gui/main_window.py`
- `resources/icons/app_icon.png`
- `resources/resources.qrc`

---

## VALIDATION COMMANDS

```bash
# Run main window
python -m src.agentic_bookkeeper.gui.main_window

# Run tests
pytest src/agentic_bookkeeper/tests/test_gui_main_window.py -v
```

---

## IMPLEMENTATION NOTES

### Files Created

- `src/gui/main_window.py` (main window implementation)
- `resources/` (icons and resources)
- Unit tests with 99% coverage

### Test Results

- 14 unit tests, all passing
- 99% code coverage
- Test execution time: 3.92s

---

## NOTES

**Completed:** 2025-10-27
**Result:** Fully functional main window with menu system, tab widget, and comprehensive test coverage.

---

## REVISION HISTORY

| Version | Date       | Author | Changes                    |
|---------|------------|--------|-----------------------------|
| 1.0     | 2025-10-29 | Claude | Initial specification       |

---

**Next Task:** T-022 - Dashboard Widget Implementation
