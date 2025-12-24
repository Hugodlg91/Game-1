"""Main Menu Screen."""
import pygame
import os
from ui.screens import Screen
from ui.buttons import Button
from ui.ui_utils import get_font, get_theme_colors, resource_path
from core.settings import load_settings


class MainMenuScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        self.settings = load_settings()
        self.theme_name = self.settings.get("theme", "Classic")
        self.theme_colors = get_theme_colors(self.theme_name)
        self.bg = self.theme_colors["bg"]
        
        # We don't init buttons here with fixed size anymore, we do it in draw() or update()
        # But buttons need state. So we init them with dummy rects and update them in draw.
        
        # --- Buttons ---
        # 1. Play Manual
        self.btn_play = Button(pygame.Rect(0,0,0,0), "PLAY MANUAL", 
                               lambda: manager.set_screen(__import__("ui.play_screen").play_screen.PlayScreen(manager)))
        # 2. Versus AI
        self.btn_versus = Button(pygame.Rect(0,0,0,0), "VERSUS AI", 
                                 lambda: manager.set_screen(__import__("ui.versus_screen").versus_screen.VersusScreen(manager)))
        # 3. Settings
        self.btn_settings = Button(pygame.Rect(0,0,0,0), "SETTINGS", 
                                   lambda: manager.set_screen(__import__("ui.settings_screen").settings_screen.SettingsScreen(manager)))
        # 4. Quit
        self.btn_quit = Button(pygame.Rect(0,0,0,0), "QUIT", 
                               lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)),
                               bg=(180, 50, 50), fg=(255, 255, 255))

        self.buttons = [self.btn_play, self.btn_versus, self.btn_settings, self.btn_quit]

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def update(self):
        # Could add animations here
        pass

    def draw(self):
        surf = self.manager.surface
        w, h = surf.get_size()
        
        # Refresh theme background
        self.settings = load_settings()
        self.theme_colors = get_theme_colors(self.settings.get("theme", "Classic"))
        surf.fill(self.theme_colors["bg"])
        
        center_x = w // 2
        
        # --- Dynamic Layout ---
        # Title Position
        title_y = int(h * 0.15)
        
        # Title "POWER 11" text
        # Scale font based on width
        t_size = int(min(w, h) * 0.1) # 10% of smallest dim
        if t_size < 30: t_size = 30
        
        font = get_font(t_size)
        txt_str = "POWER 11"
        col_main = (255, 215, 0) # Gold
        col_shadow = (0, 0, 0)
        
        txt_sh = font.render(txt_str, False, col_shadow)
        txt_mn = font.render(txt_str, False, col_main)
        
        offset = int(t_size * 0.08)
        
        rect_mn = txt_mn.get_rect(centerx=center_x, top=title_y)
        rect_sh = rect_mn.copy()
        rect_sh.x += offset
        rect_sh.y += offset
        
        surf.blit(txt_sh, rect_sh)
        surf.blit(txt_mn, rect_mn)
        
        # Buttons Layout
        # Start buttons below title
        btn_start_y = rect_mn.bottom + int(h * 0.08)
        
        # Button sizing
        btn_w = int(min(w, h) * 0.6) # 60% of viewport width
        if btn_w > 400: btn_w = 400
        if btn_w < 200: btn_w = 200
        
        btn_h = int(btn_w * 0.18) # Aspect ratio
        if btn_h < 40: btn_h = 40
        if btn_h > 70: btn_h = 70
        
        gap = int(btn_h * 0.4)
        
        # Update and draw buttons
        for i, btn in enumerate(self.buttons):
            y = btn_start_y + i * (btn_h + gap)
            rect = pygame.Rect(0, 0, btn_w, btn_h)
            rect.centerx = center_x
            rect.top = y
            
            # Update button rect
            btn.rect = rect
            
            # Draw
            btn.draw(surf)
            
        # Footer / Version
        f_size = int(t_size * 0.25)
        if f_size < 12: f_size = 12
        foot_font = get_font(f_size)
        foot = foot_font.render("HELLO WORLD !", False, self.theme_colors.get("text_dark", (100,100,100)))
        surf.blit(foot, foot.get_rect(centerx=center_x, bottom=h - 10))
