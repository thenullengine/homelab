@echo off
title AI-Lab Manager Launcher

echo ============================================
echo   AI-Lab Manager
echo ============================================
echo.
echo Starting unified AI manager...
echo.

:: Change to parent directory
cd /d "%~dp0.."

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

:: Check if required packages are installed
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install --upgrade pip
)

:: Run the GUI
python ailab_manager.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start the manager
    echo.
    pause
)
