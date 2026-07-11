import json
import time
from pathlib import Path

def build_manifest(name, chunk_hashes, kind):
    """kind: "world" or "player" """
    return {
        "name": name,
        "kind": kind,
        "chunk_hashes": chunk_hashes,  # ORDER MATTERS — this is how the file gets rebuilt
        "chunk_count": len(chunk_hashes),
        "timestamp": time.time(),
    }

def save_manifest_local(manifest, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{manifest['name']}.manifest.json"
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
    return path

def load_manifest_local(path):
    with open(path, "r") as f:
        return json.load(f)