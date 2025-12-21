"""Screen that runs the heuristic AI autoplay and visualizes the board."""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.buttons import Button
from ui.ui_utils import tile_color, EMPTY_COLOR
from ui.animations import TileAnimator
from core.game_2048 import Game2048
from core.ai_player import choose_best_move


class HeuristicScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        self.surface = manager.surface
        self.game = Game2048()
        self.bg = (187, 173, 160)
        w, h = self.surface.get_size()
        self.back_button = Button(pygame.Rect(20, h - 60, 120, 40), "Back", lambda: manager.set_screen(__import__("ui.menu").menu.MainMenuScreen(manager)))
        self.speed = 2.0  # moves per second (x2 speed)
        self.acc = 0.0
        # Animation system
        self.animator = TileAnimator(duration_ms=200)  # Slightly faster animations for autoplay

    def handle_event(self, event):
        self.back_button.handle_event(event)

    def update(self):
        # Update animations
        dt_ms = 1000 / 60.0  # ~16.67ms per frame
        self.animator.update(dt_ms)
        
        # move based on speed (only if not animating)
        if not self.animator.is_animating():
            dt = 1 / 60.0
            self.acc += dt
            if self.acc >= 1.0 / max(0.01, self.speed):
                move = choose_best_move(self.game)
                if move:
                    # Capture old board state
                    old_board = [row[:] for row in self.game.board]
                    # Make the move
                    moved = self.game.move(move)
                    # Start animation if move was successful
                    if moved:
                        self.animator.start_move_animation(old_board, self.game.board, move)
                self.acc = 0.0

    def draw(self):
        surf = self.surface
        surf.fill(self.bg)
        
        # Draw board grid (empty cells)
        size = self.game.size
        cell = 100
        margin = 10
        for r in range(size):
            for c in range(size):
                x = margin + c * (cell + margin)
                y = margin + r * (cell + margin)
                pygame.draw.rect(surf, EMPTY_COLOR, (x, y, cell, cell), border_radius=6)
        
        # Draw animated tiles
        if self.animator.is_animating():
            tiles_to_render = self.animator.get_render_tiles(cell, margin)
            
            for tile_data in tiles_to_render:
                val = tile_data['value']
                x = tile_data['x']
                y = tile_data['y']
                scale = tile_data['scale']
                alpha = tile_data['alpha']
                
                # Calculate scaled size
                scaled_size = cell * scale
                offset = (cell - scaled_size) / 2
                
                # Draw tile
                color = tile_color(val)
                # Create surface for alpha blending
                tile_surf = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
                pygame.draw.rect(tile_surf, (*color, alpha), (0, 0, scaled_size, scaled_size), border_radius=6)
                
                # Draw number
                if val and alpha > 50:
                    font = pygame.font.SysFont(None, int(28 * scale))
                    txt = font.render(str(val), True, (0, 0, 0))
                    txt_rect = txt.get_rect(center=(scaled_size/2, scaled_size/2))
                    tile_surf.blit(txt, txt_rect)
                surf.blit(tile_surf, (x + offset, y + offset))
        else:
            # Static rendering when not animating
            for r in range(size):
                for c in range(size):
                    x = margin + c * (cell + margin)
                    y = margin + r * (cell + margin)
                    val = self.game.board[r][c]
                    if val:
                        color = tile_color(val)
                        pygame.draw.rect(surf, color, (x, y, cell, cell), border_radius=6)
                        font = pygame.font.SysFont(None, 28)
                        txt = font.render(str(val), True, (0, 0, 0))
                        surf.blit(txt, txt.get_rect(center=(x + cell / 2, y + cell / 2)))

        # score
        font = pygame.font.SysFont(None, 24)
        score_s = font.render(f"Score: {self.game.score}", True, (0, 0, 0))
        surf.blit(score_s, (20, surf.get_height() - 100))
        self.back_button.draw(surf)
