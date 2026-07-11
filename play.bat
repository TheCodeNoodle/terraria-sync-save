@echo off
setlocal enabledelayedexpansion

echo ============================================
echo    SyncSave - Play
echo ============================================
echo.

if not exist "client" (
    echo ERROR: Run this from inside the Terraria-save-sync folder.
    pause
    exit /b 1
)

set /p WORLD_NAME=Enter the world name to sync (e.g. MyWorld):

if "%WORLD_NAME%"=="" (
    echo ERROR: World name cannot be empty.
    pause
    exit /b 1
)

set WORLD_PATH=%USERPROFILE%\Documents\My Games\Terraria\Worlds\%WORLD_NAME%.wld

echo.
echo Pulling the latest save for "%WORLD_NAME%"...
echo.
python -m client.restore "%WORLD_NAME%" "%WORLD_PATH%"

if errorlevel 1 (
    echo.
    echo Something went wrong during restore. Scroll up to see the error above.
    pause
    exit /b 1
)

echo.
echo ============================================
echo    You're up to date!
echo ============================================
echo.
echo Go ahead and launch Terraria now.
echo.
echo When you're done playing, run this to push your changes back:
echo   python -m client.sync_loop
echo   (press Ctrl+C once you see "Synced" in the log)
echo.
pause
