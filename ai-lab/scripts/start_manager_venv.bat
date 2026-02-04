@echo off
title AI-Lab Manager (Virtual Environment)

echo ============================================
echo   AI-Lab Manager
echo ============================================
echo.

:: Change to parent directory
cd /d "%~dp0.."

:: Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo.
    echo Please run setup_venv.bat first to create the virtual environment.
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Check if activation was successful
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo.
    pause
    exit /b 1
)

echo Starting AI Lab Manager from virtual environment...
echo.

:: Run the GUI
python ailab_manager.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start the manager
    echo.
    pause
)

:: Deactivate is automatic when script ends
