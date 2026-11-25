# Simple PowerShell script to create desktop shortcut
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "DeathAIAUS IDE.lnk"
$TargetPath = Join-Path $PSScriptRoot "launch.bat"
$WorkingDir = $PSScriptRoot

$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $WorkingDir
$Shortcut.Description = "DeathAIAUS IDE - AI-Powered Development Environment"
$Shortcut.Save()

Write-Host ""
Write-Host "SUCCESS! Desktop shortcut created!" -ForegroundColor Green
Write-Host ""
Write-Host "Look on your desktop for: DeathAIAUS IDE" -ForegroundColor Cyan
Write-Host ""
Write-Host "Desktop location: $DesktopPath" -ForegroundColor Yellow
Write-Host "Shortcut file: $ShortcutPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to close..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

