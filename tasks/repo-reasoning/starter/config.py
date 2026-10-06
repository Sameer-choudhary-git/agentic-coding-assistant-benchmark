import json
import os
from pathlib import Path

DEFAULT_TIMEOUT_SECONDS = 30


def load_service_config(config_path="service.json", environ=None):
    """Load settings from JSON, then let environment variables override them."""
    environ = os.environ if environ is None else environ
    file_values = {}
    path = Path(config_path)
    if path.exists():
        file_values = json.loads(path.read_text(encoding="utf8"))
    timeout = environ.get("SERVICE_TIMEOUT_SECONDS", file_values.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS))
    endpoint = environ.get("SERVICE_ENDPOINT", file_values.get("endpoint", "http://localhost"))
    return {"endpoint": endpoint, "timeout_seconds": int(timeout)}
