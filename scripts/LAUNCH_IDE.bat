@echo off
REM ========================================
REM DeathAIAUS IDE F.C - ONE-CLICK LAUNCHER
REM ========================================

REM Change to IDE directory
cd /d "%~dp0"

REM Launch IDE silently (no console window)
start "" pythonw deathaius_ide_fc.py 2>nul

REM If pythonw doesn't exist, use regular python
if errorlevel 1 (
    start "" python deathaius_ide_fc.py
)

REM Exit immediately (window closes)
exit
