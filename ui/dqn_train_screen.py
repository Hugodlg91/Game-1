"""Visual DQN trainer screen.

Runs training incrementally via dqn_agent.DQNTrainer (one step per update).
"""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.buttons import Button
from ui.ui_utils import tile_color, EMPTY_COLOR
from game_2048 import Game2048
import dqn_agent


class DQNTrainScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        self.surface = manager.surface
        self.bg = (187, 173, 160)
        w, h = self.surface.get_size()
        self.back_button = Button(pygame.Rect(20, h - 60, 120, 40), "Back", lambda: manager.set_screen(__import__("ui.menu").menu.MainMenuScreen(manager)))
        self.trainer = dqn_agent.DQNTrainer(episodes=1000, batch_size=64)
        self.paused = False
        self.speed = 1  # steps per frame

    def handle_event(self, event):
        self.back_button.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused
            elif event.key == pygame.K_UP:
                self.speed = min(10, self.speed + 1)
            elif event.key == pygame.K_DOWN:
                self.speed = max(1, self.speed - 1)

    def update(self):
        if not self.paused:
            for _ in range(self.speed):
                done = self.trainer.step()
                if done:
                    break

    def draw(self):
        surf = self.surface
        surf.fill(self.bg)
        # show trainer stats
        font = pygame.font.SysFont(None, 24)
        stats = self.trainer.status()
        lines = [
            f"Episode: {stats['episode']}/{stats['episodes']}", 
            f"Step: {stats['step']}", 
            f"ε={stats['epsilon']:.3f}", 
            f"Memory: {stats['memory_size']}",
            f"Avg Score: {stats['avg_score']:.1f}",
            f"Avg Max Tile: {stats['avg_max_tile']:.0f}",
            "",
            "Controls:",
            "SPACE: Pause/Resume",
            "UP/DOWN: Speed ±1",
            f"Speed: {self.speed}x"
        ]
        for i, line in enumerate(lines):
            surf.blit(font.render(line, True, (0, 0, 0)), (20, 20 + i * 26))

        # draw current board from trainer
        board = self.trainer.current_board()
        size = len(board)
        cell = 60
        margin = 8
        base_x = 20
        base_y = 350
        for r in range(size):
            for c in range(size):
                x = base_x + c * (cell + margin)
                y = base_y + r * (cell + margin)
                val = board[r][c]
                color = EMPTY_COLOR if val == 0 else tile_color(val)
                pygame.draw.rect(surf, color, (x, y, cell, cell), border_radius=6)
                if val:
                    txt = font.render(str(val), True, (0, 0, 0))
                    surf.blit(txt, txt.get_rect(center=(x + cell / 2, y + cell / 2)))

        self.back_button.draw(surf)
