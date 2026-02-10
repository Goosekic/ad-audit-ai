@echo off
setlocal enabledelayedexpansion

echo ========================================
echo     Ad Audit AI Restart Script
echo ========================================
echo.

echo Terminating Python processes...
taskkill /F /IM python.exe 2>nul
if errorlevel 1 (
    echo No Python processes found
) else (
    echo Python processes terminated
)

echo.
echo Waiting 3 seconds for cleanup...
timeout /t 3 /nobreak >nul

echo.
echo Cleaning Python cache...
del /s /q src\whisper_service\__pycache__ 2>nul
del /s /q src\whisper_service\*.pyc 2>nul
del /s /q __pycache__ 2>nul
del /s /q *.pyc 2>nul

echo.
echo Restarting Ad Audit AI...
echo.

:: Start main launcher
start.bat