"""UI utility functions for Power 11 (Pixel Art Edition).

Centralizes theme definitions, font loading, and resource management.
"""
import pygame
import os
import sys

# --- 1. FONTS ---
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_font(size: int) -> pygame.font.Font:
    """Load the project's pixel art font (PressStart2P).
    
    Args:
        size: Font size in pixels
    Returns:
        pygame.font.Font object or system fallback
    """
    font_path = resource_path("assets/fonts/PressStart2P.ttf")
    try:
        return pygame.font.Font(font_path, size)
    except Exception as e:
        print(f"Warning: Could not load pixel font: {e}. Using fallback.")
        return pygame.font.SysFont("arial", size, bold=True)


# --- 2. THEMES & COLORS ---
THEMES = {
    # Original 2048 adapted for retro feel
    "Classic": {
        "bg": (187, 173, 160),         # Board BG 
        "empty": (205, 193, 180),      # Empty Tile
        "header_bg": (143, 122, 102),  # Header/Button Base
        "text_dark": (119, 110, 101),  # Main Text (Dark)
        "text_light": (249, 246, 242), # Highlight Text
        "border": (119, 110, 101),     # Borders
        "tiles": {
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
        },
        "tiles_fallback": (60, 58, 50)
    },
    
    # Retro Dark Mode
    "Dark": {
        "bg": (30, 30, 30),
        "empty": (60, 60, 60),
        "header_bg": (80, 80, 80),
        "text_dark": (200, 200, 200),
        "text_light": (255, 255, 255),
        "border": (255, 255, 255),
        "tiles": {
            2: (80, 80, 90),
            4: (100, 100, 120),
            8: (120, 80, 140),
            16: (140, 60, 160),
            32: (160, 40, 180),
            64: (180, 20, 200),
            128: (200, 100, 100),
            256: (200, 80, 80),
            512: (200, 60, 60),
            1024: (220, 40, 40),
            2048: (240, 20, 20),
        },
        "tiles_fallback": (100, 100, 100)
    },
    
    # Cyberpunk / Neon
    "Cyberpunk": {
        "bg": (10, 10, 32),          # Deep Navy
        "empty": (20, 20, 60),       # Dark Blue
        "header_bg": (40, 20, 80),   # Purple
        "text_dark": (255, 255, 255), # All text white usually
        "text_light": (0, 255, 255),  # Cyan highlights
        "border": (0, 255, 255),     # Cyan borders
        "tiles": {
            2: (20, 40, 80),         # Dark Blue
            4: (30, 60, 120),
            8: (255, 0, 255),        # Magenta
            16: (200, 0, 255),
            32: (150, 0, 255),
            64: (0, 255, 255),       # Cyan
            128: (0, 200, 200),
            256: (255, 255, 0),      # Electric Yellow
            512: (255, 180, 0),
            1024: (255, 100, 0),     # Orange Neon
            2048: (255, 0, 0)        # Red Neon
        },
        "tiles_fallback": (50, 50, 50)
    }
}

def get_theme_colors(theme_name: str) -> dict:
    """Retrieve color palette for the given theme."""
    return THEMES.get(theme_name, THEMES["Classic"])

def tile_color(value: int, theme_name: str) -> tuple:
    """Get background color for a tile value."""
    theme = get_theme_colors(theme_name)
    return theme["tiles"].get(value, theme["tiles_fallback"])

def get_tile_text_info(value: int, theme_name: str) -> tuple:
    """
    Determine color and contrast for tile text.
    
    Returns:
        (text_color, is_dark_bg)
    """
    if theme_name == "Classic":
        # Classic logic: 2/4 are dark text, others white
        if value <= 4:
             return (119, 110, 101), False # Dark text
        else:
             return (249, 246, 242), True  # White text
    
    elif theme_name == "Cyberpunk":
        # Cyberpunk logic: Light Colors (Yellow/Cyan/Orange) need BLACK text.
        # Dark Colors (Blue/Magenta) need WHITE text.
        
        # Light value set: 64(Cyan), 256(Yellow), 512, 1024, 2048
        # Actually 2048 is red neon, readable with white? No, red neon is darkish.
        # Yellow (256), Cyan (64), Orange (1024) are bright.
        if value in [64, 128, 256, 512, 1024]:
             return (0, 0, 0), False # Black text
        else:
             return (255, 255, 255), True # White text (on blue/purple/magenta)
             
    else: # Dark theme
        # Mostly white text unless very bright tile
        return (255, 255, 255), True


def calculate_layout(screen_w: int, screen_h: int, grid_size: int = 4) -> dict:
    """
    Calculates dynamic layout values for a responsive centered grid.
    Returns a dict with: cell_size, margin, board_size_px, start_x, start_y, font_large, font_med, font_small
    """
    # 1. Determine available space (keep 75% of smallest dimension)
    min_dim = min(screen_w, screen_h)
    board_px_target = int(min_dim * 0.75)
    
    # 2. Derive cell size and margin
    # Formula: board_px = grid_size * cell + (grid_size + 1) * margin
    # We define margin = 0.1 * cell_size
    # board_px = grid_size * cell + (grid_size + 1) * 0.1 * cell
    # board_px = cell * (grid_size + 0.1 * (grid_size + 1))
    
    factor = grid_size + 0.1 * (grid_size + 1)
    cell_size = int(board_px_target / factor)
    margin = int(cell_size * 0.1)
    
    # Recalculate exact board size to avoid float gaps
    real_board_px = grid_size * (cell_size + margin) + margin
    
    # 3. Offsets for centering
    start_x = (screen_w - real_board_px) // 2
    start_y = (screen_h - real_board_px) // 2
    
    # 4. Font Sizes (proportional to cell size)
    f_large = int(cell_size * 0.45) # Value < 100
    f_med = int(cell_size * 0.35)   # Value < 1000
    f_small = int(cell_size * 0.25) # Value >= 1000
    
    return {
        "cell_size": cell_size,
        "margin": margin,
        "board_size_px": real_board_px,
        "start_x": start_x,
        "center_y": start_y,  # NOTE: We often want to shift up/down for header, but this is the pure center
        "font_large": f_large,
        "font_med": f_med, 
        "font_small": f_small
    }
