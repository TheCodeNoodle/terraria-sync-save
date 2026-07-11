import time
import logging
from pathlib import Path
import sys

from client import watcher
from client import chunker
from client import manifest as manifest_mod
from client import config
from client.uploader import SyncClient
from shared import hashing

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("syncloop")

STATE_DIR = Path.home() / ".syncsave"
STATE_DIR.mkdir(exist_ok=True)


class FileState:
    """Tracks last-synced hash and in-progress 'is this file still being written' checks."""
    def __init__(self, path, name, kind):
        self.path = path
        self.name = name
        self.kind = kind
        self.last_synced_hash = self._load_last_synced()
        self._pending_hash = None
        self._stable_count = 0

    def _state_file(self):
        return STATE_DIR / f"{self.kind}_{self.name}.lastsync"

    def _load_last_synced(self):
        f = self._state_file()
        return f.read_text().strip() if f.exists() else None

    def _save_last_synced(self, hash_):
        self._state_file().write_text(hash_)
        self.last_synced_hash = hash_

    def poll(self):
        """
        Returns True if the file has changed AND been stable for
        STABLE_CHECKS_REQUIRED consecutive polls (i.e. Terraria finished writing it).
        """
        try:
            current_hash = hashing.hash_file_whole(self.path)
        except (FileNotFoundError, PermissionError) as e:
            log.warning(f"Couldn't hash {self.path}: {e}")
            return False

        if current_hash == self.last_synced_hash:
            self._stable_count = 0
            return False  # unchanged since last sync, nothing to do

        if current_hash == self._pending_hash:
            self._stable_count += 1
        else:
            self._pending_hash = current_hash
            self._stable_count = 1

        if self._stable_count >= config.STABLE_CHECKS_REQUIRED:
            self._stable_count = 0
            return True
        return False

    def mark_synced(self):
        if self._pending_hash:
            self._save_last_synced(self._pending_hash)


def sync_one(client, state: FileState):
    log.info(f"Change detected in {state.kind} '{state.name}', syncing...")
    chunk_hashes = chunker.chunk_file(state.path)
    man = manifest_mod.build_manifest(state.name, chunk_hashes, state.kind)
    client.sync_save(chunk_hashes, chunker.LOCAL_CACHE_DIR, man)
    state.mark_synced()
    log.info(f"Synced {state.kind} '{state.name}' ({len(chunk_hashes)} chunks)")


def run(run_once=False):
    client = SyncClient(config.SERVER_URL, config.USER, config.TOKEN)

    tracked = []
    try:
        world_path, world_name = watcher.get_active_world()
        tracked.append(FileState(world_path, world_name, "world"))
    except FileNotFoundError as e:
        log.warning(e)

    if not tracked:
        log.error("No world or player files found — nothing to sync. Exiting.")
        return

    log.info(f"Watching {len(tracked)} file(s)")

    if run_once:
            # Called right after the game closes - compare against the last
            # synced hash directly instead of force-syncing every time.
            for state in tracked:
                try:
                    current_hash = hashing.hash_file_whole(state.path)
                except (FileNotFoundError, PermissionError) as e:
                    log.warning(f"Couldn't hash {state.path}: {e}")
                    continue
                if current_hash == state.last_synced_hash:
                    log.info(f"No changes in {state.kind} '{state.name}', skipping.")
                    continue
                state._pending_hash = current_hash
                try:
                    sync_one(client, state)
                except Exception as e:
                    log.error(f"Sync failed for {state.name}: {e}")
            return

    log.info(f"Polling every {config.POLL_INTERVAL_SECONDS}s")
    while True:
        for state in tracked:
            if state.poll():
                try:
                    sync_one(client, state)
                except Exception as e:
                    log.error(f"Sync failed for {state.name}: {e}")
        time.sleep(config.POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_once = "--once" in sys.argv
    run(run_once=run_once)