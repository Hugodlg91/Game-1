"""Shared UI utilities for the 2048 game.

Contains color constants and helper functions for rendering game tiles.
"""
from __future__ import annotations
from typing import Tuple


# Color constants
BG_COLOR = (187, 173, 160)
EMPTY_COLOR = (205, 193, 180)
TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}


def tile_color(value: int) -> Tuple[int, int, int]:
    """Return the color for a tile with the given value.
    
    Args:
        value: The tile value (2, 4, 8, 16, etc.)
        
    Returns:
        RGB color tuple for the tile
    """

    return TILE_COLORS.get(value, (60, 58, 50))


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller.
    
    Args:
        relative_path: Relative path to the resource (e.g. 'game_icon.png')
        
    Returns:
        Absolute path to the resource
    """
    import sys
    import os
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
