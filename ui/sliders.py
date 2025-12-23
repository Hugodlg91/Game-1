"""UI Slider components."""
from __future__ import annotations
import pygame
from ui.ui_utils import get_font

class VerticalSlider:
    def __init__(self, rect: pygame.Rect, value: float, color_fill=(50, 200, 50), color_bg=(30, 30, 30)):
        self.rect = rect
        self.value = max(0.0, min(1.0, value))  # 0.0 to 1.0
        self.color_fill = color_fill
        self.color_bg = color_bg
        self.dragging = False
        self.hovered = False

    def handle_event(self, event) -> bool:
        """
        Handle mouse events. Returns True if value changed.
        """
        changed = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value(event.pos[1])
                changed = True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.hovered = True
            else:
                self.hovered = False
                
            if self.dragging:
                self._update_value(event.pos[1])
                changed = True
                
        return changed

    def _update_value(self, mouse_y):
        """Calculate value based on mouse Y position (bottom is 0.0, top is 1.0)."""
        # Relative Y from top of rect
        rel_y = mouse_y - self.rect.y
        # Clamp
        rel_y = max(0, min(self.rect.height, rel_y))
        
        # Invert because top is low Y, but we want top = 1.0
        # filled_height = (1.0 - value) * height -> NO
        # value 1.0 -> rel_y 0
        # value 0.0 -> rel_y height
        
        self.value = 1.0 - (rel_y / self.rect.height)

    def draw(self, surface):
        # Draw background track
        pygame.draw.rect(surface, self.color_bg, self.rect)
        pygame.draw.rect(surface, (60, 60, 60), self.rect, 2)
        
        # Calculate filled height
        filled_h = int(self.rect.height * self.value)
        
        # Fill rect (bottom up)
        fill_rect = pygame.Rect(
            self.rect.x, 
            self.rect.bottom - filled_h, 
            self.rect.width, 
            filled_h
        )
        
        # Dynamic color based on value or hover
        col = self.color_fill
        if self.hovered or self.dragging:
            # Highlight slightly
            col = (min(255, col[0]+30), min(255, col[1]+30), min(255, col[2]+30))
            
        pygame.draw.rect(surface, col, fill_rect)
        
        # Optional: Draw a "handle" line at the top of the fill
        handle_y = self.rect.bottom - filled_h
        pygame.draw.line(surface, (255, 255, 255), (self.rect.x, handle_y), (self.rect.right, handle_y), 2)
