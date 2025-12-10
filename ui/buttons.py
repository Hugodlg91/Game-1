"""Simple clickable button UI component for Pygame."""
from __future__ import annotations

import pygame
from typing import Callable, Tuple


class Button:
    def __init__(self, rect: pygame.Rect, text: str, on_click: Callable[[], None],
                 bg: Tuple[int, int, int] = (200, 200, 200), fg=(0, 0, 0)):
        self.rect = rect
        self.text = text
        self.on_click = on_click
        self.bg = bg
        self.fg = fg
        self.hover = False
        self.font = pygame.font.SysFont(None, 28)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                try:
                    self.on_click()
                except Exception:
                    pass

    def draw(self, surface: pygame.Surface) -> None:
        color = tuple(min(255, c + 20) for c in self.bg) if self.hover else self.bg
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        # border
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2, border_radius=8)
        # text
        text_surf = self.font.render(self.text, True, self.fg)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
