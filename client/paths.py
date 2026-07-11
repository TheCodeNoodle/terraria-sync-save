from pathlib import Path
import ctypes
from ctypes import wintypes
from client import config

def documents_folder():
    """
    Returns the user's Documents folder.
    Works whether Documents is local, OneDrive, or redirected.
    """
    CSIDL_PERSONAL = 5  # Documents

    buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(
        None,
        CSIDL_PERSONAL,
        None,
        0,
        buf,
    )

    return Path(buf.value)


def terraria_folder():
    base = documents_folder() / "My Games" / "Terraria"
    if config.GAME_TYPE == ("tModLoader").lower():
        return base / "tModLoader"
    else:
        return base


def worlds_folder():
    return terraria_folder() / "Worlds"


def players_folder():
    return terraria_folder() / "Players"


def world_path(name):
    return worlds_folder() / f"{name}.wld"


def player_path(name):
    return players_folder() / f"{name}.plr"