"""Entry point for the graphical 2048 application.

Starts Pygame and shows the main menu screen.
"""
from __future__ import annotations

import pygame
from ui.screens import ScreenManager
from ui.menu import MainMenuScreen


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((600, 700))
    pygame.display.set_caption("2048")
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
