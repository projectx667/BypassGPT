@echo off
cls

echo ========================================
echo     BypassGPT v1 - Setup ^& Launch
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Install from: https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python %PYTHON_VERSION% detected
echo.

if not exist requirements.txt (
    echo ERROR: requirements.txt not found
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt --quiet --upgrade

if errorlevel 1 (
    echo ERROR: Installation failed
    echo Try manually: pip install -r requirements.txt
    pause
    exit /b 1
)

echo Dependencies installed
echo.

if not exist main.py (
    echo ERROR: main.py not found
    pause
    exit /b 1
)

echo ========================================
echo        Installation Complete
echo ========================================
echo.
echo Launching BypassGPT...
echo.
timeout /t 1 /nobreak >nul

python main.py

pause
