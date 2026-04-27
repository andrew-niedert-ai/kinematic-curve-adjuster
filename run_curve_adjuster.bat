@echo off
echo Starting Kinematic Curve Adjuster...
echo.
python curve_adjuster.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to run the application.
    echo Please make sure Python is installed and dependencies are installed.
    echo Run: pip install -r requirements.txt
    pause
)

