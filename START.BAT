@echo off
echo ================================================================================
echo CreatorStudio AI - Professional Content Creation Suite
echo Version 1.0.0
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.9 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    echo After installing Python, run INSTALL.BAT to install dependencies
    echo.
    pause
    exit /b 1
)

REM Check if requirements are installed by trying to import PyQt6
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Dependencies not installed!
    echo.
    echo It looks like the required dependencies are not installed yet.
    echo Please run INSTALL.BAT first to install all dependencies.
    echo.
    set /p choice="Do you want to run INSTALL.BAT now? (Y/N): "
    if /i "%choice%"=="Y" (
        call INSTALL.BAT
        if errorlevel 1 (
            echo.
            echo Installation failed. Please fix the errors and try again.
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo Please run INSTALL.BAT before starting the application.
        pause
        exit /b 1
    )
)

echo Starting CreatorStudio AI...
echo.
echo ================================================================================
echo AI-Powered Tools Available:
echo   - Video Generation and Editing
echo   - Image Creation and Manipulation
echo   - Script Writing and Optimization
echo   - Voice Synthesis and Audio Processing
echo   - Social Media Management and Scheduling
echo   - Advanced Analytics and Insights
echo   - Real-Time Trend Analysis
echo   - Project Management and Workflows
echo ================================================================================
echo.
echo Launching application...
echo.

REM Run the application
python main.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo ================================================================================
    echo ERROR: Application exited with an error
    echo ================================================================================
    echo.
    echo Please check the error messages above for details.
    echo Log files are available in the 'logs' folder.
    echo.
    echo Common issues:
    echo   1. Missing dependencies - Run INSTALL.BAT
    echo   2. API key not configured - Configure in Settings tab
    echo   3. Python version too old - Requires Python 3.9+
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo CreatorStudio AI has been closed
echo ================================================================================
echo.
echo Thank you for using CreatorStudio AI!
echo.
pause
