"""Screen that runs the heuristic AI autoplay and visualizes the board."""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.buttons import Button
from ui.ui_utils import tile_color, EMPTY_COLOR
from game_2048 import Game2048
import ai_player


class HeuristicScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        self.surface = manager.surface
        self.game = Game2048()
        self.bg = (187, 173, 160)
        w, h = self.surface.get_size()
        self.back_button = Button(pygame.Rect(20, h - 60, 120, 40), "Back", lambda: manager.set_screen(__import__("ui.menu").menu.MainMenuScreen(manager)))
        self.speed = 1.0  # moves per second
        self.acc = 0.0

    def handle_event(self, event):
        self.back_button.handle_event(event)

    def update(self):
        # move based on speed
        dt = 1 / 60.0
        self.acc += dt
        if self.acc >= 1.0 / max(0.01, self.speed):
            move = ai_player.choose_best_move(self.game)
            if move:
                self.game.move(move)
            self.acc = 0.0

    def draw(self):
        surf = self.surface
        surf.fill(self.bg)
        # draw board simple
        size = self.game.size
        cell = 100
        margin = 10
        for r in range(size):
            for c in range(size):
                x = margin + c * (cell + margin)
                y = margin + r * (cell + margin)
                val = self.game.board[r][c]
                color = EMPTY_COLOR if val == 0 else tile_color(val)
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
