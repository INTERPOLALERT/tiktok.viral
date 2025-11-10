@echo off
echo ============================================================
echo FUND.TIRES - Starting Server
echo ============================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please run install.bat first
    pause
    exit /b 1
)

:: Check if dependencies are installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Flask is not installed
    echo Please run install.bat first
    pause
    exit /b 1
)

echo Starting Fund.tires server...
echo.
echo The application will be available at:
echo http://127.0.0.1:5000
echo.
echo Press CTRL+C to stop the server
echo ============================================================
echo.

:: Run the Flask app
python app.py

pause
