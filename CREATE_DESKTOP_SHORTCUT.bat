@echo off
REM Create Desktop Shortcut for DeathAIAUS IDE
echo.
echo Creating desktop shortcut for DeathAIAUS IDE...
echo.

REM Get current directory
set "SCRIPT_DIR=%~dp0"
set "TARGET=%SCRIPT_DIR%DeathAIAUS_Launcher.py"
set "ICON=%SCRIPT_DIR%deathaius_ide_fc.py"

REM Create VBScript to make shortcut
set "VBSCRIPT=%TEMP%\create_shortcut.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBSCRIPT%"
echo sLinkFile = oWS.SpecialFolders("Desktop") ^& "\DeathAIAUS IDE.lnk" >> "%VBSCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBSCRIPT%"
echo oLink.TargetPath = "%TARGET%" >> "%VBSCRIPT%"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%VBSCRIPT%"
echo oLink.Description = "DeathAIAUS IDE F.C - AI-Powered Development Environment" >> "%VBSCRIPT%"
echo oLink.Save >> "%VBSCRIPT%"

REM Run VBScript
cscript //nologo "%VBSCRIPT%"

REM Cleanup
del "%VBSCRIPT%"

echo.
echo ✓ Desktop shortcut created successfully!
echo.
echo You can now launch the IDE from your desktop.
echo.
pause
