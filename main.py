"""Entry point for the graphical 2048 application.

Starts Pygame and shows the main menu screen.
"""
from __future__ import annotations

import pygame
import os
from ui.screens import ScreenManager
from ui.menu import MainMenuScreen
from ui.ui_utils import resource_path
from ui.sound_manager import SoundManager
from core.settings import load_settings


def main() -> None:
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
    
    # Initialize Screen (Resizable)
    screen = pygame.display.set_mode((900, 1000), pygame.RESIZABLE)
    pygame.display.set_caption("Power 11 - The Ultimate 2048")
    
    # Initialize Sound Manager with volumes from settings
    sound_manager = SoundManager(
        music_volume=settings.get('music_volume', 0.1),
        sfx_volume=settings.get('sfx_volume', 1.0),
        music_muted=settings.get('music_muted', False),
        sfx_muted=settings.get('sfx_muted', False)
    )
    
    manager = ScreenManager(screen)
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
                # Screen manager handles resizing via draw() using current surface size
                pass
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
            
            manager.handle_event(event)

        manager.update()
        manager.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
