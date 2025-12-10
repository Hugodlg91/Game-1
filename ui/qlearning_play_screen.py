"""Play using a learned Q-table visually."""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.buttons import Button
import q_learning_agent
from game_2048 import Game2048


class QLearningPlayScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        self.surface = manager.surface
        self.bg = (187, 173, 160)
        w, h = self.surface.get_size()
        self.back_button = Button(pygame.Rect(20, h - 60, 120, 40), "Back", lambda: manager.set_screen(__import__("ui.menu").menu.MainMenuScreen(manager)))
        self.qtable = q_learning_agent.load_qtable()
        self.game = Game2048()
        self.paused = False

    def handle_event(self, event):
        self.back_button.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused

    def update(self):
        if not self.paused and q_learning_agent.QFILE.exists() and self.game.has_moves_available():
            action = q_learning_agent.choose_action_from_q(self.game, self.qtable)
            if action:
                self.game.move(action)

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

        font = pygame.font.SysFont(None, 24)
        surf.blit(font.render(f"Score: {self.game.score}", True, (0, 0, 0)), (20, surf.get_height() - 100))
        self.back_button.draw(surf)
