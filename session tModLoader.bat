@echo off
setlocal enabledelayedexpansion
set SYNCSAVE_GAME_TYPE=tmodloader

echo ============================================
echo    SyncSave - Play Session (tModLoader)
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
set /p LAUNCH_GAME=Should this script launch tModLoader for you? (y/n):
if /i "%LAUNCH_GAME%"=="y" goto DO_LAUNCH
goto MANUAL_MODE

:DO_LAUNCH
echo.
echo Launching tModLoader via Steam...
start "" "steam://rungameid/1281930"
echo.
echo Waiting for tModLoader to start...
set WAITED=0
:WAIT_START
powershell -NoProfile -Command "if (Get-CimInstance Win32_Process -Filter \"Name='dotnet.exe'\" | Where-Object { $_.CommandLine -like '*tModLoader*' }) { exit 0 } else { exit 1 }"
if not errorlevel 1 goto GAME_RUNNING
timeout /t 2 >NUL
set /a WAITED+=2
if %WAITED% GEQ 90 (
    echo.
    echo tModLoader didn't seem to start after 90 seconds.
    echo Press any key once you're done playing to sync your progress manually.
    pause
    goto SYNC_NOW
)
goto WAIT_START
:GAME_RUNNING
echo tModLoader is running. Have fun!
echo (this window will wait until you close the game, then sync automatically)
echo.
:WAIT_CLOSE
timeout /t 5 >NUL
powershell -NoProfile -Command "if (Get-CimInstance Win32_Process -Filter \"Name='dotnet.exe'\" | Where-Object { $_.CommandLine -like '*tModLoader*' }) { exit 0 } else { exit 1 }"
if not errorlevel 1 goto WAIT_CLOSE
echo.
echo tModLoader closed. Syncing your progress...
echo.
goto SYNC_NOW

:MANUAL_MODE
echo.
echo Okay - go ahead and launch tModLoader yourself whenever you're ready.
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