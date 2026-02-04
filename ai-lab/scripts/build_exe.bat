@echo off
echo ================================================================
echo   Building AI-Lab Manager Executable
echo ================================================================
echo.

:: Change to parent directory
cd /d "%~dp0.."

:: Check if we should use venv or global Python
set USE_VENV=0
if exist "venv\Scripts\activate.bat" (
    echo Virtual environment detected!
    echo.
    choice /C YN /M "Build using virtual environment"
    if errorlevel 2 (
        echo Using global Python installation...
    ) else (
        echo Activating virtual environment...
        call venv\Scripts\activate.bat
        set USE_VENV=1
    )
    echo.
)

:: Check if pyinstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    echo.
)

:: Build the executable
echo Building executable...
pyinstaller --onefile --windowed --icon=NONE --name="AILab_Manager" ailab_manager.py

echo.
echo ================================================================
echo   Build Complete!
echo ================================================================
echo.
echo Executable location: dist\AILab_Manager.exe
echo.
echo You can now:
echo   1. Run dist\AILab_Manager.exe directly
echo   2. Create a shortcut to this exe file
echo   3. Move it anywhere you want
echo.
pause
