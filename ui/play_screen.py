"""Play screen for manual gameplay using Game2048."""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.buttons import Button
from game_2048 import Game2048
from settings import load_settings


class PlayScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        self.surface = manager.surface
        self.game = Game2048()
        self.bg = (187, 173, 160)
        w, h = self.surface.get_size()
        self.back_button = Button(pygame.Rect(20, h - 60, 120, 40), "Back", lambda: manager.set_screen(manager._screen.__class__(manager)))
        # placeholder: use back to go to main menu
        self.back_action = lambda: manager.set_screen(__import__("ui.menu").menu.MainMenuScreen(manager))
        # load keys
        settings = load_settings()
        self.keymap = settings.get("keys", {"up": "w", "down": "s", "left": "a", "right": "d"})

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            # map key name to direction
            inv = {v: k for k, v in self.keymap.items()}
            if key_name in inv:
                self.game.move(inv[key_name])
        self.back_button.handle_event(event)

    def update(self):
        pass

    def draw(self):
        surf = self.surface
        surf.fill(self.bg)
        # draw board
        size = self.game.size
        cell = 100
        margin = 10
        for r in range(size):
            for c in range(size):
                x = margin + c * (cell + margin)
                y = margin + r * (cell + margin)
                val = self.game.board[r][c]
                color = (205, 193, 180) if val == 0 else (237, 207, 114)
                pygame.draw.rect(surf, color, (x, y, cell, cell), border_radius=6)
                if val:
                    font = pygame.font.SysFont(None, 28)
                    txt = font.render(str(val), True, (0, 0, 0))
                    surf.blit(txt, txt.get_rect(center=(x + cell / 2, y + cell / 2)))

        # score
        font = pygame.font.SysFont(None, 24)
        score_s = font.render(f"Score: {self.game.score}", True, (0, 0, 0))
        surf.blit(score_s, (20, surf.get_height() - 100))
        self.back_button.draw(surf)
