@echo off
echo ================================================================
echo   AI Lab Manager - Virtual Environment Setup
echo ================================================================
echo.

:: Change to parent directory (ai-lab folder)
cd /d "%~dp0.."

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

:: Check Python version
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.10 or higher is required
    echo.
    python --version
    echo.
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
    
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo.
        echo Make sure you have Python's venv module installed.
        echo On some systems you may need to install it:
        echo   - Ubuntu/Debian: sudo apt install python3-venv
        echo   - Windows: Usually included with Python
        echo.
        pause
        exit /b 1
    )
    
    echo Virtual environment created successfully!
    echo.
) else (
    echo Virtual environment already exists.
    echo.
)

:: Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
if exist "requirements.txt" (
    echo.
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    echo.
) else (
    echo WARNING: requirements.txt not found
    echo Installing basic dependencies...
    pip install ttkbootstrap psutil
    echo.
)

echo ================================================================
echo   Setup Complete!
echo ================================================================
echo.
echo Virtual environment is ready to use!
echo.
echo To activate the virtual environment manually:
echo   venv\Scripts\activate
echo.
echo To deactivate:
echo   deactivate
echo.
echo To run AI Lab Manager:
echo   scripts\start_manager_venv.bat
echo.
pause
