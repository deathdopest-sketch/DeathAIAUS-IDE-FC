@echo off
echo ============================================
echo  Creating DeathAIAUS IDE Desktop Shortcut
echo ============================================
echo.

set SCRIPT_DIR=%~dp0
set SHORTCUT_PATH=%USERPROFILE%\Desktop\DeathAIAUS IDE.lnk
set ICON_PATH=%SCRIPT_DIR%assets\icon.ico

echo Creating shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = '%SCRIPT_DIR%launch.bat'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.IconLocation = '%ICON_PATH%'; $Shortcut.Description = 'DeathAIAUS IDE - AI-Powered Development with ReapGate'; $Shortcut.Save()"

if exist "%SHORTCUT_PATH%" (
    echo.
    echo ============================================
    echo  SUCCESS!
    echo ============================================
    echo.
    echo Desktop shortcut created successfully!
    echo Location: %SHORTCUT_PATH%
    echo.
    echo You can now launch DeathAIAUS IDE from your desktop!
) else (
    echo.
    echo ERROR: Failed to create shortcut.
    echo Please check permissions and try again.
)

echo.
pause

