@echo off
REM Push to New GitHub Repository
REM CreatorStudio AI Transfer Script

echo ==========================================
echo Pushing CreatorStudio AI to New GitHub
echo ==========================================
echo.
echo Repository: https://github.com/Expansion3D/tiktok.viral.369
echo Branch: claude/work-in-progress-011CUyEsPRwmJL1Ggb3tKuFK
echo.

echo METHOD: Using Personal Access Token
echo ------------------------------------
echo 1. Get your token from: https://github.com/settings/tokens
echo    - Click "Generate new token (classic)"
echo    - Check "repo" permissions
echo    - Copy the token
echo.
echo 2. Run this command (replace YOUR_TOKEN with your actual token):
echo.
echo git push https://YOUR_TOKEN@github.com/Expansion3D/tiktok.viral.369.git claude/work-in-progress-011CUyEsPRwmJL1Ggb3tKuFK
echo.
echo ==========================================
echo After successful push:
echo 1. Visit: https://github.com/Expansion3D/tiktok.viral.369
echo 2. You'll see your branch there
echo 3. Create a Pull Request if needed
echo ==========================================
echo.

set /p token="Paste your GitHub token here and press Enter (or Ctrl+C to exit): "

if "%token%"=="" (
    echo ERROR: No token provided
    pause
    exit /b 1
)

echo.
echo Pushing to GitHub...
git push https://%token%@github.com/Expansion3D/tiktok.viral.369.git claude/work-in-progress-011CUyEsPRwmJL1Ggb3tKuFK

if errorlevel 1 (
    echo.
    echo ERROR: Push failed!
    echo Please check your token and try again
    pause
    exit /b 1
)

echo.
echo ==========================================
echo SUCCESS! Your code is now on GitHub!
echo ==========================================
echo.
echo View it at: https://github.com/Expansion3D/tiktok.viral.369
echo.
pause
