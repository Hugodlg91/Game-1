"""Play screen for manual gameplay using Game2048."""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.buttons import Button
from ui.ui_utils import tile_color, EMPTY_COLOR
from ui.animations import TileAnimator
from core.game_2048 import Game2048
from core.settings import *
load_settings


class PlayScreen(Screen):
    def __init__(self1, manager):
        super().__init__(manager)
        self.surface = manager.surface
        self.game = Game2048()
        self.bg = (187, 173, 160)
        w, h = self.surface.get_size()
        
        # Back button - return to main menu
        self.back_button = Button(
            pygame.Rect(20, h - 60, 120, 40), 
            "Back", 
            lambda: manager.set_screen(__import__("ui.menu").menu.MainMenuScreen(manager))
        )
        
        # Reset button with icon - circular design
        button_size = 55
        self.reset_button_pos = (w - 80, h - 75)
        self.reset_button_radius = button_size // 2
        self.reset_button_hover = False
        
        # Load reset icon
        try:
            import os
            icon_path = os.path.join(os.path.dirname(__file__), 'reset_icon.png')
            self.reset_icon = pygame.image.load(icon_path).convert_alpha()
            # Resize (scale avoids blurring for pixel art, but for this double arrow maybe smoothscale is better? 
            # Let's stick to smoothscale as it looks like a high-res vector conversion)
            self.reset_icon = pygame.transform.smoothscale(self.reset_icon, (24, 24))
            # Make white background transparent if it exists (safety check)
            self.reset_icon.set_colorkey((255, 255, 255))
        except Exception as e:
            print(f"Failed to load reset icon: {e}")
            self.reset_icon = None
        
        # load keys
        settings = load_settings()
        self.keymap = settings.get("keys", {"up": "w", "down": "s", "left": "a", "right": "d"})
        # Animation system
        self.animator = TileAnimator(duration_ms=250)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            # map key name to direction
            inv = {v: k for k, v in self.keymap.items()}
            if key_name in inv and not self.animator.is_animating():
                direction = inv[key_name]
                # Capture old board state
                old_board = [row[:] for row in self.game.board]
                # Make the move
                moved = self.game.move(direction)
                # Start animation if move was successful
                if moved:
                    self.animator.start_move_animation(old_board, self.game.board, direction)
        
        # Handle reset button (circular)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            dx = mx - (self.reset_button_pos[0] + self.reset_button_radius)
            dy = my - (self.reset_button_pos[1] + self.reset_button_radius)
            if dx*dx + dy*dy <= self.reset_button_radius*self.reset_button_radius:
                self.manager.set_screen(PlayScreen(self.manager))
        
        # Handle hover for reset button
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            dx = mx - (self.reset_button_pos[0] + self.reset_button_radius)
            dy = my - (self.reset_button_pos[1] + self.reset_button_radius)
            self.reset_button_hover = dx*dx + dy*dy <= self.reset_button_radius*self.reset_button_radius
        
        self.back_button.handle_event(event)

    def update(self):
        # Update animations (~16.67ms per frame at 60 FPS)
        self.animator.update(1000 / 60)

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
        
        # Draw circular reset button with shadow and hover effect
        center_x = self.reset_button_pos[0] + self.reset_button_radius
        center_y = self.reset_button_pos[1] + self.reset_button_radius
        
        # Shadow
        shadow_offset = 3
        pygame.draw.circle(surf, (140, 130, 120), 
                          (center_x + shadow_offset, center_y + shadow_offset), 
                          self.reset_button_radius)
        
        # Button background with hover effect
        if self.reset_button_hover:
            button_color = (220, 210, 200)  # Lighter on hover
        else:
            button_color = (205, 193, 180)  # Same as empty tile
        
        pygame.draw.circle(surf, button_color, (center_x, center_y), self.reset_button_radius)
        
        # Border
        pygame.draw.circle(surf, (160, 150, 140), (center_x, center_y), self.reset_button_radius, 2)
        
        # Draw Icon
        if self.reset_icon:
            icon_rect = self.reset_icon.get_rect(center=(center_x, center_y))
            surf.blit(self.reset_icon, icon_rect)
