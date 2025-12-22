"""Graphical settings screen with Pixel Art style."""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.buttons import Button
from core.settings import KEYS, load_settings, save_settings, save_theme
from ui.ui_utils import THEMES, get_theme_colors, get_font, calculate_layout


class SettingsScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        self.surface = manager.surface
        
        # Load Settings & Theme
        self.settings = load_settings()
        self.current_theme = self.settings.get("theme", "Classic")
        self.theme_colors = get_theme_colors(self.current_theme)
        self.bg = self.theme_colors["bg"]
        
        # Initialize Buttons with Dummy Rects (updated in draw/update)
        self.back_button = Button(
            pygame.Rect(0, 0, 150, 50),
            "BACK",
            lambda: manager.set_screen(__import__("ui.menu").menu.MainMenuScreen(manager)),
            bg=(180, 50, 50), fg=(255, 255, 255)
        )
        
        self.theme_button = Button(
            pygame.Rect(0, 0, 300, 60),
            f"THEME: {self.current_theme.upper()}",
            lambda: self.cycle_theme(),
            bg=(50, 50, 180), fg=(255, 255, 255)
        )
        
        # Key Binding State
        self.listening = None
        self.key_actions = ["up", "down", "left", "right"]
        self.key_boxes = {}

    def cycle_theme(self):
        themes = list(THEMES.keys())
        try:
            current_idx = themes.index(self.current_theme)
        except ValueError:
            current_idx = 0
        
        next_idx = (current_idx + 1) % len(themes)
        self.current_theme = themes[next_idx]
        
        # Update text
        self.theme_button.text = f"THEME: {self.current_theme.upper()}"
        save_theme(self.current_theme)
        
        # Apply new theme immediately
        self.theme_colors = get_theme_colors(self.current_theme)
        self.bg = self.theme_colors["bg"]

    def handle_event(self, event):
        self.back_button.handle_event(event)
        self.theme_button.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.listening:
                for action, rect in self.key_boxes.items():
                    if rect.collidepoint(event.pos):
                        self.listening = action
                        break
            else:
                pass
                
        elif event.type == pygame.KEYDOWN:
            if self.listening:
                key_name = pygame.key.name(event.key)
                if "keys" not in self.settings:
                    self.settings["keys"] = {}
                self.settings["keys"][self.listening] = key_name
                save_settings(self.settings)
                self.listening = None

    def update(self):
        pass

    def draw(self):
        surf = self.surface
        w, h = surf.get_size()
        
        # Refresh BG
        self.theme_colors = get_theme_colors(self.current_theme)
        self.bg = self.theme_colors["bg"]
        surf.fill(self.bg)
        
        center_x = w // 2
        
        # --- TITLE ---
        t_size = int(min(w, h) * 0.08)
        if t_size < 30: t_size = 30
        title_font = get_font(t_size)
        title_str = "SETTINGS"
        
        t_sh = title_font.render(title_str, False, (0, 0, 0))
        t_mn = title_font.render(title_str, False, (255, 255, 255))
        
        top_margin = int(h * 0.05)
        r_mn = t_mn.get_rect(centerx=center_x, top=top_margin)
        r_sh = r_mn.copy()
        r_sh.x += int(t_size*0.06)
        r_sh.y += int(t_size*0.06)
        
        surf.blit(t_sh, r_sh)
        surf.blit(t_mn, r_mn)
        
        # --- THEME BUTTON ---
        btn_w = int(min(w, h) * 0.5)
        if btn_w < 200: btn_w = 200
        btn_h = int(btn_w * 0.2)
        if btn_h < 40: btn_h = 40
        
        btn_y = r_mn.bottom + int(h * 0.05)
        self.theme_button.rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.theme_button.rect.centerx = center_x
        self.theme_button.rect.top = btn_y
        self.theme_button.draw(surf)
        
        # --- KEY BINDINGS ---
        start_y = self.theme_button.rect.bottom + int(h * 0.05)
        # Use dynamic gap
        gap_y = int(h * 0.08)
        if gap_y < 50: gap_y = 50
        
        label_size = int(min(w,h) * 0.03)
        if label_size < 16: label_size = 16
        label_font = get_font(label_size)
        
        key_box_size = int(label_size * 2.5)
        key_font = get_font(int(key_box_size * 0.4))
        
        current_keys = self.settings.get("keys", {"up": "w", "down": "s", "left": "a", "right": "d"})
        self.key_boxes = {}
        
        for i, action in enumerate(self.key_actions):
            row_y = start_y + i * gap_y
            
            # Key Box Rect
            # Position box slightly right of center
            key_rect = pygame.Rect(0, 0, key_box_size, key_box_size)
            key_rect.centerx = center_x + int(key_box_size * 0.8)
            key_rect.centery = row_y
            self.key_boxes[action] = key_rect
            
            # Draw Label (Right aligned to center - gap)
            label_txt = label_font.render(action.upper(), False, (200, 200, 200))
            label_rect = label_txt.get_rect(right=center_x - int(key_box_size * 0.2), centery=row_y)
            surf.blit(label_txt, label_rect)
            
            # Draw Box
            if self.listening == action:
                box_col = (200, 50, 50)
                border_col = (255, 200, 200)
                display_char = "?"
            else:
                box_col = (50, 50, 50)
                border_col = (0, 0, 0)
                display_char = current_keys.get(action, "?").upper()
            
            pygame.draw.rect(surf, box_col, key_rect)
            pygame.draw.rect(surf, border_col, key_rect, 3)
            
            char_txt = key_font.render(display_char, False, (255, 255, 255))
            char_rect = char_txt.get_rect(center=key_rect.center)
            surf.blit(char_txt, char_rect)

        # --- INSTRUCTION ---
        if self.listening:
            instr_font = get_font(int(label_size * 0.8))
            instr_txt = instr_font.render("PRESS NEW KEY...", False, (255, 50, 50))
            instr_rect = instr_txt.get_rect(centerx=center_x, top=start_y + 4 * gap_y + 10)
            surf.blit(instr_txt, instr_rect)

        # --- BACK BUTTON ---
        self.back_button.rect.width = int(btn_w * 0.6)
        self.back_button.rect.height = int(btn_h * 0.8)
        self.back_button.rect.centerx = center_x
        self.back_button.rect.bottom = h - int(h * 0.05)
        self.back_button.draw(surf)
