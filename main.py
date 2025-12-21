"""Entry point for the graphical 2048 application.

Starts Pygame and shows the main menu screen.
"""
from __future__ import annotations

import pygame
import os
from ui.screens import ScreenManager
from ui.menu import MainMenuScreen
from ui.ui_utils import resource_path


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

    screen = pygame.display.set_mode((900, 1000))
    pygame.display.set_caption("2048 Ultimate")
    manager = ScreenManager(screen)
    main_menu = MainMenuScreen(manager)
    manager.set_screen(main_menu)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                manager.handle_event(event)

        manager.update()
        manager.draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
