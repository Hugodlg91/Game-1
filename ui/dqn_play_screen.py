"""Play using a trained DQN model visually."""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.buttons import Button
from ui.ui_utils import tile_color, EMPTY_COLOR
from ui.animations import TileAnimator
import dqn_agent
from game_2048 import Game2048
from pathlib import Path


class DQNPlayScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        self.surface = manager.surface
        self.bg = (187, 173, 160)
        w, h = self.surface.get_size()
        self.back_button = Button(pygame.Rect(20, h - 60, 120, 40), "Back", lambda: manager.set_screen(__import__("ui.menu").menu.MainMenuScreen(manager)))
        
        # Load DQN agent
        self.agent = dqn_agent.DQNAgent()
        model_path = Path("dqn_checkpoints/dqn_final.pth")
        
        if model_path.exists():
            try:
                self.agent.load(str(model_path))
                self.model_loaded = True
            except Exception as e:
                print(f"Error loading DQN model: {e}")
                self.model_loaded = False
        else:
            self.model_loaded = False
        
        self.game = Game2048()
        self.paused = False
        self.speed = 2.0  # moves per second
        self.acc = 0.0
        
        # Animation system
        self.animator = TileAnimator(duration_ms=200)

    def handle_event(self, event):
        self.back_button.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused

    def update(self):
        # Update animations
        dt_ms = 1000 / 60.0
        self.animator.update(dt_ms)
        
        # Make moves (only if not animating)
        if not self.paused and self.model_loaded and not self.animator.is_animating():
            if self.game.has_moves_available():
                dt = 1 / 60.0
                self.acc += dt
                if self.acc >= 1.0 / max(0.01, self.speed):
                    # Get action from DQN
                    action = dqn_agent.choose_action_from_dqn(self.game, self.agent)
                    if action:
                        # Capture old board
                        old_board = [row[:] for row in self.game.board]
                        # Make move
                        moved = self.game.move(action)
                        # Animate
                        if moved:
                            self.animator.start_move_animation(old_board, self.game.board, action)
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
                
                scaled_size = cell * scale
                offset = (cell - scaled_size) / 2
                
                color = tile_color(val)
                tile_surf = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
                pygame.draw.rect(tile_surf, (*color, alpha), (0, 0, scaled_size, scaled_size), border_radius=6)
                
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

        # Status text
        font = pygame.font.SysFont(None, 24)
        
        if not self.model_loaded:
            error_text = font.render("No trained model found!", True, (255, 0, 0))
            surf.blit(error_text, (20, surf.get_height() - 140))
            help_text = font.render("Train a model first (DQN: Train)", True, (0, 0, 0))
            surf.blit(help_text, (20, surf.get_height() - 115))
        
        score_text = font.render(f"Score: {self.game.score}", True, (0, 0, 0))
        surf.blit(score_text, (20, surf.get_height() - 100))
        
        pause_text = font.render("SPACE: Pause/Resume", True, (100, 100, 100))
        surf.blit(pause_text, (surf.get_width() - 220, surf.get_height() - 100))
        
        self.back_button.draw(surf)
