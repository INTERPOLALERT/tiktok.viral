@echo off
echo ================================================================================
echo CreatorStudio AI - Installation Script
echo ================================================================================
echo.
echo This script will install all required dependencies for CreatorStudio AI
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.9 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Checking Python version...
python --version
echo.

echo Upgrading pip to latest version...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Could not upgrade pip, but continuing...
)
echo.

echo ================================================================================
echo Installing CreatorStudio AI dependencies...
echo This may take several minutes depending on your internet connection
echo ================================================================================
echo.

REM Install requirements
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo.
    echo Please check your internet connection and try again.
    echo If the problem persists, try installing dependencies manually:
    echo    python -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Installation Complete!
echo ================================================================================
echo.
echo All dependencies have been successfully installed.
echo.
echo Next steps:
echo   1. Configure your API keys (optional but recommended):
echo      - Run the application: START.BAT
echo      - Go to Settings tab
echo      - Enter your OpenAI API key
echo.
echo   2. Start creating content!
echo.
echo To run CreatorStudio AI, simply double-click START.BAT
echo or run: python main.py
echo.
echo ================================================================================
echo.
pause
