"""Graphical main menu screen."""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.buttons import Button
from ui.play_screen import PlayScreen
from ui.heuristic_screen import HeuristicScreen
from ui.expectimax_screen import ExpectimaxScreen
from ui.settings_screen import SettingsScreen


class MainMenuScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        w, h = manager.surface.get_size()
        self.bg = (187, 173, 160)
        btn_w, btn_h = 300, 50
        cx = w // 2 - btn_w // 2
        start_y = 120  # Adjusted for more buttons
        gap = 12
        self.buttons = []

        def mk(text, action, idx):
            rect = pygame.Rect(cx, start_y + idx * (btn_h + gap), btn_w, btn_h)
            return Button(rect, text, action, bg=(220, 180, 120))

        self.buttons.append(mk("Play (manual)", lambda: manager.set_screen(PlayScreen(manager)), 0))
        self.buttons.append(mk("Autoplay (Heuristic AI)", lambda: manager.set_screen(HeuristicScreen(manager)), 1))
        self.buttons.append(mk("Autoplay (Expectimax)", lambda: manager.set_screen(ExpectimaxScreen(manager)), 2))
        self.buttons.append(mk("Settings", lambda: manager.set_screen(SettingsScreen(manager)), 3))
        self.buttons.append(mk("Quit", lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)), 4))

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def update(self):
        pass

    def draw(self):
        surf = self.manager.surface
        surf.fill(self.bg)
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("2048", True, (50, 30, 20))
        surf.blit(title, title.get_rect(center=(surf.get_width() // 2, 60)))
        for b in self.buttons:
            b.draw(surf)
