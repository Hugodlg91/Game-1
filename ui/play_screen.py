"""Play screen for manual gameplay using Game2048."""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.buttons import Button
from ui.ui_utils import tile_color, EMPTY_COLOR
from ui.animations import TileAnimator
from game_2048 import Game2048
from settings import load_settings


class PlayScreen(Screen):
    def __init__(self, manager):
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
        
        # Draw Procedural Arrow Icon (Smoother version)
        icon_color = (60, 60, 60)
        arrow_radius = 12
        
        # Draw Arc (nearly full circle)
        # We'll use multiple line segments for smoother look or pygame.draw.arc
        rect = pygame.Rect(center_x - arrow_radius, center_y - arrow_radius, arrow_radius * 2, arrow_radius * 2)
        import math
        start_angle = 0
        end_angle = 1.5 * math.pi # 270 degrees
        
        pygame.draw.arc(surf, icon_color, rect, start_angle, end_angle, 3)
        
        # Draw Arrow Head - Adjusted for correct tangent
        # The arc ends at angle 0 (3 o'clock position on standard circle math, but pygame handles rects)
        # Pygame arc angles: 0 is East, pi/2 is North.
        # We drew from 0 to 1.5pi (East -> North -> West -> South)
        # So the end is at South (1.5pi, 270 deg) ??
        # Wait, pygame arc coordinate system: 0 is right, pi/2 is top, pi is left, 3pi/2 is bottom.
        # We want a clockwise arrow. 
        # Let's draw it manually with points for perfect control.

        points = []
        steps = 30
        for i in range(steps):
             # Angle goes from -45 deg to 225 deg (clockwise visual)
             # In radians: -pi/4 to 5pi/4
             angle = -math.pi/4 + (i / (steps-1)) * (1.5 * math.pi)
             # Invert Y for screen coords
             px = center_x + math.cos(angle) * arrow_radius
             py = center_y - math.sin(angle) * arrow_radius
             points.append((px, py))

        if len(points) > 1:
            pygame.draw.lines(surf, icon_color, False, points, 3)

        # Arrow head at the end of the arc
        # End angle is roughly 225 deg (5pi/4)
        end_angle = -math.pi/4 + 1.5 * math.pi
        px = center_x + math.cos(end_angle) * arrow_radius
        py = center_y - math.sin(end_angle) * arrow_radius
        
        # Tangent direction is perpendicular to radius
        # vector is (-sin(a), -cos(a))
        tx = -math.sin(end_angle)
        ty = -math.cos(end_angle)
        
        # Arrow head points
        head_size = 7
        # Tip is at (px, py)
        tip = (px + tx * 2, py - ty * 2) # Slight offset forward
        
        # Back points rotated +150 and -150 degrees from tangent
        angle_tangent = math.atan2(-ty, tx) # Note flipped Y for screen
        
        left_wing_angle = angle_tangent + math.radians(150)
        right_wing_angle = angle_tangent - math.radians(150)
        
        p_left = (
            px + math.cos(left_wing_angle) * head_size,
            py - math.sin(left_wing_angle) * head_size
        )
        p_right = (
            px + math.cos(right_wing_angle) * head_size,
            py - math.sin(right_wing_angle) * head_size
        )
        
        pygame.draw.polygon(surf, icon_color, [tip, p_left, p_right])
