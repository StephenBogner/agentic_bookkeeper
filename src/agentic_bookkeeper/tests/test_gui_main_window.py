"""
Package Name: agentic_bookkeeper
File Name: test_gui_main_window.py
Description: Unit tests for the MainWindow GUI component
Author: Stephen Bogner, P.Eng.
LLM: claude-sonnet-4-5-20250929
Ownership: Stephen Bogner - All Rights Reserved.  See LICENSE.md
Date Created: 2025-10-27
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtTest import QTest

from agentic_bookkeeper.gui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit - other tests might need it


@pytest.fixture
def main_window(qapp, qtbot):
    """Create MainWindow instance for testing."""
    window = MainWindow()
    qtbot.addWidget(window)
    return window


def test_main_window_initialization(main_window):
    """Test that the main window initializes correctly."""
    assert main_window is not None
    assert main_window.windowTitle() == "Agentic Bookkeeper"
    assert main_window.minimumSize().width() == 1024
    assert main_window.minimumSize().height() == 768


def test_main_window_menu_bar(main_window):
    """Test that the menu bar is created with File and Help menus."""
    menu_bar = main_window.menuBar()
    assert menu_bar is not None

    # Check for File menu
    menus = menu_bar.findChildren(object)
    menu_titles = [action.text() for action in menu_bar.actions()]

    assert "&File" in menu_titles
    assert "&Help" in menu_titles


def test_file_menu_exit_action(main_window):
    """Test that the File menu has an Exit action."""
    menu_bar = main_window.menuBar()
    file_menu = None

    for action in menu_bar.actions():
        if action.text() == "&File":
            file_menu = action.menu()
            break

    assert file_menu is not None

    # Check for Exit action - convert to list first to avoid Qt object deletion issues
    exit_action = None
    actions_list = list(file_menu.actions())
    for action in actions_list:
        try:
            if (
                not action.isSeparator() and action.text() and "xit" in action.text()
            ):  # Match Exit or E&xit
                exit_action = action
                break
        except RuntimeError:
            # Action was deleted, skip it
            continue

    assert exit_action is not None
    assert exit_action.shortcut().toString() == "Ctrl+Q"


def test_help_menu_about_action(main_window):
    """Test that the Help menu has an About action."""
    menu_bar = main_window.menuBar()
    help_menu = None

    for action in menu_bar.actions():
        if action.text() == "&Help":
            help_menu = action.menu()
            break

    assert help_menu is not None

    # Check for About action - convert to list first to avoid Qt object deletion issues
    about_action = None
    actions_list = list(help_menu.actions())
    for action in actions_list:
        try:
            if not action.isSeparator() and action.text() and "About" in action.text():
                about_action = action
                break
        except RuntimeError:
            # Action was deleted, skip it
            continue

    assert about_action is not None


def test_tab_widget_exists(main_window):
    """Test that the tab widget is created."""
    tab_widget = main_window.get_tab_widget()
    assert tab_widget is not None
    assert tab_widget.count() == 3  # Dashboard, Transactions, Reports


def test_tab_widget_tabs(main_window):
    """Test that the correct tabs are created."""
    tab_widget = main_window.get_tab_widget()

    tab_titles = []
    for i in range(tab_widget.count()):
        tab_titles.append(tab_widget.tabText(i))

    assert "Dashboard" in tab_titles
    assert "Transactions" in tab_titles
    assert "Reports" in tab_titles


def test_status_bar_exists(main_window):
    """Test that the status bar is created."""
    status_bar = main_window.statusBar()
    assert status_bar is not None


def test_show_status_message(main_window):
    """Test showing a status message."""
    message = "Test status message"
    main_window.show_status_message(message, 1000)

    status_bar = main_window.statusBar()
    assert status_bar.currentMessage() == message


@patch("agentic_bookkeeper.gui.main_window.QMessageBox.about")
def test_about_dialog(mock_about, main_window, qtbot):
    """Test that the About dialog can be triggered."""
    # Find the About action
    menu_bar = main_window.menuBar()
    help_menu = None

    for action in menu_bar.actions():
        if action.text() == "&Help":
            help_menu = action.menu()
            break

    assert help_menu is not None

    # Find and trigger About action - convert to list first to avoid Qt object deletion issues
    actions_list = list(help_menu.actions())
    for action in actions_list:
        try:
            if not action.isSeparator() and action.text() and "About" in action.text():
                action.trigger()
                break
        except RuntimeError:
            # Action was deleted, skip it
            continue

    # Verify the about dialog was called
    mock_about.assert_called_once()
    call_args = mock_about.call_args[0]
    assert "Agentic Bookkeeper" in call_args[2]
    assert "Stephen Bogner" in call_args[2]


def test_close_event_accept(main_window, qtbot):
    """Test that closing the window is auto-accepted during testing."""
    from PySide6.QtGui import QCloseEvent

    # Create a mock close event
    event = QCloseEvent()

    # Call closeEvent - should be auto-accepted in test mode
    main_window.closeEvent(event)

    # Verify event was accepted without showing dialog
    assert event.isAccepted() is True


@patch("agentic_bookkeeper.gui.main_window.QMessageBox.question")
@patch.dict("os.environ", {}, clear=True)
def test_close_event_reject(mock_question, main_window, qtbot):
    """Test that closing the window can be cancelled (in non-test mode)."""
    from PySide6.QtGui import QCloseEvent

    # Mock user clicking No
    mock_question.return_value = QMessageBox.StandardButton.No

    # Remove test mode attributes to simulate production behavior
    if hasattr(main_window, "_testing_mode"):
        delattr(main_window, "_testing_mode")

    # Create a mock close event
    event = QCloseEvent()

    # Call closeEvent directly
    main_window.closeEvent(event)

    # Verify event was ignored
    assert event.isAccepted() is False
    mock_question.assert_called_once()


def test_window_icon(main_window):
    """Test that window icon is set if file exists."""
    icon = main_window.windowIcon()
    assert icon is not None

    # Check if icon file exists
    icon_path = Path(__file__).parent.parent.parent.parent / "resources" / "icons" / "app_icon.png"
    if icon_path.exists():
        assert not icon.isNull()


def test_window_resizable(main_window):
    """Test that the window is resizable."""
    initial_size = main_window.size()

    # Resize the window
    new_width = initial_size.width() + 100
    new_height = initial_size.height() + 100
    main_window.resize(new_width, new_height)

    # Check that the size changed
    assert main_window.width() == new_width
    assert main_window.height() == new_height


def test_minimum_size_enforced(main_window):
    """Test that minimum size is enforced."""
    # Try to resize below minimum
    main_window.resize(500, 400)

    # Size should be constrained to minimum
    assert main_window.width() >= 1024
    assert main_window.height() >= 768
