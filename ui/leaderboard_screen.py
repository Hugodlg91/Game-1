import pygame
import threading
from ui.screens import Screen
from ui.buttons import Button
from ui.ui_utils import get_font, get_theme_colors, calculate_layout
from core.leaderboard import LeaderboardManager

from core.settings import load_settings

class LeaderboardScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        self.surface = manager.surface
        
        # Load Theme
        settings = load_settings()
        self.current_theme = settings.get("theme", "Classic")
        self.theme_colors = get_theme_colors(self.current_theme)
        self.bg = self.theme_colors["bg"]
        
        w, h = self.surface.get_size()
        
        # Buttons
        btn_w = 240
        btn_h = 80
        self.back_button = Button(
            pygame.Rect((w - btn_w) // 2, h - 80, btn_w, btn_h),
            "BACK",
            lambda: manager.set_screen(__import__("ui.menu").menu.MainMenuScreen(manager)),
            bg=(180, 50, 50), fg=(255, 255, 255)
        )
        
        self.scores = []
        self.loading = True
        self.error_msg = None
        
        # Start fetching scores in background
        threading.Thread(target=self.fetch_scores, daemon=True).start()

    def fetch_scores(self):
        try:
            self.scores = LeaderboardManager.get_top_scores(10)
            self.loading = False
        except Exception as e:
            self.scores = []
            self.loading = False
            self.error_msg = "Could not load scores."
            print(f"Error fetching scores: {e}")

    def handle_event(self, event):
        self.back_button.handle_event(event)

    def update(self):
        pass

    def draw(self):
        surf = self.surface
        w, h = surf.get_size()
        
        # Refresh active theme in case it changed
        settings = load_settings()
        self.current_theme = settings.get("theme", "Classic")
        self.theme_colors = get_theme_colors(self.current_theme)
        self.bg = self.theme_colors["bg"]
        
        surf.fill(self.bg)
        
        center_x = w // 2
        
        # Text Colors from Theme
        title_col = self.theme_colors.get("text_light", (255, 215, 0)) # Default/Fallback
        text_col = self.theme_colors.get("text_dark", (200, 200, 200))
        
        # Title
        title_font = get_font(int(min(w, h) * 0.08))
        title = title_font.render("WORLD RECORDS", False, title_col)
        rect = title.get_rect(center=(center_x, int(h * 0.1)))
        surf.blit(title, rect)
        
        # Scores Area
        start_y = int(h * 0.2)
        row_h = int(h * 0.06)
        if row_h < 30: row_h = 30
        
        font = get_font(int(row_h * 0.6))
        
        if self.loading:
            load_txt = font.render("Loading...", False, (200, 200, 200))
            surf.blit(load_txt, load_txt.get_rect(center=(center_x, h // 2)))
        
        elif self.error_msg:
            err_txt = font.render(self.error_msg, False, (255, 50, 50))
            surf.blit(err_txt, err_txt.get_rect(center=(center_x, h // 2)))
            
        elif not self.scores:
            empty_txt = font.render("No scores found.", False, (200, 200, 200))
            surf.blit(empty_txt, empty_txt.get_rect(center=(center_x, h // 2)))
            
        else:
            # Draw Header (Rank | Name | Score)
            header_y = start_y
            # Draw Header (Rank | Name | Score)
            header_y = start_y
            # We can use columns - Increased spacing to prevent overlap
            # Rank: x-700, Name: x, Score: x+700 (Total spread 1400px) in 4K
            col_rank_x = center_x - 700
            col_name_x = center_x
            col_score_x = center_x + 700
            
            # Draw Rows
            for i, (rank, name, score) in enumerate(self.scores):
                y = header_y + (i * row_h) + 10
                
                # Colors
                if i == 0: color = (255, 215, 0) # Gold
                elif i == 1: color = (192, 192, 192) # Silver
                elif i == 2: color = (205, 127, 50) # Bronze
                else: color = (200, 200, 200) # White-ish
                
                # Rank
                r_txt = font.render(f"#{rank}", False, color)
                r_rect = r_txt.get_rect(midright=(col_rank_x - 20, y + row_h//2))
                surf.blit(r_txt, r_rect)
                
                # Name
                n_txt = font.render(name[:12], False, color) # Limit display length
                n_rect = n_txt.get_rect(midleft=(col_rank_x, y + row_h//2)) # Align name start where rank ended approx
                # Actually let's center name?
                n_rect = n_txt.get_rect(center=(col_name_x, y + row_h//2))
                surf.blit(n_txt, n_rect)
                
                # Score
                s_txt = font.render(str(score), False, color)
                s_rect = s_txt.get_rect(midleft=(col_score_x, y + row_h//2))
                surf.blit(s_txt, s_rect)

        # Back Button
        self.back_button.rect.centerx = center_x
        self.back_button.rect.bottom = h - 30
        self.back_button.draw(surf)
