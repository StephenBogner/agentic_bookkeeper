# Windows Executable Build Guide

**Version:** 0.1.0
**Last Updated:** 2025-10-29
**Author:** Stephen Bogner

---

## Overview

This guide covers building a standalone Windows executable for Agentic Bookkeeper using PyInstaller and creating an installer using NSIS (Nullsoft Scriptable Install System).

**Build Process:**

1. Build executable with PyInstaller (.exe file)
2. Create installer with NSIS (.exe installer)
3. Test on clean Windows 10/11 system
4. (Optional) Code sign for production release

---

## Prerequisites

### Required Software

1. **Windows 10 or Windows 11**
   - 64-bit operating system
   - Administrator privileges

2. **Python 3.8 or higher**
   - Download: https://www.python.org/downloads/
   - Install with "Add to PATH" option enabled
   - Verify: `python --version`

3. **Git** (optional, for version control)
   - Download: https://git-scm.com/download/win
   - Verify: `git --version`

4. **NSIS 3.0 or higher** (for installer creation)
   - Download: https://nsis.sourceforge.io/Download
   - Install to default location: `C:\Program Files (x86)\NSIS`
   - Add NSIS to PATH: `C:\Program Files (x86)\NSIS`
   - Verify: `makensis /?`

### Required Python Packages

All packages listed in `requirements.txt` plus:

- `pyinstaller>=6.0.0` (automatically installed by build script)

### System Requirements

- **Disk Space:** At least 2 GB free
  - Source code: ~50 MB
  - Virtual environment: ~500 MB
  - Build artifacts: ~500 MB
  - Final installer: ~100 MB

- **Memory:** Minimum 4 GB RAM (8 GB recommended)

- **Internet Connection:** Required for downloading dependencies

---

## Quick Start

### Option 1: Automated Build (Recommended)

```cmd
REM 1. Navigate to project directory
cd C:\path\to\agentic_bookkeeper_module

REM 2. Build executable
build_windows.bat

REM 3. Build installer
cd installer
build_installer.bat

REM 4. Test installer
..\dist\AgenticBookkeeper-0.1.0-Setup.exe
```text

### Option 2: Manual Build

See detailed instructions below.

---

## Detailed Build Instructions

### Step 1: Prepare Build Environment

1. **Clone/Download Project**

   ```cmd
   git clone https://github.com/yourusername/agentic_bookkeeper.git
   cd agentic_bookkeeper
   ```

2. **Create Virtual Environment**

   ```cmd
   python -m venv venv
   ```

3. **Activate Virtual Environment**

   ```cmd
   venv\Scripts\activate
   ```

4. **Install Dependencies**

   ```cmd
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   pip install pyinstaller>=6.0.0
   ```

### Step 2: Build Executable with PyInstaller

1. **Run Build Script** (recommended)

   ```cmd
   build_windows.bat
   ```

   OR

2. **Build Manually**

   ```cmd
   REM Clean previous builds
   rmdir /s /q build
   rmdir /s /q dist

   REM Run PyInstaller
   pyinstaller agentic_bookkeeper.spec --clean
   ```

3. **Verify Build Output**
   - Location: `dist\AgenticBookkeeper\`
   - Main executable: `dist\AgenticBookkeeper\AgenticBookkeeper.exe`
   - Supporting files: DLLs, Python libraries, PySide6 plugins

4. **Test Executable**

   ```cmd
   dist\AgenticBookkeeper\AgenticBookkeeper.exe
   ```

   **Expected behavior:**
   - Application window opens
   - No console window appears (windowed mode)
   - First-run setup wizard displays
   - All GUI features work

### Step 3: Build Installer with NSIS

1. **Navigate to Installer Directory**

   ```cmd
   cd installer
   ```

2. **Run Installer Build Script** (recommended)

   ```cmd
   build_installer.bat
   ```

   OR

3. **Build Manually**

   ```cmd
   makensis windows_installer.nsi
   ```

4. **Verify Installer Output**
   - Location: `dist\AgenticBookkeeper-0.1.0-Setup.exe`
   - Size: Approximately 80-100 MB (compressed)

### Step 4: Test Installation

**IMPORTANT:** Test on a clean Windows 10/11 system or virtual machine.

1. **Copy Installer to Test System**
   - Copy `dist\AgenticBookkeeper-0.1.0-Setup.exe`
   - Transfer via USB, network share, or cloud storage

2. **Run Installer**
   - Double-click `AgenticBookkeeper-0.1.0-Setup.exe`
   - Accept UAC prompt (requires admin)
   - Follow installation wizard

3. **Verify Installation**
   - Start Menu shortcut created: `Agentic Bookkeeper`
   - Desktop shortcut created: `Agentic Bookkeeper`
   - Program Files location: `C:\Program Files\Agentic Bookkeeper`

4. **Test Application**
   - Launch from Start Menu
   - Complete first-run setup
   - Test all features:
     - Document processing (upload PDF/image)
     - Transaction management (add, edit, delete)
     - Report generation (income statement, expense report)
     - Settings configuration (API keys, directories)
   - Check logs: `C:\Program Files\Agentic Bookkeeper\logs`

5. **Test Uninstaller**
   - Control Panel → Programs → Uninstall
   - Choose whether to keep data
   - Verify complete removal

---

## Troubleshooting

### Build Issues

#### PyInstaller Build Fails

**Symptom:** `pyinstaller` command fails with import errors

**Solutions:**

1. Ensure all dependencies are installed:

   ```cmd
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. Check for hidden imports in `agentic_bookkeeper.spec`
   - Add missing modules to `hiddenimports` list

