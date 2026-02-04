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

:: Check if all dependencies are installed
echo Checking dependencies...
pip install -r requirements.txt --quiet
echo.

:: Build the executable with all dependencies embedded
echo Building self-contained executable...
echo This may take a few minutes...
echo.
pyinstaller AILab_Manager.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   Build Complete!
echo ================================================================
echo.
echo Executable location: dist\AILab_Manager.exe
echo.
echo The executable is SELF-CONTAINED and includes:
echo   - Python runtime
echo   - tkinter GUI framework
echo   - ttkbootstrap themes
echo   - psutil library
echo   - All necessary dependencies
echo.
echo You can now:
echo   1. Run dist\AILab_Manager.exe directly (no Python needed!)
echo   2. Distribute this single file to any Windows machine
echo   3. Create shortcuts anywhere you want
echo.
if %USE_VENV%==1 (
    echo Note: Virtual environment was used for building.
    echo The exe is still fully standalone.
    echo.
)
pause
