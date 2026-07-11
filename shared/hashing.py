import hashlib

CHUNK_SIZE = 4 * 1024 * 1024  # 4 MB — keep in sync with chunker.py

def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def hash_file_chunks(path, chunk_size=CHUNK_SIZE):
    """Yield (chunk_bytes, chunk_hash) for a file, in order."""
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk, hash_bytes(chunk)

def hash_file_whole(path):
    """Full-file hash — cheap way to check 'did this file change at all' before re-chunking."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()
