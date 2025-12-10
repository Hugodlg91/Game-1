"""Screen manager and base classes for UI screens."""
from __future__ import annotations

import pygame
from typing import Optional


class Screen:
    def __init__(self, manager: "ScreenManager") -> None:
        self.manager = manager

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self) -> None:
        pass

    def draw(self) -> None:
        pass


class ScreenManager:
    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface
        self._screen: Optional[Screen] = None

    def set_screen(self, screen: Screen) -> None:
        self._screen = screen

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._screen:
            self._screen.handle_event(event)

    def update(self) -> None:
        if self._screen:
            self._screen.update()

    def draw(self) -> None:
        if self._screen:
            self._screen.draw()
