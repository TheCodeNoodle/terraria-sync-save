from flask import Flask, request, send_file, jsonify, abort
from pathlib import Path
import json

app = Flask(__name__)
BASE_DIR = Path(__file__).parent
CHUNKS_DIR, MANIFESTS_DIR, USERS_DIR = BASE_DIR / "chunks", BASE_DIR / "manifests", BASE_DIR / "users"
for d in (CHUNKS_DIR, MANIFESTS_DIR, USERS_DIR):
    d.mkdir(exist_ok=True)

def check_auth(user):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    token_file = USERS_DIR / f"{user}.token"
    if not token_file.exists() or token_file.read_text().strip() != token:
        abort(401)

@app.route("/chunks/<chunk_hash>", methods=["HEAD"])
def chunk_head(chunk_hash):
    return ("", 200) if (CHUNKS_DIR / f"{chunk_hash}.chunk").exists() else ("", 404)

@app.route("/chunks/<chunk_hash>", methods=["PUT"])
def chunk_put(chunk_hash):
    path = CHUNKS_DIR / f"{chunk_hash}.chunk"
    if not path.exists():
        path.write_bytes(request.get_data())
    return ("", 201)

@app.route("/chunks/<chunk_hash>", methods=["GET"])
def chunk_get(chunk_hash):
    path = CHUNKS_DIR / f"{chunk_hash}.chunk"
    if not path.exists():
        abort(404)
    return send_file(path)

@app.route("/manifests/<user>/<name>", methods=["POST"])
def manifest_post(user, name):
    check_auth(user)
    user_dir = MANIFESTS_DIR / user
    user_dir.mkdir(exist_ok=True)
    manifest = request.get_json()
    (user_dir / f"{name}.{manifest.get('timestamp', 0)}.json").write_text(json.dumps(manifest))
    (user_dir / f"{name}.latest.json").write_text(json.dumps(manifest))  # keeps version history too
    return ("", 201)

@app.route("/manifests/<user>/<name>/latest", methods=["GET"])
def manifest_latest(user, name):
    check_auth(user)
    latest_path = MANIFESTS_DIR / user / f"{name}.latest.json"
    if not latest_path.exists():
        abort(404)
    return jsonify(json.loads(latest_path.read_text()))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
