"""Simple settings manager for keybindings persisted as JSON.

Provides load_settings(), save_settings(), configure_keybindings().
"""
from __future__ import annotations

import json
import sys
import os
from pathlib import Path
from typing import Dict

DEFAULT_SETTINGS = {
    "keys": {
        "up": "w",
        "down": "s",
        "left": "a",
        "right": "d",
    },
    "highscore": 0,
    "theme": "Classic",
    "music_volume": 0.1,
    "sfx_volume": 1.0,
    "music_muted": False,
    "sfx_muted": False
}

# Add KEYS alias if that's what was expected, or fix import to use DEFAULT_SETTINGS
KEYS = DEFAULT_SETTINGS["keys"]

def get_settings_path() -> Path:
    """Get the path to the settings file.
    
    If frozen (exe), use the executable directory.
    Otherwise, use the current working directory.
    """
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(".")
    return base_path / "settings.json"

SETTINGS_PATH = get_settings_path()


def load_settings() -> Dict:
    if SETTINGS_PATH.exists():
        try:
            with SETTINGS_PATH.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
                # Ensure defaults exist for any missing keys
                for k, v in DEFAULT_SETTINGS.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: Dict) -> None:
    with SETTINGS_PATH.open("w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2, ensure_ascii=False)


def save_highscore(new_score: int) -> None:
    """Updates highscore if new_score is greater than current record."""
    settings = load_settings()
    current_high = settings.get("highscore", 0)
    if new_score > current_high:
        settings["highscore"] = new_score
        save_settings(settings)


def save_theme(theme_name: str) -> None:
    """Updates the selected theme."""
    settings = load_settings()
    settings["theme"] = theme_name
    save_settings(settings)



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
