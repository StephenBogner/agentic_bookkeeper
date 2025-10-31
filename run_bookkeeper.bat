@echo off
REM Agentic Bookkeeper Launcher Script (Windows)
REM This script starts the Agentic Bookkeeper application

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ========================================
echo   Agentic Bookkeeper Launcher
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run the installation script first:
    echo   install.bat
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if agentic_bookkeeper is installed
python -c "import agentic_bookkeeper" 2>nul
if errorlevel 1 (
    echo [ERROR] Agentic Bookkeeper package not installed!
    echo.
    echo Please run the installation script:
    echo   install.bat
    echo.
    pause
    exit /b 1
)

REM Check for .env file
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo The application will start, but you'll need to configure API keys.
    echo See docs\user\ENV_SETUP_GUIDE.md for details.
    echo.
)

REM Display startup information
echo Starting Agentic Bookkeeper...
echo.
echo Application Mode: GUI
for /f "delims=" %%V in ('python --version 2^>^&1') do set PYTHON_VERSION=%%V
echo Python Version: !PYTHON_VERSION!
echo Working Directory: %SCRIPT_DIR%
echo.
echo Press Ctrl+C to stop the application
echo.
echo ========================================
echo.

REM Start the application
python src\agentic_bookkeeper\main.py

REM Cleanup message
echo.
echo Application closed successfully.
echo.
pause
