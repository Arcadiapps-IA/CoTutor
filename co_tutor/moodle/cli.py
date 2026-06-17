"""CLI tool to interactively configure Moodle connection for CoTutor.

Usage:
  python -m co_tutor.moodle.cli

Options:
  --base-url URL     Moodle base URL (e.g. https://moodle.example.org). If omitted, prompted.
  --username USER    Username to authenticate. If omitted, prompted.
  --service SERVICE  Service shortname to request a token for (default: moodle_mobile_app).
  --no-save-username Do not store the username in the local config (only base_url and token will be saved).

The CLI will prompt for the password securely and attempt to obtain a token via
/login/token.php. On success it stores the connection in co_tutor/moodle/.moodle_config.json
using the existing config_store.save_config().
"""
from __future__ import annotations
import argparse
import getpass
import sys

from .client import MoodleClient, MoodleAPIError
from .config_store import save_config


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="moodle-cli", description="Configure Moodle connection for CoTutor")
    parser.add_argument("--base-url", help="Moodle base URL (e.g. https://moodle.example.org)")
    parser.add_argument("--username", help="Username to authenticate as")
    parser.add_argument("--service", default="moodle_mobile_app", help="Service shortname to request token for (default: moodle_mobile_app)")
    parser.add_argument("--no-save-username", action="store_true", help="Do not save the username in the local config")

    args = parser.parse_args(argv)

    try:
        base_url = args.base_url or input("Moodle URL: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("Aborted.")
        return 1

    if not base_url:
        print("Moodle URL is required", file=sys.stderr)
        return 2

    try:
        username = args.username or input("Username: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("Aborted.")
        return 1

    if not username:
        print("Username is required", file=sys.stderr)
        return 2

    try:
        password = getpass.getpass("Password: ")
    except (EOFError, KeyboardInterrupt):
        print("Aborted." )
        return 1

    if not password:
        print("Password is required", file=sys.stderr)
        return 2

    service = args.service

    client = MoodleClient(base_url=base_url)
    try:
        token = client.authenticate_with_credentials(username, password, service=service)
    except MoodleAPIError as e:
        print(f"Authentication failed: {e}", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 4

    cfg = {
        "base_url": base_url,
        "token": token,
        "service": service,
        "saved_at": None,
    }
    if not args.no_save_username:
        cfg["username"] = username

    save_config(cfg)
    print("Moodle connection saved locally.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
