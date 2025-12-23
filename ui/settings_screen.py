"""Graphical settings screen with Pixel Art style."""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.buttons import Button
from ui.sliders import VerticalSlider
from core.settings import KEYS, load_settings, save_settings, save_theme
from ui.ui_utils import THEMES, get_theme_colors, get_font, calculate_layout


class SettingsScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        self.surface = manager.surface
        self.sound_manager = manager.sound_manager if hasattr(manager, 'sound_manager') else None
        
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
        
        # Volume Sliders (Vertical)
        self.sliders = {}
        self.mute_buttons = {}  # Store mute button rects
        
        # We will initialize rects in draw() when we have dimensions, 
        # but we need the objects to persist to handle dragging.
        # So we'll defer creation or update rects in draw.
        # Actually, let's init with 0-rects and update them in draw.
        self.music_slider = VerticalSlider(pygame.Rect(0,0,10,10), self.settings.get("music_volume", 0.1))
        self.sfx_slider = VerticalSlider(pygame.Rect(0,0,10,10), self.settings.get("sfx_volume", 1.0))

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
            # Check checkboxes/mute buttons
            for button_name, button_rect in self.mute_buttons.items():
                if button_rect.collidepoint(event.pos):
                    if button_name == 'music':
                        if self.sound_manager:
                            self.settings['music_muted'] = self.sound_manager.toggle_music_mute()
                    elif button_name == 'sfx':
                        if self.sound_manager:
                            self.settings['sfx_muted'] = self.sound_manager.toggle_sfx_mute()
                            if not self.settings['sfx_muted']:
                                self.sound_manager.play('move')
                    save_settings(self.settings)
                    return

            # Check key binding boxes
            if not self.listening:
                for action, rect in self.key_boxes.items():
                    if rect.collidepoint(event.pos):
                        self.listening = action
                        break
            else:
                pass

        # Handle Sliders (Pass all events to allow dragging)
        if self.music_slider.handle_event(event):
            self.settings['music_volume'] = self.music_slider.value
            if self.sound_manager:
                self.sound_manager.set_music_volume(self.music_slider.value)
            save_settings(self.settings)

        if self.sfx_slider.handle_event(event):
            self.settings['sfx_volume'] = self.sfx_slider.value
            if self.sound_manager:
                self.sound_manager.set_sfx_volume(self.sfx_slider.value)
            save_settings(self.settings)
                
        if event.type == pygame.KEYDOWN:
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
        t_size = int(min(w,h) * 0.06)
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
        
        # --- VOLUME MIXER ---
        # Draw a panel for the mixer
        mixer_y = start_y + 4 * gap_y + 40
        mixer_height = h - mixer_y - int(h * 0.15) # Leave space for back button using dynamic logic
        # Actually back button is at h - 0.05.
        mixer_height = self.back_button.rect.top - mixer_y - 20
        
        if mixer_height < 150: mixer_height = 150

        # Define slider dimensions
        slider_w = 40
        slider_h = mixer_height - 60 # Space for labels/buttons
        
        # Center the two sliders
        spacing = 150
        
        # Music Slider
        music_x = center_x - spacing // 2
        self.music_slider.rect = pygame.Rect(music_x - slider_w//2, mixer_y + 10, slider_w, slider_h)
        self.music_slider.draw(surf)
        self._draw_mixer_controls(surf, "MUSIC", music_x, mixer_y, slider_h + 20, 'music', label_font)

        # SFX Slider
        sfx_x = center_x + spacing // 2
        self.sfx_slider.rect = pygame.Rect(sfx_x - slider_w//2, mixer_y + 10, slider_w, slider_h)
        self.sfx_slider.draw(surf)
        self._draw_mixer_controls(surf, "SFX", sfx_x, mixer_y, slider_h + 20, 'sfx', label_font)

        # --- BACK BUTTON ---
        self.back_button.rect.width = int(btn_w * 0.6)
        self.back_button.rect.height = int(btn_h * 0.8)
        self.back_button.rect.centerx = center_x
        self.back_button.rect.bottom = h - int(h * 0.05)
        self.back_button.draw(surf)

    def _draw_mixer_controls(self, surf, label, x, start_y, height_offset, key, font):
        # Label above
        lbl = font.render(label, False, (200, 200, 200))
        lbl_rect = lbl.get_rect(centerx=x, bottom=start_y)
        surf.blit(lbl, lbl_rect)
        
        # Mute Button below slider
        is_muted = self.settings.get(f'{key}_muted', False)
        btn_y = start_y + height_offset + 10
        btn_size = 30
        btn_rect = pygame.Rect(0, 0, btn_size, btn_size)
        btn_rect.centerx = x
        btn_rect.top = btn_y
        
        self.mute_buttons[key] = btn_rect
        
        if is_muted:
            col = (200, 50, 50)
            txt = "X"
        else:
            col = (50, 200, 50)
            txt = "OK" # or Volume icon
        
        pygame.draw.rect(surf, col, btn_rect)
        pygame.draw.rect(surf, (255, 255, 255), btn_rect, 2)
        
        # Small text or icon
        small_font = get_font(15)
        t = small_font.render(txt, False, (255, 255, 255))
        tr = t.get_rect(center=btn_rect.center)
        surf.blit(t, tr)
