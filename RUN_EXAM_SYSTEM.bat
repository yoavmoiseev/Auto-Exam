@echo off
REM Start Exam System Flask Application
REM Windows batch file to run the web application

echo.
echo ======================================
echo Exam System - Flask Web Application
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

REM Install requirements if needed
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install Flask if not already installed
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing Flask...
    pip install Flask==3.0.0 Werkzeug==3.0.1
)

REM Run the application
echo.
echo Starting application on http://localhost:5000
echo Press Ctrl+C to stop
echo.

python app.py

REM If application crashes or exits, show message
echo.
echo Application stopped
pause
