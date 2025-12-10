"""
Pygame-based interactive frontend for the 2048 game.

Run with:
    python game_2048_pygame.py

Controls: arrow keys or W/A/S/D to move, R to restart, Esc or close window to quit.
"""
from __future__ import annotations

import random
import sys
import pygame
from typing import Tuple

from game_2048 import Game2048


CELL_SIZE = 100
MARGIN = 10
FONT_SIZE = 36
BG_COLOR = (187, 173, 160)
EMPTY_COLOR = (205, 193, 180)
TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}


def tile_color(value: int) -> Tuple[int, int, int]:
    return TILE_COLORS.get(value, (60, 58, 50))


class Pygame2048:
    def __init__(self, size: int = 4, seed: int | None = None):
        pygame.init()
        self.size = size
        self.cell = CELL_SIZE
        self.margin = MARGIN
        self.width = size * self.cell + (size + 1) * self.margin
        self.height = self.width + 80
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("2048")
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.small_font = pygame.font.SysFont(None, 20)
        self.clock = pygame.time.Clock()

        self.rng_seed = seed
        self.reset_game()

    def reset_game(self) -> None:
        rng = random.Random(self.rng_seed) if self.rng_seed is not None else random.Random()
        self.game = Game2048(size=self.size, rng=rng)

    def draw(self) -> None:
        self.screen.fill(BG_COLOR)
        # draw grid background
        for row in range(self.size):
            for col in range(self.size):
                x = self.margin + col * (self.cell + self.margin)
                y = self.margin + row * (self.cell + self.margin)
                value = self.game.board[row][col]
                color = EMPTY_COLOR if value == 0 else tile_color(value)
                pygame.draw.rect(self.screen, color, (x, y, self.cell, self.cell), border_radius=6)
                if value:
                    text = self.font.render(str(value), True, (0, 0, 0))
                    txt_rect = text.get_rect(center=(x + self.cell / 2, y + self.cell / 2))
                    self.screen.blit(text, txt_rect)

        # score and hints
        score_text = self.small_font.render(f"Score: {self.game.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (self.margin, self.width + 10))
        hint_text = self.small_font.render("Arrows or W/A/S/D to move — R to restart — Esc to quit", True, (0, 0, 0))
        self.screen.blit(hint_text, (self.margin, self.width + 35))

        if self.game.has_won():
            win_surf = self.font.render("You reached 2048!", True, (0, 0, 0))
            self.screen.blit(win_surf, (self.margin, self.width + 10))

        if not self.game.has_moves_available():
            over_surf = self.font.render("Game Over", True, (200, 0, 0))
            rect = over_surf.get_rect(center=(self.width / 2, self.width / 2))
            self.screen.blit(over_surf, rect)

        pygame.display.flip()

    def handle_key(self, key) -> None:
        mapping = {
            pygame.K_UP: "up",
            pygame.K_w: "up",
            pygame.K_DOWN: "down",
            pygame.K_s: "down",
            pygame.K_LEFT: "left",
            pygame.K_a: "left",
            pygame.K_RIGHT: "right",
            pygame.K_d: "right",
        }
        if key in mapping:
            _ = self.game.move(mapping[key])

    def run(self) -> None:
        running = True
        while running:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset_game()
                    else:
                        self.handle_key(event.key)

            self.draw()

        pygame.quit()


def main() -> None:
    size = 4
    seed = None
    app = Pygame2048(size=size, seed=seed)
    app.run()


if __name__ == "__main__":
    main()
