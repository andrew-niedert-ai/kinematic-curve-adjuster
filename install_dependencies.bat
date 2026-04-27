@echo off
echo ========================================
echo Installing Required Python Libraries
echo ========================================
echo.
echo This will install the following packages:
echo - numpy (numerical computing)
echo - matplotlib (plotting and visualization)
echo - scikit-learn (machine learning utilities)
echo - pyperclip (clipboard operations)
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
echo.

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing required packages...
python -m pip install -r requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! All dependencies installed.
    echo ========================================
    echo.
    echo You can now run the application using:
    echo   python curve_adjuster.py
    echo.
    echo Or simply double-click: run_curve_adjuster.bat
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR: Installation failed!
    echo ========================================
    echo.
    echo Please try running this command manually:
    echo   pip install numpy matplotlib scikit-learn pyperclip
    echo.
)

pause

