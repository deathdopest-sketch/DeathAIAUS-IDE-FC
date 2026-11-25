@echo off
cls
color 0A
echo.
echo  ================================================
echo   Creating Desktop Shortcut
echo  ================================================
echo.

REM Get current directory
set "CURRENT_DIR=%~dp0"
set "LAUNCH_FILE=%CURRENT_DIR%launch.bat"

REM Check if launch.bat exists
if not exist "%LAUNCH_FILE%" (
    echo  [ERROR] launch.bat not found!
    echo.
    pause
    exit /b 1
)

echo  [*] Found launch.bat: %LAUNCH_FILE%
echo.
echo  [*] Creating shortcut on desktop...
echo.

REM Create VBS script
set "VBS_FILE=%TEMP%\create_shortcut_temp.vbs"

(
echo Set WshShell = WScript.CreateObject^("WScript.Shell"^)
echo DesktopPath = WshShell.SpecialFolders^("Desktop"^)
echo Set oShellLink = WshShell.CreateShortcut^(DesktopPath ^& "\DeathAIAUS IDE.lnk"^)
echo oShellLink.TargetPath = "%LAUNCH_FILE%"
echo oShellLink.WorkingDirectory = "%CURRENT_DIR%"
echo oShellLink.Description = "DeathAIAUS IDE - AI Development Environment"
echo oShellLink.Save
) > "%VBS_FILE%"

REM Execute VBS
cscript //nologo "%VBS_FILE%"

REM Check result
if errorlevel 1 (
    echo.
    echo  [ERROR] Failed to create shortcut!
    echo.
    pause
    del "%VBS_FILE%" 2>nul
    exit /b 1
)

REM Cleanup
del "%VBS_FILE%" 2>nul

echo.
echo  ================================================
echo   SUCCESS! Desktop shortcut created!
echo  ================================================
echo.
echo  Look on your desktop for:
echo  "DeathAIAUS IDE"
echo.
echo  Desktop location: %USERPROFILE%\Desktop
echo.
echo  Double-click it to launch the IDE!
echo.
pause

