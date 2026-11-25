@echo off
echo ============================================
echo  Starting ReapGate - Death's Inference Engine
echo ============================================
echo.

if not exist reapgate.exe (
    echo ERROR: reapgate.exe not found!
    echo.
    echo Please build first using: BUILD.bat
    echo.
    pause
    exit /b 1
)

echo Starting ReapGate on port 7777...
echo.
echo To stop: Press Ctrl+C
echo.

reapgate.exe
