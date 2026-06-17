"""Moodle REST API client

Simple client to call Moodle webservice REST endpoints using a service token.
Reads MOODLE_URL and MOODLE_TOKEN from environment if not provided explicitly.

This implementation is intentionally minimal and dependency-light.
"""
from typing import Any, Dict
import os
import time
import requests


class MoodleAPIError(Exception):
    pass


class MoodleClient:
    def __init__(self, base_url: str | None = None, token: str | None = None, timeout: int = 10, max_retries: int = 3):
        self.base_url = base_url or os.getenv("MOODLE_URL")
        self.token = token or os.getenv("MOODLE_TOKEN")
        if not self.base_url:
            raise ValueError("MOODLE_URL not provided (either pass base_url or set MOODLE_URL env var)")
        if not self.token:
            raise ValueError("MOODLE_TOKEN not provided (either pass token or set MOODLE_TOKEN env var)")
        self.timeout = timeout
        self.max_retries = max_retries
        self._endpoint = self.base_url.rstrip("/") + "/webservice/rest/server.php"

    def _flatten_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert lists into the Moodle indexed form (e.g. courseids[0]=1, courseids[1]=2)
        and keep nested dicts by key.subkey notation where needed.
        This is a pragmatic serializer for common Moodle REST patterns.
        """
        flat: Dict[str, Any] = {}

        def _rec(prefix: str, value: Any):
            if isinstance(value, list):
                for i, v in enumerate(value):
                    _rec(f"{prefix}[{i}]", v)
            elif isinstance(value, dict):
                for k, v in value.items():
                    _rec(f"{prefix}[{k}]", v)
            else:
                flat[prefix] = value

        for k, v in (params or {}).items():
            _rec(k, v)
        return flat

    def call_api(self, wsfunction: str, params: dict | None = None) -> Any:
        """Call a Moodle webservice function and return the parsed JSON result.

        Args:
            wsfunction: Moodle wsfunction name (e.g. 'core_course_get_courses')
            params: Additional parameters (dict). Lists will be converted to indexed form.
        """
        payload = {
            "wstoken": self.token,
            "wsfunction": wsfunction,
            "moodlewsrestformat": "json",
        }
        if params:
            payload.update(self._flatten_params(params))

        last_exc = None
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = requests.post(self._endpoint, data=payload, timeout=self.timeout)
                resp.raise_for_status()
                data = resp.json()
                # Moodle returns errors as objects with 'exception' key
                if isinstance(data, dict) and data.get("exception"):
                    raise MoodleAPIError(data)
                return data
            except requests.RequestException as e:
                last_exc = e
                # For server errors, backoff and retry
                if attempt < self.max_retries:
                    time.sleep(0.5 * attempt)
                    continue
                raise
            except ValueError as e:
                # JSON decode error
                raise MoodleAPIError("Invalid JSON response") from e
        # If we exit loop unexpectedly
        if last_exc:
            raise last_exc

