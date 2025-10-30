@echo off
REM Build NSIS installer for Agentic Bookkeeper
REM Author: Stephen Bogner
REM Created: 2025-10-29

echo ========================================
echo Agentic Bookkeeper - Installer Build
echo ========================================
echo.

REM Check if NSIS is installed
where makensis >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: NSIS (Nullsoft Scriptable Install System) is not installed or not in PATH
    echo.
    echo Please download and install NSIS from:
    echo https://nsis.sourceforge.io/Download
    echo.
    echo After installation, add NSIS to your PATH:
    echo   Typical location: C:\Program Files (x86)\NSIS
    echo.
    pause
    exit /b 1
)

echo [1/4] Checking if executable exists...
if not exist "..\dist\AgenticBookkeeper\AgenticBookkeeper.exe" (
    echo ERROR: Executable not found
    echo.
    echo Please build the executable first by running:
    echo   build_windows.bat
    echo.
    pause
    exit /b 1
)

echo [2/4] Checking if LICENSE file exists...
if not exist "..\LICENSE" (
    echo WARNING: LICENSE file not found
    echo Creating placeholder LICENSE file...
    echo Copyright (C) 2025 Stephen Bogner > "..\LICENSE"
    echo All Rights Reserved >> "..\LICENSE"
)

echo [3/4] Building installer with NSIS...
makensis windows_installer.nsi

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo ERROR: NSIS installer build failed
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo Common issues:
    echo   - Missing files referenced in NSI script
    echo   - Syntax errors in NSI script
    echo   - Insufficient permissions
    echo.
    pause
    exit /b 1
)

echo [4/4] Verifying installer...
if exist "..\dist\AgenticBookkeeper-0.1.0-Setup.exe" (
    echo.
    echo ========================================
    echo Installer built successfully!
    echo ========================================
    echo.
    echo Output: dist\AgenticBookkeeper-0.1.0-Setup.exe
    echo.
    echo Size information:
    dir "..\dist\AgenticBookkeeper-0.1.0-Setup.exe" | find "AgenticBookkeeper"
    echo.
    echo Next steps:
    echo   1. Test installer on clean Windows 10/11 VM
    echo   2. Verify all features work after installation
    echo   3. Test uninstaller
    echo   4. Consider code signing for production release
    echo.
) else (
    echo ERROR: Installer file not created
    pause
    exit /b 1
)

pause
