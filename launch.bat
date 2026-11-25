@echo off
cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Install from: https://www.python.org/
    pause
    exit /b 1
)

REM Launch branded launcher
pythonw DeathAIAUS_Launcher.py
