@echo off
echo Building PokerTracker...

if exist "build" (
    echo Cleaning previous build...
    rmdir /s /q build
)

if exist "dist" (
    echo Cleaning dist...
    rmdir /s /q dist
)

echo Running PyInstaller...
pyinstaller PokerTracker.spec

if exist "dist\PokerTracker\PokerTracker.exe" (
    echo.
    echo Build successful!
    echo Output: dist\PokerTracker\PokerTracker.exe
    echo.
    for %%A in ("dist\PokerTracker\PokerTracker.exe") do echo File size: %%~zA bytes
) else (
    echo Build failed!
    pause
    exit /b 1
)

echo.
pause
