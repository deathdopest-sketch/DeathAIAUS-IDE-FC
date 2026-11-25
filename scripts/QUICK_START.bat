@echo off
cls
color 0B
echo.
echo  ================================================
echo   DeathAIAUS IDE - Quick Start
echo  ================================================
echo.
echo  Choose an option:
echo.
echo  1. Launch IDE now
echo  2. Create desktop shortcut
echo  3. Both (Launch + Create shortcut)
echo.
echo  ================================================
echo.
set /p choice="Enter your choice (1, 2, or 3): "

if "%choice%"=="1" goto launch
if "%choice%"=="2" goto shortcut
if "%choice%"=="3" goto both
goto invalid

:launch
echo.
echo  Launching IDE...
echo.
call launch.bat
goto end

:shortcut
echo.
echo  Creating desktop shortcut...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0MAKE_SHORTCUT.ps1"
goto end

:both
echo.
echo  Creating desktop shortcut...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0MAKE_SHORTCUT.ps1"
echo.
echo  Launching IDE...
echo.
call launch.bat
goto end

:invalid
echo.
echo  Invalid choice. Please run again and choose 1, 2, or 3.
echo.
pause
goto end

:end

