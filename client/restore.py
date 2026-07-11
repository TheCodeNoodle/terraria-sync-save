import requests
from pathlib import Path
from client import config
import sys
from client.paths import world_path, player_path

def get_latest_manifest(server_url, user, token, name, game_type):
    r = requests.get(
        f"{server_url}/manifests/{game_type}/{name}/latest",
        headers={"Authorization": f"Bearer {token}", "X-SyncSave-User": user},
    )

    if r.status_code == 404:
        return None

    r.raise_for_status()
    return r.json()

def download_chunk(server_url, chunk_hash, token, cache_dir):
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    chunk_path = cache_dir / f"{chunk_hash}.chunk"
    if chunk_path.exists():
        return chunk_path
    r = requests.get(f"{server_url}/chunks/{chunk_hash}", headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    chunk_path.write_bytes(r.content)
    return chunk_path

def restore_file(server_url, user, name, token, cache_dir):
    manifest = get_latest_manifest(server_url, user, token, name, game_type = config.GAME_TYPE)
    if manifest is None:
        print(f"No save named '{name}' exists on the server.")
        return None
    kind = manifest["kind"].lower()
    if kind == "world":
        output_path = world_path(manifest["name"])
    elif kind == "player":
        output_path = player_path(manifest["name"])
    else:
        raise ValueError(f"Unknown manifest kind: {manifest['kind']!r}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as out:
        for chunk_hash in manifest["chunk_hashes"]:
            chunk_path = download_chunk(server_url, chunk_hash, token, cache_dir)
            out.write(chunk_path.read_bytes())
    return output_path

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m client.restore <save_name>")
        sys.exit(1)

    name = sys.argv[1]
    from client.chunker import LOCAL_CACHE_DIR

    result = restore_file(
        server_url=config.SERVER_URL,
        user=config.USER,
        name=name,
        token=config.TOKEN,
        cache_dir=LOCAL_CACHE_DIR,
    )
    if result is None:
        print("Starting with a fresh save.")
    else:
        print(f"Restored '{name}' to {result}")


if __name__ == "__main__":
    main()
