import json
from pathlib import Path


def check(workspace: Path) -> dict:
    try:
        config = json.loads((workspace / "config.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"passed": False, "reason": f"Cannot read valid config.json: {exc}"}

    valid = (
        isinstance(config, dict)
        and isinstance(config.get("server"), dict)
        and config["server"].get("host") == "127.0.0.1"
        and type(config["server"].get("port")) is int
        and config["server"]["port"] == 8765
        and isinstance(config.get("paths"), dict)
        and config["paths"].get("data_dir") == "./data"
        and config["paths"].get("log_file") == "./logs/service.log"
        and isinstance(config.get("features"), dict)
        and type(config["features"].get("cache_enabled")) is bool
        and config["features"]["cache_enabled"] is True
        and type(config["features"].get("debug_enabled")) is bool
        and config["features"]["debug_enabled"] is False
    )
    return {
        "passed": valid,
        "reason": "All checks passed" if valid else "Config fields, types or values are incorrect",
    }
