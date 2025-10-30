# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Agentic Bookkeeper.

Build command:
    pyinstaller agentic_bookkeeper.spec

This will create a Windows executable in the dist/ directory.
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Project root directory
project_root = Path(".").resolve()
src_dir = project_root / "src"

# Add src directory to path
sys.path.insert(0, str(src_dir))

block_cipher = None

# Collect all PySide6 plugins and data files
pyside6_datas = collect_data_files("PySide6")

# Collect hidden imports for dynamic modules
hidden_imports = [
    "agentic_bookkeeper",
    "agentic_bookkeeper.core",
    "agentic_bookkeeper.core.document_processor",
    "agentic_bookkeeper.core.document_monitor",
    "agentic_bookkeeper.core.transaction_manager",
    "agentic_bookkeeper.core.report_generator",
    "agentic_bookkeeper.core.exporters",
    "agentic_bookkeeper.core.exporters.pdf_exporter",
    "agentic_bookkeeper.core.exporters.csv_exporter",
    "agentic_bookkeeper.core.exporters.json_exporter",
    "agentic_bookkeeper.models",
    "agentic_bookkeeper.models.database",
    "agentic_bookkeeper.models.transaction",
    "agentic_bookkeeper.llm",
    "agentic_bookkeeper.llm.llm_provider",
    "agentic_bookkeeper.llm.openai_provider",
    "agentic_bookkeeper.llm.anthropic_provider",
    "agentic_bookkeeper.llm.xai_provider",
    "agentic_bookkeeper.llm.google_provider",
    "agentic_bookkeeper.gui",
    "agentic_bookkeeper.gui.main_window",
    "agentic_bookkeeper.gui.dashboard_widget",
    "agentic_bookkeeper.gui.transactions_widget",
    "agentic_bookkeeper.gui.transaction_edit_dialog",
    "agentic_bookkeeper.gui.transaction_add_dialog",
    "agentic_bookkeeper.gui.document_review_dialog",
    "agentic_bookkeeper.gui.settings_dialog",
    "agentic_bookkeeper.gui.reports_widget",
    "agentic_bookkeeper.utils",
    "agentic_bookkeeper.utils.config",
    "agentic_bookkeeper.utils.logger",
    "agentic_bookkeeper.utils.exceptions",
    "agentic_bookkeeper.utils.error_handler",
    # PySide6 platform plugins
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    # Additional dependencies
    "PIL._tkinter_finder",
    "watchdog.observers",
    "watchdog.observers.winapi",
    "dotenv",
    "cryptography.hazmat.backends.openssl",
    "cryptography.hazmat.bindings._rust",
]

# Collect all submodules
hidden_imports.extend(collect_submodules("reportlab"))
hidden_imports.extend(collect_submodules("pandas"))
hidden_imports.extend(collect_submodules("openai"))
hidden_imports.extend(collect_submodules("anthropic"))
hidden_imports.extend(collect_submodules("google.generativeai"))

a = Analysis(
    [str(src_dir / "agentic_bookkeeper" / "main.py")],
    pathex=[str(src_dir)],
    binaries=[],
    datas=pyside6_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "IPython",
        "jupyter",
        "notebook",
        "sphinx",
        "pytest",
        "test",
        "tests",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AgenticBookkeeper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windowed application (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='resources/icon.ico',  # Uncomment if you add an icon file
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AgenticBookkeeper",
)
