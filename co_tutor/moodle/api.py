from flask import Blueprint, request, jsonify
from .client import MoodleClient, MoodleAPIError
from .config_store import save_config, load_config, clear_config
import time

bp = Blueprint("moodle", __name__, url_prefix="/moodle")


@bp.route("/connect", methods=["POST"])
def connect():
    """Authenticate to Moodle using user credentials and store the token.

    Expects JSON body: {"base_url": ..., "username": ..., "password": ..., "service": "moodle_mobile_app"}
    Returns 200 on success.
    """
    data = request.get_json(silent=True) or {}
    base_url = data.get("base_url")
    username = data.get("username")
    password = data.get("password")
    service = data.get("service", "moodle_mobile_app")

    if not base_url or not username or not password:
        return jsonify({"error": "base_url, username and password are required"}), 400

    client = MoodleClient(base_url=base_url)
    try:
        token = client.authenticate_with_credentials(username, password, service=service)
    except MoodleAPIError as e:
        return jsonify({"error": "authentication_failed", "details": str(e)}), 400

    cfg = {
        "base_url": base_url,
        "username": username,
        "token": token,
        "service": service,
        "saved_at": int(time.time()),
    }
    save_config(cfg)
    return jsonify({"status": "ok", "saved": True})


@bp.route("/config", methods=["GET"])
def get_config():
    cfg = load_config()
    if not cfg:
        return jsonify({"configured": False}), 404
    masked = cfg.copy()
    if "token" in masked:
        t = masked.get("token", "")
        masked["token_present"] = bool(t)
        if t:
            masked["token"] = (t[:4] + "..." ) if len(t) > 8 else "****"
    return jsonify({"configured": True, "config": masked})


@bp.route("/disconnect", methods=["POST"])
def disconnect():
    clear_config()
    return jsonify({"status": "ok"})
