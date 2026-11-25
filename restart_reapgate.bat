@echo off
echo Killing existing ReapGate processes...
taskkill /f /im reapgate.exe 2>nul
timeout /t 2 /nobreak >nul

echo Starting ReapGate...
cd ReapGate
start reapgate.exe

echo ReapGate restarted! Check http://localhost:7777/health
pause
