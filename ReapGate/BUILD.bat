@echo off
echo ============================================
echo  Building ReapGate - Death's Inference Engine
echo ============================================
echo.

echo [1/3] Checking Go installation...
go version
if errorlevel 1 (
    echo ERROR: Go is not installed!
    echo.
    echo Please install Go from: https://go.dev/dl/
    pause
    exit /b 1
)

echo.
echo [2/3] Tidying dependencies...
go mod tidy
if errorlevel 1 (
    echo ERROR: Failed to tidy dependencies!
    pause
    exit /b 1
)

echo.
echo [2.5/3] Downloading dependencies...
go mod download
if errorlevel 1 (
    echo ERROR: Failed to download dependencies!
    pause
    exit /b 1
)

echo.
echo [3/3] Building ReapGate...
go build -o reapgate.exe
if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo [4/4] Copying required DLLs...
if exist "C:\mingw64\mingw64\bin\libwinpthread-1.dll" (
    copy /Y "C:\mingw64\mingw64\bin\libwinpthread-1.dll" .
    copy /Y "C:\mingw64\mingw64\bin\libstdc++-6.dll" .
    copy /Y "C:\mingw64\mingw64\bin\libgcc_s_seh-1.dll" .
    echo DLLs copied successfully!
) else (
    echo WARNING: MinGW DLLs not found. ReapGate may not run.
)

echo.
echo ============================================
echo  BUILD SUCCESSFUL!
echo ============================================
echo.
echo ReapGate.exe created!
echo.
echo To run: .\reapgate.exe
echo Or use: START_REAPGATE.bat
echo.
pause
