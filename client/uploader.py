import requests
from client import config
class SyncClient:
    def __init__(self, server_url, user, token):
        self.server_url = server_url.rstrip("/")
        self.user = user
        self.token = token

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "X-SyncSave-User": self.user,
        }
    def chunk_exists_on_server(self, chunk_hash):
        r = requests.head(f"{self.server_url}/chunks/{chunk_hash}", headers=self._headers())
        return r.status_code == 200

    def upload_chunk(self, chunk_path, chunk_hash):
        if self.chunk_exists_on_server(chunk_hash):
            return  # server already has this content — skip
        with open(chunk_path, "rb") as f:
            r = requests.put(f"{self.server_url}/chunks/{chunk_hash}", data=f, headers=self._headers())
        r.raise_for_status()

    def upload_manifest(self, manifest):
        r = requests.post(
            f"{self.server_url}/manifests/{config.GAME_TYPE}/{manifest['name']}",
            json=manifest, headers=self._headers(),
        )
        r.raise_for_status()
        
    def sync_save(self, chunk_hashes, chunk_cache_dir, manifest):
        for chunk_hash in chunk_hashes:
            self.upload_chunk(chunk_cache_dir / f"{chunk_hash}.chunk", chunk_hash)
        self.upload_manifest(manifest)