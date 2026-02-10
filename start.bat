@echo off
setlocal enabledelayedexpansion

echo ========================================
echo     Ad Audit AI One-Click Launcher
echo     (Portable, using Embedded Python)
echo ========================================
echo.

:: Get script directory
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

:: Check embedded Python
if not exist "python-3.13-embed\python.exe" (
    echo Error: Embedded Python directory not found
    echo Please ensure python-3.13-embed directory exists
    pause
    exit /b 1
)

:: Set Python command
set "PYTHON_CMD=python-3.13-embed\python.exe"

:: Check virtual environment
if not exist "venv\Scripts\python.exe" (
    echo Virtual environment not found, creating...
    "%PYTHON_CMD%" -m virtualenv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

:: Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo Installing dependencies...
    pip install -r requirements.txt --disable-pip-version-check --default-timeout=1000 -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo Warning: Dependency installation failed, trying to continue...
    )
)

:: Set Playwright browsers path to local directory (for offline installation)
set "PLAYWRIGHT_BROWSERS_PATH=%PROJECT_DIR%browsers"
:: Check multiple possible browser paths
if exist "%PLAYWRIGHT_BROWSERS_PATH%\chromium-1208\chrome-win\chrome.exe" (
    echo Found offline Chromium browser installation (chrome-win)
) else if exist "%PLAYWRIGHT_BROWSERS_PATH%\chromium-1208\chrome-win64\chrome.exe" (
    echo Found offline Chromium browser installation (chrome-win64)
) else if exist "%PLAYWRIGHT_BROWSERS_PATH%\chrome-win\chrome.exe" (
    echo Found offline Chromium browser installation (root chrome-win)
) else if exist "%PLAYWRIGHT_BROWSERS_PATH%\chrome-win64\chrome.exe" (
    echo Found offline Chromium browser installation (root chrome-win64)
) else (
    echo No offline browser found, will use system browser or download
    :: Even if no local browser, set path so Playwright will install browser in this directory
    set "PLAYWRIGHT_BROWSERS_PATH=%PROJECT_DIR%browsers"
)

:: Check and install Playwright browser if needed using Python script
echo Checking Playwright browser installation...
python check_playwright.py
if errorlevel 1 (
    echo Warning: Playwright browser check script failed
    echo Session capture functionality may not be available
)

:skip_playwright

echo.
echo Starting Ad Audit AI application...
echo Please open your browser and visit:
echo http://localhost:8000
echo.
echo Press Ctrl+C to stop the service
echo.

:: Start the application
python -m src.update.launcher %*

if errorlevel 1 (
    echo.
    echo Application exited abnormally, please check error messages
    pause
) else (
    echo.
    echo Application stopped normally
    pause
)