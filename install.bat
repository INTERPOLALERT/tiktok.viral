@echo off
echo ============================================================
echo FUND.TIRES - Installation Script for Windows 11
echo ============================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

:: Check if pip is available
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    pause
    exit /b 1
)

echo Installing required packages...
echo.

:: Install requirements
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Installation completed successfully!
echo ============================================================
echo.
echo Next steps:
echo 1. Run: run.bat
echo 2. Open your browser to: http://127.0.0.1:5000
echo.
pause
