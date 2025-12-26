"""Entry point for the graphical 2048 application.

Starts Pygame and shows the main menu screen.
"""

import pygame
import os
from ui.screens import ScreenManager
from ui.menu import MainMenuScreen
from ui.ui_utils import resource_path
from ui.sound_manager import SoundManager
from core.settings import load_settings
from core.display_manager import DisplayManager


def main() -> None:
    # Fix High DPI scaling on Windows
    import ctypes
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

    pygame.init()

    # Set window icon
    icon_path = resource_path("assets/game_icon.png")
    if os.path.exists(icon_path):
        try:
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")

    # Load settings first to get resolution
    settings = load_settings()
    
    # Initialize Display Manager
    # Internal Logic is now 3840x2160 (4K)
    display_manager = DisplayManager((1280, 720), virtual_width=3840, virtual_height=2160)
    pygame.display.set_caption("Power 11 - The Ultimate 2048")
    
    # Initialize Sound Manager with volumes from settings
    sound_manager = SoundManager(
        music_volume=settings.get('music_volume', 0.1),
        sfx_volume=settings.get('sfx_volume', 1.0),
        music_muted=settings.get('music_muted', False),
        sfx_muted=settings.get('sfx_muted', False)
    )
    
    # Pass the VIRTUAL surface to the ScreenManager
    manager = ScreenManager(display_manager.virtual_surface)
    manager.sound_manager = sound_manager  # Attach for access in screens
    main_menu = MainMenuScreen(manager)
    manager.set_screen(main_menu)

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60)
        
        # Event Loop
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                display_manager.resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
            
            # Helper for converting mouse events to virtual coordinates
            event = display_manager.convert_event(event)
            
            manager.handle_event(event)

        manager.update()
        
        # Draw everything to the virtual surface
        manager.draw() 
        
        # Scale and render to real screen
        display_manager.draw()

    pygame.quit()


if __name__ == "__main__":
    main()
