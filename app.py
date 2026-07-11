"""
SyncSave desktop UI.

Run from the project root (same folder as client/, server/, shared/):
    python app.py

Requires:
    pip install flet psutil
(in addition to your existing requirements-client.txt)
"""

import os
import sys
import time
import threading
from pathlib import Path

import flet as ft
import psutil

sys.path.insert(0, str(Path(__file__).resolve().parent))

from client import config
from client.restore import restore_file
from client.chunker import LOCAL_CACHE_DIR
from client import sync_loop

STEAM_APP_IDS = {
    "vanilla": "105600",
    "tmodloader": "1281930",
}


def is_game_running(game_type: str) -> bool:
    if game_type == "vanilla":
        for p in psutil.process_iter(["name"]):
            try:
                if (p.info["name"] or "").lower() == "terraria.exe":
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    else:
        for p in psutil.process_iter(["name", "cmdline"]):
            try:
                if (p.info["name"] or "").lower() == "dotnet.exe":
                    cmdline = " ".join(p.info["cmdline"] or [])
                    if "tmodloader" in cmdline.lower():
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False


def main(page: ft.Page):
    page.title = "SyncSave"
    page.window_width = 480
    page.window_height = 680
    page.window_resizable = False
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    page.bgcolor = "#0f0f14"
    page.fonts = {}

    game_type = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="vanilla", label="Vanilla"),
                ft.Radio(value="tmodloader", label="tModLoader"),
            ]
        ),
        value="vanilla",
    )

    world_name = ft.TextField(label="World name", width=420)
    auto_launch = ft.Checkbox(label="Launch the game automatically", value=True)

    status_log = ft.ListView(expand=True, spacing=4, auto_scroll=True)
    play_button = ft.ElevatedButton("Restore & Play", width=420, height=48)
    sync_button = ft.OutlinedButton("Sync now", width=420, height=44)

    def log(msg, color=None):
        status_log.controls.append(ft.Text(msg, size=13, color=color))
        page.update()

    def set_busy(busy: bool):
        play_button.disabled = busy
        sync_button.disabled = busy
        page.update()

    def do_sync_only():
        def worker():
            set_busy(True)
            try:
                log("Syncing...")
                sync_loop.run(run_once=True)
                log("Synced successfully.", "green400")
            except Exception as ex:
                log(f"Sync failed: {ex}", "red400")
            finally:
                set_busy(False)

        threading.Thread(target=worker, daemon=True).start()

    def run_session(e):
        gt = game_type.value
        config.GAME_TYPE = gt  # affects paths.py, uploader.py, restore.py at call time
        name = world_name.value.strip()

        if not name:
            log("Enter a world name first.", "red400")
            return

        def worker():
            set_busy(True)
            try:
                log(f"Pulling latest save for '{name}' ({gt})...")
                restore_file(
                    server_url=config.SERVER_URL,
                    user=config.USER,
                    token=config.TOKEN,
                    name=name,
                    cache_dir=LOCAL_CACHE_DIR,
                )
                log("Restore complete.", "green400")
            except Exception as ex:
                log(f"Restore failed: {ex}", "red400")
                set_busy(False)
                return

            if not auto_launch.value:
                log("Auto-launch off - play manually, then hit 'Sync now'.", "amber400")
                set_busy(False)
                return

            app_id = STEAM_APP_IDS[gt]
            log(f"Launching via Steam (app {app_id})...")
            os.startfile(f"steam://rungameid/{app_id}")

            log("Waiting for the game to start...")
            waited = 0
            while not is_game_running(gt) and waited < 90:
                time.sleep(2)
                waited += 2

            if not is_game_running(gt):
                log("Didn't detect the game after 90s. Play manually, then hit 'Sync now'.", "amber400")
                set_busy(False)
                return

            log("Game is running. Have fun!", "green400")
            while is_game_running(gt):
                time.sleep(5)

            log("Game closed. Syncing...")
            try:
                sync_loop.run(run_once=True)
                log("Synced successfully.", "green400")
            except Exception as ex:
                log(f"Sync failed: {ex}", "red400")
            finally:
                set_busy(False)

        threading.Thread(target=worker, daemon=True).start()

    play_button.on_click = run_session
    sync_button.on_click = lambda e: do_sync_only()

    page.add(
        ft.Text("SyncSave", size=28, weight=ft.FontWeight.BOLD),
        ft.Text("Terraria save sync", size=14, color="grey400"),
        ft.Divider(),
        ft.Text("Game version", size=13, weight=ft.FontWeight.W_600),
        game_type,
        world_name,
        auto_launch,
        ft.Container(height=10),
        play_button,
        sync_button,
        ft.Container(height=14),
        ft.Text("Log", size=13, weight=ft.FontWeight.W_600),
        ft.Container(
            content=status_log,
            height=220,
            bgcolor="#1a1a22",
            border_radius=10,
            padding=12,
        ),
    )


if __name__ == "__main__":
    ft.app(target=main)