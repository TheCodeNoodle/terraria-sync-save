@echo off
setlocal enabledelayedexpansion
set SYNCSAVE_GAME_TYPE=vanilla

echo ============================================
echo    SyncSave - Play Session (Vanilla)
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
echo.
echo Pulling the latest save for "%WORLD_NAME%"...
echo.
python -m client.restore "%WORLD_NAME%"
if errorlevel 1 (
    echo.
    echo Restore failed. Scroll up to see the error above.
    pause
    exit /b 1
)

echo.
set /p LAUNCH_GAME=Should this script launch Terraria for you? (y/n):
if /i "%LAUNCH_GAME%"=="y" goto DO_LAUNCH
goto MANUAL_MODE

:DO_LAUNCH
echo.
echo Launching Terraria via Steam...
start "" "steam://rungameid/105600"
echo.
echo Waiting for Terraria to start...
set WAITED=0
:WAIT_START
tasklist /FI "IMAGENAME eq Terraria.exe" 2>NUL | find /I "Terraria.exe" >NUL
if not errorlevel 1 goto GAME_RUNNING
timeout /t 2 >NUL
set /a WAITED+=2
if %WAITED% GEQ 90 (
    echo.
    echo Terraria didn't seem to start after 90 seconds.
    echo Press any key once you're done playing to sync your progress manually.
    pause
    goto SYNC_NOW
)
goto WAIT_START
:GAME_RUNNING
echo Terraria is running. Have fun!
echo (this window will wait until you close the game, then sync automatically)
echo.
:WAIT_CLOSE
timeout /t 5 >NUL
tasklist /FI "IMAGENAME eq Terraria.exe" 2>NUL | find /I "Terraria.exe" >NUL
if not errorlevel 1 goto WAIT_CLOSE
echo.
echo Terraria closed. Syncing your progress...
echo.
goto SYNC_NOW

:MANUAL_MODE
echo.
echo Okay - go ahead and launch Terraria yourself whenever you're ready.
echo Come back to this window and press any key once you're done playing.
pause

:SYNC_NOW
python -m client.sync_loop --once
if errorlevel 1 (
    echo.
    echo Sync failed. Your progress may not have been pushed - check the
    echo error above and consider running "python -m client.sync_loop --once"
    echo manually before closing this window.
    pause
    exit /b 1
)
echo.
echo ============================================
echo    All synced up!
echo ============================================
pause