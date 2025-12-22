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
        
        # Volume Sliders (10 segments each)
        self.volume_sliders = {}
        self.mute_buttons = {}  # Store mute button rects
        self.num_segments = 10

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
            # Check mute buttons first
            for button_name, button_rect in self.mute_buttons.items():
                if button_rect.collidepoint(event.pos):
                    if button_name == 'music':
                        if self.sound_manager:
                            self.settings['music_muted'] = self.sound_manager.toggle_music_mute()
                    elif button_name == 'sfx':
                        if self.sound_manager:
                            self.settings['sfx_muted'] = self.sound_manager.toggle_sfx_mute()
                            # Play test sound if unmuting
                            if not self.settings['sfx_muted']:
                                self.sound_manager.play('move')
                    save_settings(self.settings)
                    return
            
            # Check volume sliders
            for slider_name, segments in self.volume_sliders.items():
                for i, seg_rect in enumerate(segments):
                    if seg_rect.collidepoint(event.pos):
                        # Calculate new volume (1-indexed)
                        new_volume = (i + 1) / self.num_segments
                        
                        # Update settings
                        if slider_name == 'music':
                            self.settings['music_volume'] = new_volume
                            if self.sound_manager:
                                self.sound_manager.set_music_volume(new_volume)
                        elif slider_name == 'sfx':
                            self.settings['sfx_volume'] = new_volume
                            if self.sound_manager:
                                self.sound_manager.set_sfx_volume(new_volume)
                                # Play a test sound
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
        
        # --- VOLUME SLIDERS ---
        volume_start_y = start_y + 4 * gap_y + 60
        
        # Get current volumes
        music_vol = self.settings.get('music_volume', 0.1)
        sfx_vol = self.settings.get('sfx_volume', 1.0)
        
        slider_gap = int(h * 0.08)
        if slider_gap < 50: slider_gap = 50
        
        self._draw_volume_slider(surf, "MUSIC", music_vol, center_x, volume_start_y, label_font, 'music')
        self._draw_volume_slider(surf, "SFX", sfx_vol, center_x, volume_start_y + slider_gap, label_font, 'sfx')

        # --- BACK BUTTON ---
        self.back_button.rect.width = int(btn_w * 0.6)
        self.back_button.rect.height = int(btn_h * 0.8)
        self.back_button.rect.centerx = center_x
        self.back_button.rect.bottom = h - int(h * 0.05)
        self.back_button.draw(surf)
    
    def _draw_volume_slider(self, surf, label, volume, center_x, y, label_font, slider_name):
        """Draw a retro-style segmented volume slider with mute button."""
        # Get mute state
        is_muted = self.settings.get(f'{slider_name}_muted', False)
        
        # Draw label and mute button on same line
        label_txt = label_font.render(label, False, (200, 200, 200))
        label_rect = label_txt.get_rect(centerx=center_x - 80, bottom=y - 10)
        surf.blit(label_txt, label_rect)
        
        # Mute button (small square button)
        button_size = 30
        button_x = center_x + 60
        button_y = label_rect.centery - button_size // 2
        button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        self.mute_buttons[slider_name] = button_rect
        
        # Button color based on mute state
        if is_muted:
            button_color = (200, 50, 50)  # Red when muted
            border_color = (255, 100, 100)
            button_text = "X"
        else:
            button_color = (50, 200, 50)  # Green when active
            border_color = (100, 255, 100)
            button_text = "✓"
        
        pygame.draw.rect(surf, button_color, button_rect)
        pygame.draw.rect(surf, border_color, button_rect, 2)
        
        # Draw button text
        btn_font = get_font(18)
        btn_txt = btn_font.render(button_text, False, (255, 255, 255))
        btn_txt_rect = btn_txt.get_rect(center=button_rect.center)
        surf.blit(btn_txt, btn_txt_rect)
        
        # Slider dimensions
        seg_width = 30
        seg_height = 20
        seg_gap = 4
        total_width = self.num_segments * (seg_width + seg_gap) - seg_gap
        
        start_x = center_x - total_width // 2
        
        # Calculate how many segments should be lit
        lit_segments = int(volume * self.num_segments)
        
        # Store segment rects for click detection
        self.volume_sliders[slider_name] = []
        
        for i in range(self.num_segments):
            seg_x = start_x + i * (seg_width + seg_gap)
            seg_rect = pygame.Rect(seg_x, y, seg_width, seg_height)
            self.volume_sliders[slider_name].append(seg_rect)
            
            # Color based on lit state (dimmed if muted)
            if i < lit_segments:
                if is_muted:
                    seg_color = (100, 100, 100)  # Gray when muted
                    border_color = (150, 150, 150)
                else:
                    seg_color = (50, 200, 50)  # Bright green
                    border_color = (100, 255, 100)
            else:
                seg_color = (30, 30, 30)  # Dark gray
                border_color = (60, 60, 60)
            
            pygame.draw.rect(surf, seg_color, seg_rect)
            pygame.draw.rect(surf, border_color, seg_rect, 2)
