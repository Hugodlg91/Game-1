"""Graphical settings screen for keybindings and training speed."""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.buttons import Button
from settings import load_settings, save_settings


class SettingsScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        self.surface = manager.surface
        self.bg = (187, 173, 160)
        w, h = self.surface.get_size()
        self.back_button = Button(pygame.Rect(20, h - 60, 120, 40), "Back", lambda: manager.set_screen(__import__("ui.menu").menu.MainMenuScreen(manager)))
        self.settings = load_settings()
        self.listening = None

    def handle_event(self, event):
        self.back_button.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # simple regions for keys
            x, y = event.pos
            # map areas for up/down/left/right display
            base_x = 200
            base_y = 150
            if base_x < x < base_x + 200:
                if base_y < y < base_y + 30:
                    self.listening = "up"
                elif base_y + 40 < y < base_y + 70:
                    self.listening = "down"
                elif base_y + 80 < y < base_y + 110:
                    self.listening = "left"
                elif base_y + 120 < y < base_y + 150:
                    self.listening = "right"
        elif event.type == pygame.KEYDOWN and self.listening:
            key_name = pygame.key.name(event.key)
            self.settings.setdefault("keys", {})[self.listening] = key_name
            save_settings(self.settings)
            self.listening = None

    def update(self):
        pass

    def draw(self):
        surf = self.surface
        surf.fill(self.bg)
        font = pygame.font.SysFont(None, 28)
        surf.blit(font.render("Settings - Click a field then press a key", True, (0, 0, 0)), (20, 20))
        keys = self.settings.get("keys", {})
        base_x = 200
        base_y = 150
        surf.blit(font.render(f"Up: {keys.get('up','w')}", True, (0, 0, 0)), (base_x, base_y))
        surf.blit(font.render(f"Down: {keys.get('down','s')}", True, (0, 0, 0)), (base_x, base_y + 40))
        surf.blit(font.render(f"Left: {keys.get('left','a')}", True, (0, 0, 0)), (base_x, base_y + 80))
        surf.blit(font.render(f"Right: {keys.get('right','d')}", True, (0, 0, 0)), (base_x, base_y + 120))
        if self.listening:
            surf.blit(font.render(f"Press a key for {self.listening}", True, (200, 0, 0)), (20, 60))
        self.back_button.draw(surf)
