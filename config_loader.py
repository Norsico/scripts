import json
from pathlib import Path
from typing import Any, Dict

# Default
DEFAULT_CONFIG: Dict[str, Any] = {
    "gemini": {
        "base_url": "https://xxx",
        "model": "gemini-2.5-flash-image-preview",
        "api_key": "sk-abc",
        "return_base64_default": False,
    }
}

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
_CONFIG_CACHE: Dict[str, Any] | None = None


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_from_disk() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        # Fall back to defaults if the config file is unreadable
        return {}


def load_config(refresh: bool = False) -> Dict[str, Any]:
    """
    Returns the merged configuration (defaults + config.json).
    Use refresh=True to bypass the in-memory cache.
    """
    global _CONFIG_CACHE

    if _CONFIG_CACHE is None or refresh:
        file_config = _load_from_disk()
        _CONFIG_CACHE = _deep_merge(DEFAULT_CONFIG, file_config)

    return _CONFIG_CACHE
