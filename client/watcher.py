import os
import glob
from client.paths import worlds_folder, players_folder

def expand_env_path(path):
    return os.path.expandvars(path).replace("\\", "/")

PLAYER_PATH_FOLDER = players_folder()
WORLD_PATH_FOLDER = worlds_folder()

def find_worlds():
    return [f.replace("\\", "/") for f in glob.glob(f"{WORLD_PATH_FOLDER}/*.wld")]

def find_players():
    return [f.replace("\\", "/") for f in glob.glob(f"{PLAYER_PATH_FOLDER}/*.plr")]

def name_from_path(path):
    return os.path.splitext(os.path.basename(path))[0]

def get_active_world():
    worlds = find_worlds()
    if not worlds:
        raise FileNotFoundError("No .wld file found in Worlds folder")
    world_path = worlds[0]  # TODO: support choosing among multiple worlds
    return world_path, name_from_path(world_path)

def get_active_player():
    players = find_players()
    if not players:
        raise FileNotFoundError("No .plr file found in Players folder")
    player_path = players[0]  # TODO: support choosing among multiple players
    return player_path, name_from_path(player_path)

if __name__ == "__main__":
    world_path, world_name = get_active_world()
    player_path, player_name = get_active_player()
    print(f"World: {world_name} -> {world_path}")
    print(f"Player: {player_name} -> {player_path}")