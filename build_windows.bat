@echo off
REM Build script for Agentic Bookkeeper Windows executable
REM Author: Stephen Bogner
REM Created: 2025-10-29

echo ========================================
echo Agentic Bookkeeper - Windows Build
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [1/6] Checking virtual environment...
if not exist "venv\" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo [3/6] Installing/upgrading dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller>=6.0.0

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/6] Cleaning previous build artifacts...
if exist "build\" rmdir /s /q build
if exist "dist\" rmdir /s /q dist
if exist "*.spec.bak" del /q *.spec.bak

echo [5/6] Building executable with PyInstaller...
pyinstaller agentic_bookkeeper.spec --clean

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo ERROR: PyInstaller build failed
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo Common issues:
    echo   - Missing dependencies in requirements.txt
    echo   - Import errors in Python code
    echo   - Insufficient disk space
    echo.
    pause
    exit /b 1
)

echo [6/6] Creating distribution folder structure...
if not exist "dist\AgenticBookkeeper\config" mkdir "dist\AgenticBookkeeper\config"
if not exist "dist\AgenticBookkeeper\data" mkdir "dist\AgenticBookkeeper\data"
if not exist "dist\AgenticBookkeeper\logs" mkdir "dist\AgenticBookkeeper\logs"

REM Copy configuration template
if exist "samples\config\.env.sample" (
    copy "samples\config\.env.sample" "dist\AgenticBookkeeper\config\.env.sample"
)

REM Copy documentation
if exist "docs\USER_GUIDE.md" (
    copy "docs\USER_GUIDE.md" "dist\AgenticBookkeeper\USER_GUIDE.md"
)

REM Create README for distribution
echo Agentic Bookkeeper - Windows Distribution > "dist\AgenticBookkeeper\README.txt"
echo. >> "dist\AgenticBookkeeper\README.txt"
echo Thank you for using Agentic Bookkeeper! >> "dist\AgenticBookkeeper\README.txt"
echo. >> "dist\AgenticBookkeeper\README.txt"
echo To run the application: >> "dist\AgenticBookkeeper\README.txt"
echo   1. Double-click AgenticBookkeeper.exe >> "dist\AgenticBookkeeper\README.txt"
echo   2. Follow the first-time setup wizard >> "dist\AgenticBookkeeper\README.txt"
echo. >> "dist\AgenticBookkeeper\README.txt"
echo For detailed documentation, see USER_GUIDE.md >> "dist\AgenticBookkeeper\README.txt"
echo. >> "dist\AgenticBookkeeper\README.txt"
echo Support: https://github.com/yourusername/agentic_bookkeeper >> "dist\AgenticBookkeeper\README.txt"

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Output location: dist\AgenticBookkeeper\
echo Executable: dist\AgenticBookkeeper\AgenticBookkeeper.exe
echo.
echo Size information:
dir "dist\AgenticBookkeeper" | find "AgenticBookkeeper.exe"
echo.
echo Next steps:
echo   1. Test the executable: dist\AgenticBookkeeper\AgenticBookkeeper.exe
echo   2. Build installer: Run installer\build_installer.bat
echo   3. Test installation on clean Windows 10/11 system
echo.

pause
