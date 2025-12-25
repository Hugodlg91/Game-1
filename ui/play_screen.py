"""Main gameplay screen."""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.input_box import InputBox
from ui.buttons import Button
from ui.animations import TileAnimator
from ui.ui_utils import get_font, get_theme_colors, resource_path, draw_board, calculate_layout
from core.leaderboard import LeaderboardManager
from core.game_2048 import Game2048
from core.settings import load_settings, save_settings
import threading
import os

class PlayScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        self.surface = manager.surface
        self.game = Game2048()
        
        settings = load_settings()
        self.high_score = settings.get("highscore", 0)
        self.theme_name = settings.get("theme", "Classic")
        self.theme = get_theme_colors(self.theme_name)
        self.bg = self.theme["bg"]
        
        # --- Load Key Bindings ---
        keys = settings.get("keys", {"up": "w", "down": "s", "left": "a", "right": "d"})
        self.key_up = pygame.key.key_code(keys.get("up", "w"))
        self.key_down = pygame.key.key_code(keys.get("down", "s"))
        self.key_left = pygame.key.key_code(keys.get("left", "a"))
        self.key_right = pygame.key.key_code(keys.get("right", "d"))
        
        # Use shared sound manager from manager
        self.sound_manager = manager.sound_manager if hasattr(manager, 'sound_manager') else None
        
        # --- Back Button (Restored) ---
        self.back_button = Button(
            pygame.Rect(0, 0, 240, 80), # Position updated in draw
            "BACK",
            lambda: self.on_back(),
            bg=(200, 50, 50), fg=(255, 255, 255)
        )
        
        # --- Reset Button ---
        # Load Icon
        self.reset_icon = None
        try:
            icon_path = resource_path("assets/reset_block.png")
            if os.path.exists(icon_path):
                self.reset_icon = pygame.image.load(icon_path)
        except Exception:
            print("Warning: Reset icon not found.")
        
        self.reset_button = Button(
            pygame.Rect(0, 0, 260, 80), # Position updated in draw
            "RESET", 
            self.reset_game, 
            bg=(50, 180, 50), fg=(255, 255, 255),
            icon=self.reset_icon
        )
        
        self.animator = TileAnimator()
        
        # --- Game Over ---
        self.game_over_handled = False
        self.try_again_button = Button(
            pygame.Rect(0, 0, 300, 80), 
            "TRY AGAIN", 
            self.reset_game, 
            bg=(237, 194, 46), 
            fg=(255, 255, 255),
            font_size=30
        )
        
        # --- Leaderboard Submission ---
        self.input_box = InputBox(0, 0, 200, 40) # Positioned in draw
        self.score_submitted = False
        self.submitting = False

    def on_back(self):
        # Save before leaving
        settings = load_settings()
        settings["highscore"] = self.high_score
        settings["theme"] = self.theme_name
        save_settings(settings)
        try:
            from ui.menu import MainMenuScreen
            self.manager.set_screen(MainMenuScreen(self.manager))
        except ImportError:
             self.manager.set_screen(__import__("ui.menu").menu.MainMenuScreen(self.manager))

    def reset_game(self):
        self.game = Game2048()
        self.animator = TileAnimator()
        self.game_over_handled = False
        self.score_submitted = False
        self.submitting = False
        self.input_box.text = '' # Empty by default
        self.input_box.txt_surface = self.input_box.font.render('', True, self.input_box.color)
        
        if self.sound_manager:
            self.sound_manager.play("move")

    def handle_event(self, event):
        # High score check
        if self.game.score > self.high_score:
            self.high_score = self.game.score
            settings = load_settings()
            settings["highscore"] = self.high_score
            settings["theme"] = self.theme_name
            save_settings(settings)

        # Game Over
        if not self.game.has_moves_available():
            if not self.game_over_handled:
                if self.sound_manager:
                    self.sound_manager.play("gameover")
                self.game_over_handled = True
            
            # Handle Score Submission
            if not self.score_submitted and not self.submitting:
                name = self.input_box.handle_event(event)
                if name:
                    self.submitting = True
                    def submit_thread():
                        success = LeaderboardManager.submit_score(name, self.game.score)
                        self.score_submitted = success # Ideally check success
                    threading.Thread(target=submit_thread, daemon=True).start()
            
            self.try_again_button.handle_event(event)

            # Handle Menu Button Click (stored in self.menu_button during draw)
            if hasattr(self, 'menu_button') and event.type == pygame.MOUSEBUTTONDOWN:
                if self.menu_button.rect.collidepoint(event.pos):
                    self.on_back()
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.on_back()
            return

        # Normal Gameplay
        self.back_button.handle_event(event) # Handle Back Button
        self.reset_button.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.on_back()
            
            moved = False
            old_board = [row[:] for row in self.game.board]
            move_dir = None
            
            if event.key in (pygame.K_LEFT, self.key_left):
                moved = self.game.move('left'); move_dir = 'left'
            elif event.key in (pygame.K_RIGHT, self.key_right):
                moved = self.game.move('right'); move_dir = 'right'
            elif event.key in (pygame.K_UP, self.key_up):
                moved = self.game.move('up'); move_dir = 'up'
            elif event.key in (pygame.K_DOWN, self.key_down):
                moved = self.game.move('down'); move_dir = 'down'

            if moved:
                if self.sound_manager:
                    self.sound_manager.play("move")
                self.animator.start_move_animation(old_board, self.game.board, move_dir)
                if self.game.score > self.high_score:
                    self.high_score = self.game.score

    def update(self):
        dt = 1000 / 60
        self.animator.update(dt)

    def draw(self):
        try:
            surf = self.surface
            w, h = surf.get_size()
            
            # Vertical centering with header room
            header_height = int(h * 0.15) if h > 600 else 80
            footer_height = 80 # Reserve space for buttons
            
            available_h = h - header_height - footer_height
            if available_h < 100: available_h = 100 

            
            # --- DYNAMIC LAYOUT ---
            layout = calculate_layout(w, available_h, self.game.size)
            CELL_SIZE = layout["cell_size"]
            MARGIN = layout["margin"]
            board_px = layout["board_size_px"]
            start_x = (w - board_px) // 2
            
            start_y = header_height + (available_h - board_px) // 2
            if start_y < header_height + 10: start_y = header_height + 10
            
            font_lg = layout["font_large"]
            
            self.bg = self.theme["bg"] 
            surf.fill(self.bg)

            # ===== HEADER =====
            t_size = int(min(w,h) * 0.05) if w > 600 else 24
            title_font = get_font(t_size)
            title_col = self.theme.get("text_light", (255, 255, 255))
            title_txt = title_font.render("POWER 11", False, title_col)
            
            title_x = int(w * 0.04)
            title_y = int(h * 0.03)
            surf.blit(title_txt, (title_x, title_y))

            # 2. Score Boxes (Top Right)
            
            # Helper to calculate needed width
            def get_text_width(text, font_size):
                f = get_font(font_size)
                return f.size(text)[0]

            # Base height
            # 4K context: Box height should be substantial
            box_h = 100 
            
            # Calculate font sizes
            lbl_font_size = int(box_h * 0.25)
            val_font_size = int(box_h * 0.5)

            # Calculate content widths
            score_str = str(self.game.score)
            best_str = str(self.high_score)
            
            score_val_w = get_text_width(score_str, val_font_size)
            best_val_w = get_text_width(best_str, val_font_size)
            
            min_w = 200
            padding = 40
            
            score_w = max(min_w, score_val_w + padding)
            best_w = max(min_w, best_val_w + padding)
            
            # Layout from Right to Left
            box_gap = 20
            margin_right = int(w * 0.04)
            
            # Best Score (Rightmost)
            best_x = w - margin_right - best_w
            
            # Score (Left of Best)
            score_x = best_x - box_gap - score_w
            
            box_bg = self.theme.get("empty", (100, 100, 100))
            border_col = self.theme.get("border", (0, 0, 0))
            lbl_col = self.theme.get("text_dark", (200, 200, 200))
            val_col = self.theme.get("text_light", (255, 255, 255))
            
            def draw_score_box(label, value_str, x, y, width):
                r = pygame.Rect(x, y, width, box_h)
                pygame.draw.rect(surf, box_bg, r)
                pygame.draw.rect(surf, border_col, r, 5) 
                
                l_font = get_font(lbl_font_size)
                l_txt = l_font.render(label, False, lbl_col)
                surf.blit(l_txt, l_txt.get_rect(centerx=r.centerx, top=r.top + box_h*0.1))
                
                v_font = get_font(val_font_size)
                v_txt = v_font.render(value_str, False, val_col)
                surf.blit(v_txt, v_txt.get_rect(centerx=r.centerx, bottom=r.bottom - box_h*0.1))

            draw_score_box("SCORE", score_str, score_x, title_y, score_w)
            draw_score_box("BEST", best_str, best_x, title_y, best_w)

            # ===== DRAW BOARD =====
            draw_board(surf, self.game, start_x, start_y, CELL_SIZE, MARGIN, self.theme_name, self.animator)

            # ===== BUTTONS =====
            self.back_button.rect.x = 40
            self.back_button.rect.y = h - 120
            self.back_button.draw(surf)
            
            self.reset_button.rect.x = w - 340
            self.reset_button.rect.y = h - 120
            self.reset_button.draw(surf)

            # ===== GAME OVER =====
            if not self.game.has_moves_available():
                # 1. Overlay
                overlay = pygame.Surface((w, h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                surf.blit(overlay, (0,0))
                
                center_x, center_y = w // 2, h // 2
                
                # Layout Constants
                # Title -> Score -> Instruction -> Input -> Buttons
                
                # 2. Title "GAME OVER"
                go_font = get_font(int(min(w,h)*0.1))
                go_txt = go_font.render("GAME OVER", False, (220, 50, 50))
                go_rect = go_txt.get_rect(center=(center_x, center_y - 200))
                surf.blit(go_txt, go_rect)
                
                # 3. Score
                sc_font = get_font(50)
                sc_txt = sc_font.render(f"Score: {self.game.score}", False, (255, 255, 255))
                sc_rect = sc_txt.get_rect(center=(center_x, go_rect.bottom + 60))
                surf.blit(sc_txt, sc_rect)
                
                # 4. Instruction / Input / Status
                if self.score_submitted:
                    sent_font = get_font(40)
                    sent_txt = sent_font.render("Score Sent!", False, (50, 255, 50))
                    surf.blit(sent_txt, sent_txt.get_rect(center=(center_x, sc_rect.bottom + 80)))
                    
                elif self.submitting:
                    sub_font = get_font(40)
                    sub_txt = sub_font.render("Sending...", False, (255, 255, 50))
                    surf.blit(sub_txt, sub_txt.get_rect(center=(center_x, sc_rect.bottom + 80)))
                    
                else:
                    # Instruction
                    p_font = get_font(30)
                    p_txt = p_font.render("Enter Name & Press Enter:", False, (100, 255, 255))
                    p_rect = p_txt.get_rect(center=(center_x, sc_rect.bottom + 60))
                    surf.blit(p_txt, p_rect)
                    
                    # Update Input Box Position & Draw
                    # Ensure box is centered
                    self.input_box.rect.centerx = center_x
                    self.input_box.rect.top = p_rect.bottom + 20
                    self.input_box.update() # Handle resize
                    self.input_box.draw(surf)

                # 5. Buttons (Try Again, Menu)
                # Positioned at the bottom area
                btn_y = center_y + 200
                btn_gap = 20
                
                # Try Again
                self.try_again_button.rect.width = 300
                self.try_again_button.rect.height = 80
                self.try_again_button.rect.centerx = center_x - 160
                self.try_again_button.rect.top = btn_y
                self.try_again_button.draw(surf)
                
                # Menu (Reuse Back Button logic or create temporary button?)
                # Let's create a dedicated Menu button logic if needed, 
                # but for now we can reuse Back button if we change its text/pos, 
                # or better: draw a "MENU" button specifically for Game Over.
                # Since we don't have a "self.menu_button", let's use a temporary one or add it to init.
                # For simplicity, I'll draw a "MENU" button using the standard button style here.
                
                menu_btn_rect = pygame.Rect(center_x + 10, btn_y, 300, 80)
                menu_btn = Button(menu_btn_rect, "MENU", self.on_back, bg=(100, 100, 200), fg=(255, 255, 255))
                menu_btn.draw(surf)
                
                # Store this rect to handle clicks in handle_event? 
                # Better solution: Add self.menu_button to __init__ to avoid re-creation.
                self.menu_button = menu_btn # Hack to store reference for event handling
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error in PlayScreen.draw: {e}")
