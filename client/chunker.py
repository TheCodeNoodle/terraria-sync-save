import os
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import hashing

LOCAL_CACHE_DIR = Path(os.path.expandvars(r"%localappdata%/SyncSave/chunk_cache"))

def chunk_file(file_path):
    """
    Splits a file into content-addressed chunks in a local cache dir.
    Returns an ordered list of chunk hashes — this order is what lets
    restore.py reconstruct the file correctly.
    """
    LOCAL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    chunk_hashes = []
    for chunk, chunk_hash in hashing.hash_file_chunks(file_path):
        chunk_path = LOCAL_CACHE_DIR / f"{chunk_hash}.chunk"
        if not chunk_path.exists():  # identical content across saves = free dedup
            with open(chunk_path, "wb") as out:
                out.write(chunk)
        chunk_hashes.append(chunk_hash)
    return chunk_hashes
