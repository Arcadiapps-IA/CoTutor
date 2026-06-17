import json
import os
from typing import Dict, Any

CONFIG_FILENAME = os.path.join(os.path.dirname(__file__), ".moodle_config.json")


def save_config(data: Dict[str, Any]) -> None:
    """Save configuration to a local file with restrictive permissions.

    The file contains the token returned by Moodle and MUST NOT be committed to
    the repository. We set file mode to 0o600 where possible.
    """
    with open(CONFIG_FILENAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    try:
        os.chmod(CONFIG_FILENAME, 0o600)
    except Exception:
        # Ignore chmod failures on unsupported platforms
        pass


def load_config() -> Dict[str, Any]:
    if not os.path.exists(CONFIG_FILENAME):
        return {}
    with open(CONFIG_FILENAME, "r", encoding="utf-8") as f:
        return json.load(f)


def clear_config() -> None:
    try:
        if os.path.exists(CONFIG_FILENAME):
            os.remove(CONFIG_FILENAME)
    except Exception:
        pass
