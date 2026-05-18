@echo off
REM ── SnapAI — Upload AI Models to GitHub (Run Once) ──────────────────────
REM Double-click this file to upload the large YOLO model files to GitHub.
REM After this runs once, Railway will download them automatically on deploy.

echo.
echo ============================================================
echo   SnapAI — Uploading AI Models to GitHub Releases
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Install requests if needed
pip install requests >nul 2>&1

REM Run the upload script
cd /d "%~dp0"
python scripts\upload_models_github.py

echo.
IF ERRORLEVEL 1 (
    echo ============================================================
    echo   UPLOAD FAILED - See error above
    echo ============================================================
) ELSE (
    echo ============================================================
    echo   DONE! Models are now on GitHub.
    echo   Push your code to GitHub - Railway will auto-deploy.
    echo ============================================================
)

pause