3. Clear cache and rebuild:

   ```cmd
   pyinstaller --clean agentic_bookkeeper.spec
   ```

#### Executable Won't Run

**Symptom:** Double-clicking `AgenticBookkeeper.exe` does nothing

**Solutions:**

1. Run from command line to see errors:

   ```cmd
   dist\AgenticBookkeeper\AgenticBookkeeper.exe
   ```

2. Check Windows Event Viewer for errors:
   - Event Viewer → Windows Logs → Application

3. Test with console mode:
   - Edit `agentic_bookkeeper.spec`
   - Change `console=False` to `console=True`
   - Rebuild

#### Missing DLLs

**Symptom:** Error message about missing DLL files

**Solutions:**

1. Install Visual C++ Redistributable:
   - Download: https://aka.ms/vs/17/release/vc_redist.x64.exe

2. Add DLLs to PyInstaller:
   - Edit `agentic_bookkeeper.spec`
   - Add to `binaries` list:

     ```python
     binaries=[('path/to/missing.dll', '.')],
     ```

#### Large Executable Size

**Symptom:** Executable is larger than 100 MB

**Solutions:**

1. Check excluded modules in `agentic_bookkeeper.spec`:

   ```python
   excludes=['tkinter', 'matplotlib', 'IPython', 'jupyter']
   ```

2. Enable UPX compression:
   - Download UPX: https://upx.github.io/
   - Add to PATH
   - PyInstaller will use automatically

### Installer Issues

#### NSIS Not Found

**Symptom:** `makensis` command not recognized

**Solutions:**

1. Install NSIS from https://nsis.sourceforge.io/
2. Add to PATH: `C:\Program Files (x86)\NSIS`
3. Restart command prompt

#### Installer Build Fails

**Symptom:** NSIS compilation errors

**Solutions:**

1. Verify executable exists:

   ```cmd
   dir dist\AgenticBookkeeper\AgenticBookkeeper.exe
   ```

2. Check LICENSE file exists:

   ```cmd
   dir LICENSE
   ```

3. Review NSIS log output for missing files

#### Installation Fails

**Symptom:** Installer shows error during installation

**Solutions:**

1. Run installer as Administrator
2. Disable antivirus temporarily
3. Check disk space (requires 200+ MB)
4. Close all other applications

### Runtime Issues

#### Application Won't Start After Installation

**Symptom:** Installed application fails to launch

**Solutions:**

1. Check event logs:
   - Event Viewer → Windows Logs → Application

2. Verify all files installed:

   ```cmd
   dir "C:\Program Files\Agentic Bookkeeper"
   ```

3. Run from command line:

   ```cmd
   cd "C:\Program Files\Agentic Bookkeeper"
   AgenticBookkeeper.exe
   ```

4. Check for missing Visual C++ Redistributable

#### Features Don't Work

**Symptom:** Application starts but features fail

**Solutions:**

1. Check `.env` configuration:
   - Location: `C:\Users\<username>\.agentic_bookkeeper\.env`
   - Verify API keys are set

2. Check permissions:
   - Watch folder: Read/Write access
   - Data folder: Read/Write access
   - Log folder: Write access

3. Review log files:
   - Location: `C:\Program Files\Agentic Bookkeeper\logs`
   - Check for error messages

---

## Advanced Topics

### Code Signing (Optional)

**Benefits:**

- Removes "Unknown Publisher" warning
- Increases user trust
- Required for some enterprise deployments

**Requirements:**

- Code signing certificate (from CA like DigiCert, Sectigo)
- SignTool.exe (included with Windows SDK)

**Process:**

1. Obtain code signing certificate
2. Install certificate to Windows certificate store
3. Sign executable:

   ```cmd
   signtool sign /a /t http://timestamp.digicert.com /fd SHA256 "dist\AgenticBookkeeper\AgenticBookkeeper.exe"
   ```

4. Sign installer:

   ```cmd
   signtool sign /a /t http://timestamp.digicert.com /fd SHA256 "dist\AgenticBookkeeper-0.1.0-Setup.exe"
   ```

### Custom Icon

**Adding an Application Icon:**

1. Create/obtain `.ico` file (256x256, 48x48, 32x32, 16x16)
2. Save as `resources/icon.ico`
3. Edit `agentic_bookkeeper.spec`:

   ```python
   icon='resources/icon.ico'
   ```

4. Edit `installer/windows_installer.nsi`:

   ```text
   !define MUI_ICON "resources\icon.ico"
   ```

5. Rebuild

### Automated Build Pipeline

**GitHub Actions Example:**

```yaml
name: Build Windows Executable

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller
      - name: Build executable
        run: pyinstaller agentic_bookkeeper.spec
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: windows-executable
          path: dist/AgenticBookkeeper/
```text

