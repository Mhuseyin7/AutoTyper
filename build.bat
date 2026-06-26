@echo off
title Auto Typer Pro - Premium Build Tool
echo ===================================================
echo Auto Typer Pro - Standalone Compiler Script
echo ===================================================

:: Ensure we are running from project root
cd /d "%~dp0"

:: Detect virtual environment
if exist venv\Scripts\activate.bat (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo [WARNING] No venv folder detected. Compiling using global Python environment.
)

:: Check for PyInstaller
python -c "import pyinstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] PyInstaller is not installed. Downloading now...
    pip install pyinstaller
)

:: Make sure app icon is generated
if not exist app\assets\app.ico (
    echo [INFO] Assets icon not found. Running icon generator...
    python generate_icon.py
)

echo [INFO] Compiling Standalone Single-File Executable...
pyinstaller --clean --noconfirm --onefile --windowed --name "AutoTyperPro" --icon "app/assets/app.ico" --add-data "app/assets;app/assets" run.py

echo [INFO] Compiling Complete Directory Folder Package...
pyinstaller --clean --noconfirm --onedir --windowed --name "AutoTyperProPackage" --icon "app/assets/app.ico" --add-data "app/assets;app/assets" run.py

echo ===================================================
echo [SUCCESS] Package compilation completed successfully.
echo Output executables are located inside the 'dist/' folder:
echo  - Standalone: dist/AutoTyperPro.exe
echo  - Folder Package: dist/AutoTyperProPackage/AutoTyperProPackage.exe
echo ===================================================
pause
