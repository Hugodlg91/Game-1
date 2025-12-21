"""Simple settings manager for keybindings persisted as JSON.

Provides load_settings(), save_settings(), configure_keybindings().
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

DEFAULT_SETTINGS = {
    "keys": {
        "up": "w",
        "down": "s",
        "left": "a",
        "right": "d",
    }
}

# Add KEYS alias if that's what was expected, or fix import to use DEFAULT_SETTINGS
KEYS = DEFAULT_SETTINGS["keys"]

SETTINGS_PATH = Path("settings.json")


def load_settings() -> Dict:
    if SETTINGS_PATH.exists():
        try:
            with SETTINGS_PATH.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: Dict) -> None:
    with SETTINGS_PATH.open("w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2, ensure_ascii=False)


def configure_keybindings() -> None:
    """Interactive console configuration for keybindings."""
    settings = load_settings()
    keys = settings.get("keys", {})
    print("Configure keybindings (press Enter to keep current)")
    for action in ("up", "down", "left", "right"):
        current = keys.get(action, "")
        prompt = f"Key for {action} [{current}]: "
        choice = input(prompt).strip().lower()
        if choice:
            keys[action] = choice
    settings["keys"] = keys
    save_settings(settings)
    print(f"Saved settings to {SETTINGS_PATH}")
