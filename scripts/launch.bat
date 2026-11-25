@echo off
cls
color 0A
echo.
echo  ================================================
echo   DeathAIAUS IDE F.C - AI-Powered
echo   Version 3.0 - Full Consolidation Edition
echo  ================================================
echo.
echo   [*] Checking Python...
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [ERROR] Python not found!
    echo.
    echo  Please install Python from: https://www.python.org/
    echo  Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo   [*] Launching IDE...
echo.

REM Try pythonw first (no console window)
start "" pythonw deathaius_ide_fc.py
timeout /t 1 >nul

REM Check if it started, if not try regular python
tasklist /FI "IMAGENAME eq pythonw.exe" 2>nul | find "pythonw.exe" >nul
if errorlevel 1 (
    REM If pythonw fails, use regular python
    start "" python deathaius_ide_fc.py
)

REM Success - close after 1 second
timeout /t 1 >nul
exit