### Multi-Version Support

**Building for Different Python Versions:**

```cmd
REM Python 3.8
py -3.8 -m venv venv38
venv38\Scripts\activate
pip install -r requirements.txt
pyinstaller agentic_bookkeeper.spec --distpath dist38

REM Python 3.11
py -3.11 -m venv venv311
venv311\Scripts\activate
pip install -r requirements.txt
pyinstaller agentic_bookkeeper.spec --distpath dist311
```text

---

## Testing Checklist

### Pre-Build Testing

- [ ] All unit tests pass: `pytest`
- [ ] Application runs from source: `python src/agentic_bookkeeper/main.py`
- [ ] All dependencies in requirements.txt
- [ ] Version number updated in spec file

### Post-Build Testing

- [ ] Executable runs without console window
- [ ] All GUI elements render correctly
- [ ] First-run setup wizard works
- [ ] Settings dialog opens and saves
- [ ] Document processing works
- [ ] Transaction CRUD operations work
- [ ] Report generation works (all formats)
- [ ] Export functions work (PDF, CSV, JSON)
- [ ] Application logs are created
- [ ] Database is created and accessible

### Installation Testing

- [ ] Installer runs without errors
- [ ] Start Menu shortcuts created
- [ ] Desktop shortcut created
- [ ] Application launches from shortcuts
- [ ] Configuration directory created
- [ ] Data directory created
- [ ] Logs directory created
- [ ] Uninstaller is registered

### Clean System Testing

- [ ] Test on Windows 10 (version 21H2+)
- [ ] Test on Windows 11
- [ ] Test with no Python installed
- [ ] Test with antivirus enabled
- [ ] Test installation to non-default location
- [ ] Test installation as non-admin user
- [ ] Test uninstallation (keep data)
- [ ] Test uninstallation (delete data)

---

## File Size Expectations

| Component | Expected Size | Notes |
|-----------|---------------|-------|
| Source Code | ~5 MB | Python files only |
| Virtual Environment | ~500 MB | With all dependencies |
| Build Directory | ~300 MB | Temporary PyInstaller files |
| Dist Directory | ~200 MB | Uncompressed executable + libs |
| Final Executable | ~150 MB | AgenticBookkeeper.exe + DLLs |
| Installer (NSIS) | ~80-100 MB | Compressed installer |

**Size Reduction Tips:**

1. Enable UPX compression in PyInstaller
2. Exclude unused modules in spec file
3. Remove test files from distribution
4. Use NSIS solid compression

---

## Distribution Checklist

Before releasing to users:

- [ ] Code signed (optional but recommended)
- [ ] Tested on clean Windows 10 VM
- [ ] Tested on clean Windows 11 VM
- [ ] User Guide included
- [ ] LICENSE file included
- [ ] README.txt included
- [ ] Sample configuration (.env.sample) included
- [ ] Version number correct in all files
- [ ] GitHub release created with installer
- [ ] SHA256 checksum published
- [ ] Release notes written

---

## Support and Resources

### Documentation

- User Guide: `docs/USER_GUIDE.md`
- Developer Guide: `docs/DEVELOPMENT.md`
- Architecture: `docs/ARCHITECTURE.md`

### External Resources

- PyInstaller Documentation: https://pyinstaller.org/en/stable/
- NSIS Documentation: https://nsis.sourceforge.io/Docs/
- Windows Code Signing: https://learn.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools

### Common Commands

```cmd
REM Build executable
build_windows.bat

REM Build installer
cd installer && build_installer.bat

REM Clean build artifacts
rmdir /s /q build dist

REM Test executable
dist\AgenticBookkeeper\AgenticBookkeeper.exe

REM Check dependencies
pip list

REM Update dependencies
pip install --upgrade -r requirements.txt
```text

---

## Appendix A: PyInstaller Spec File Reference

Key sections in `agentic_bookkeeper.spec`:

```python
# Entry point
[str(src_dir / 'agentic_bookkeeper' / 'main.py')]

# Hidden imports (dynamic imports)
hiddenimports=[
    'agentic_bookkeeper.core',
    # ... all submodules
]

# Data files (non-Python resources)
datas=pyside6_datas

# Excluded modules (reduce size)
excludes=['tkinter', 'matplotlib']

# Executable configuration
console=False  # No console window
name='AgenticBookkeeper'  # Output name
```text

---

## Appendix B: NSIS Installer Reference

Key sections in `installer/windows_installer.nsi`:

```nsis
; Product information
!define PRODUCT_NAME "Agentic Bookkeeper"
!define PRODUCT_VERSION "0.1.0"

; Installation directory
InstallDir "$PROGRAMFILES64\${PRODUCT_NAME}"

; Shortcuts
CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${PRODUCT_NAME}.lnk"

; Registry keys
WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" ""
```text

---

## Changelog

### Version 0.1.0 (2025-10-29)

- Initial Windows build documentation
- PyInstaller configuration
- NSIS installer script
- Automated build scripts
- Comprehensive troubleshooting guide

---

**End of BUILD_WINDOWS.md**
