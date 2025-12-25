"""Simple clickable button UI component for Pygame."""
from __future__ import annotations

import pygame
from typing import Callable, Tuple, Optional
from ui.ui_utils import get_font

class Button:
    def __init__(self, rect: pygame.Rect, text: str, on_click: Callable[[], None],
                 bg: Tuple[int, int, int] = (200, 200, 200), fg=(0, 0, 0),
                 icon: Optional[pygame.Surface] = None, font_size: int = 45):
        self.rect = rect
        self.text = text
        self.on_click = on_click
        self.bg = bg
        self.fg = fg
        self.hover = False
        self.icon = icon
        self.icon = icon
        self.initial_font_size = font_size
        
        # Use Pixel Font
        # Auto-scale text to fit
        self._calculate_font()
        
        # Style properties for external customization (e.g. from Menu)
        self.bg_color = bg
        self.text_color = fg
        self.border_radius = 0 # PIXEL ART = SQUARE

    def resize(self, new_rect: pygame.Rect):
        """Update button geometry and re-calculate font scaling."""
        self.rect = new_rect
        self._calculate_font()

    def _calculate_font(self):
        """Re-calculate font size to fit current rect."""
        # If rect is too small/invalid (e.g. initialization 0,0,0,0), skip or use default
        if self.rect.width < 10:
            # Use requested size without scaling context
            try:
                self.font = get_font(self.initial_font_size)
            except:
                self.font = pygame.font.SysFont(None, self.initial_font_size)
            return

        current_size = self.initial_font_size
        while current_size > 10:
            try:
                self.font = get_font(current_size)
            except:
                self.font = pygame.font.SysFont(None, current_size)
            
            txt_w = self.font.size(self.text)[0]
            if txt_w < self.rect.width - 20: # 20px padding
                break
            current_size -= 2

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            prev_hover = self.hover
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                try:
                    self.on_click()
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"Error clicking button {self.text}: {e}")

    def draw(self, surface: pygame.Surface) -> None:
        # Determine current color
        current_bg = self.bg_color if hasattr(self, 'bg_color') else self.bg
        current_fg = self.text_color if hasattr(self, 'text_color') else self.fg
        
        draw_color = current_bg
        if self.hover:
            # Simple brighten effect
            draw_color = tuple(min(255, c + 30) for c in current_bg)
            
        pygame.draw.rect(surface, draw_color, self.rect, border_radius=self.border_radius)
        
        # Border
        border_col = (0, 0, 0)
        pygame.draw.rect(surface, border_col, self.rect, 3, border_radius=self.border_radius)
        
        # Content (Icon or Text)
        if self.icon:
            # Center icon
            # Start with original icon size
            icon_w = self.icon.get_width()
            icon_h = self.icon.get_height()
            
            # If icon larger than button, scale down
            max_h = self.rect.height - 10
            if icon_h > max_h:
                scale = max_h / icon_h
                render_w = int(icon_w * scale)
                render_h = int(icon_h * scale)
                final_icon = pygame.transform.scale(self.icon, (render_w, render_h))
            else:
                final_icon = self.icon
            
            icon_rect = final_icon.get_rect(center=self.rect.center)
            surface.blit(final_icon, icon_rect)
        else:
            # Text
            text_surf = self.font.render(self.text, False, current_fg)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
