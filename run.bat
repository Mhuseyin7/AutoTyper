@echo off
title Auto Typer Pro Launcher
echo ===================================================
echo Auto Typer Pro Launcher
echo ===================================================

cd /d "%~dp0"

:: Detect virtual environment
if exist venv\Scripts\activate.bat (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate
)

echo [INFO] Starting Auto Typer Pro...
python run.py

if %errorlevel% neq 0 (
    echo [ERROR] Application closed with exit code %errorlevel%.
    pause
)
