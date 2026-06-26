@echo off
title Auto Typer Pro Setup Installer
echo ===================================================
echo Auto Typer Pro - Installation and Setup Tool
echo ===================================================

cd /d "%~dp0"

:: 1. Verify Python Installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in system PATH.
    echo Please install Python 3.11+ and check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: 2. Create Virtual Environment
if not exist venv (
    echo [INFO] Creating Python virtual environment (venv)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [INFO] Existing virtual environment found.
)

:: 3. Activate Virtual Environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate

:: 4. Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

:: 5. Install Dependencies
echo [INFO] Installing required packages from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
)

:: 6. Generate Assets
echo [INFO] Generating graphic assets...
python generate_icon.py

:: 7. Run Codebase Integrity Check
echo [INFO] Running application modules integrity check...
python verify_integrity.py
if %errorlevel% neq 0 (
    echo [WARNING] Some codebase integration checks failed. Please check log files.
)

:: 8. Run Automated Test Suite
echo [INFO] Running test suite...
python test_suite.py
if %errorlevel% neq 0 (
    echo [WARNING] Test suite failures detected.
)

echo ===================================================
echo [SUCCESS] Auto Typer Pro installation completed!
echo To run the application, execute: run.bat
echo To build standalone binary, execute: build.bat
echo ===================================================
pause
