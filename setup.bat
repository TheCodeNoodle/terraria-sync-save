@echo off
setlocal enabledelayedexpansion

echo ============================================
echo    SyncSave - Friend Setup
echo ============================================
echo.

REM --- Check Python is installed ---
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found on this PC.
    echo Please install it from https://python.org, make sure to
    echo check "Add Python to PATH" during install, then re-run this script.
    pause
    exit /b 1
)

REM --- Make sure we're being run from the project root ---
if not exist "client" (
    echo ERROR: Couldn't find the "client" folder.
    echo Please run this script from inside the Terraria-save-sync folder.
    pause
    exit /b 1
)

echo Installing required packages, this may take a minute...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies. Check your internet connection.
    pause
    exit /b 1
)

echo.
echo ----------------------------------------------
echo  You'll need the token I sent you.
echo  If you don't have one yet, ask him first.
echo ----------------------------------------------
echo.

set /p SS_NAME=Enter your name, no spaces (e.g. yahya):
set /p SS_TOKEN=Paste your token here:

set CONFIG_FILE=client\config.py

(
echo import os
echo.
echo SERVER_URL = "https://api.palworldsyncsaveterraria.shop"
echo USER = "%SS_NAME%"
echo TOKEN = "%SS_TOKEN%"
echo POLL_INTERVAL_SECONDS = 1
echo STABLE_CHECKS_REQUIRED = 2
echo GAME_TYPE = os.environ.get("SYNCSAVE_GAME_TYPE", "vanilla")
) > "%CONFIG_FILE%"

echo.
echo ============================================
echo    Setup complete!
echo ============================================
echo.
echo Config saved to %CONFIG_FILE%
echo.
echo HOW TO USE IT:
echo.
echo   Before you play, pull the latest save:
echo     python -m client.restore WorldName "C:\Users\%%USERNAME%%\Documents\My Games\Terraria\Worlds\WorldName.wld"
echo.
echo   After you're done playing, push your changes:
echo     python -m client.sync_loop
echo     (press Ctrl+C once you see "Synced" in the log)
echo.
pause
