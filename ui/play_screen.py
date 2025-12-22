"""Main gameplay screen."""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.buttons import Button
from ui.ui_utils import tile_color, get_theme_colors, get_font, get_tile_text_info, calculate_layout, resource_path
from ui.animations import TileAnimator
from ui.sound_manager import SoundManager
from core.game_2048 import Game2048
from core.settings import load_settings, save_settings
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
            pygame.Rect(0, 0, 120, 40), # Position updated in draw
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
            pygame.Rect(0, 0, 100, 40), # Position updated in draw
            "RESET", 
            self.reset_game, 
            bg=(50, 180, 50), fg=(255, 255, 255),
            icon=self.reset_icon
        )
        
        self.animator = TileAnimator()
        
        # --- Game Over ---
        self.game_over_handled = False
        self.try_again_button = Button(pygame.Rect(0, 0, 200, 60), "TRY AGAIN", self.reset_game, bg=(237, 194, 46), fg=(255, 255, 255))

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
                
            self.try_again_button.handle_event(event)
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
            if available_h < 100: available_h = 100 # Minimum clamp to prevent crash, but 300 was too high

            
            # --- DYNAMIC LAYOUT ---
            # Pass available_h to ensure board fits in the gap
            # Actually calculate_layout centers based on width passed. 
            # Better: calculate based on full W, but reduced H.
            layout = calculate_layout(w, available_h, self.game.size)
            CELL_SIZE = layout["cell_size"]
            MARGIN = layout["margin"]
            board_px = layout["board_size_px"]
            start_x = (w - board_px) // 2
            
            start_y = header_height + (available_h - board_px) // 2
            if start_y < header_height + 10: start_y = header_height + 10
            
            font_lg = layout["font_large"]
            font_md = layout["font_med"]
            font_sm = layout["font_small"]

            self.bg = self.theme["bg"] # Ensure dynamic theme update if changed
            surf.fill(self.bg)

            # ===== HEADER =====
            # 1. Main Title "POWER 11" (Top Left)
            t_size = int(min(w,h) * 0.05) if w > 600 else 24
            title_font = get_font(t_size)
            title_col = self.theme.get("text_light", (255, 255, 255))
            title_txt = title_font.render("POWER 11", False, title_col)
            
            title_x = int(w * 0.04)
            title_y = int(h * 0.03)
            surf.blit(title_txt, (title_x, title_y))

            # 2. Score Boxes (Top Right)
            box_w = int(w * 0.16)
            if box_w < 100: box_w = 100
            if box_w > 180: box_w = 180
            box_h = int(box_w * 0.5)
            box_gap = 10
            
            # Group Width
            group_w = box_w * 2 + box_gap
            # Align Right with margin
            group_x = w - group_w - int(w * 0.04)
            
            box_bg = self.theme.get("empty", (100, 100, 100))
            border_col = self.theme.get("border", (0, 0, 0))
            lbl_col = self.theme.get("text_dark", (200, 200, 200))
            val_col = self.theme.get("text_light", (255, 255, 255))
            
            def draw_score_box(label, value, x, y):
                r = pygame.Rect(x, y, box_w, box_h)
                pygame.draw.rect(surf, box_bg, r)
                pygame.draw.rect(surf, border_col, r, 3)
                
                l_font = get_font(int(box_h * 0.25))
                l_txt = l_font.render(label, False, lbl_col)
                surf.blit(l_txt, l_txt.get_rect(centerx=r.centerx, top=r.top + box_h*0.1))
                
                v_font = get_font(int(box_h * 0.4))
                v_txt = v_font.render(str(value), False, val_col)
                surf.blit(v_txt, v_txt.get_rect(centerx=r.centerx, bottom=r.bottom - box_h*0.1))

            # Align with title Y vertically
            draw_score_box("SCORE", self.game.score, group_x, title_y)
            draw_score_box("BEST", self.high_score, group_x + box_w + box_gap, title_y)

            # ===== BOARD BACKGROUND =====
            board_bg_col = self.theme.get("header_bg", (143, 122, 102))
            
            # Main Board Rect (Thick Border)
            pygame.draw.rect(surf, board_bg_col, (start_x, start_y, board_px, board_px))
            pygame.draw.rect(surf, border_col, (start_x, start_y, board_px, board_px), 4)

            empty_tile_col = self.theme["empty"]
            
            def draw_tile(val, x, y, size_px, alpha=255):
                rect = (x, y, size_px, size_px)
                
                if val == 0: col = empty_tile_col
                else: col = tile_color(val, self.theme_name)
                
                if alpha < 255:
                    # Ghost tile
                    s = pygame.Surface((size_px, size_px), pygame.SRCALPHA)
                    pygame.draw.rect(s, (*col, alpha), (0,0,size_px,size_px))
                    if val != 0: pygame.draw.rect(s, (*border_col, alpha), (0,0,size_px,size_px), 2)
                    surf.blit(s, (x, y))
                else:
                    pygame.draw.rect(surf, col, rect)
                    if val != 0: pygame.draw.rect(surf, border_col, rect, 2)
                
                # Text
                if val != 0:
                    txt_col, _ = get_tile_text_info(val, self.theme_name)
                    
                    # Dynamic sizing
                    if val < 100: f_sz = font_lg
                    elif val < 1000: f_sz = font_md
                    else: f_sz = font_sm
                    
                    if size_px != CELL_SIZE:
                        f_sz = int(f_sz * (size_px / CELL_SIZE))
                    
                    # Safety clamp
                    if f_sz < 8: f_sz = 8
                    
                    ft = get_font(f_sz)
                    tx = ft.render(str(val), False, txt_col)
                    surf.blit(tx, tx.get_rect(center=(x + size_px/2, y + size_px/2)))

            # Static Grid (Empty + Static Tiles)
            for r in range(self.game.size):
                for c in range(self.game.size):
                    x = start_x + MARGIN + c * (CELL_SIZE + MARGIN)
                    y = start_y + MARGIN + r * (CELL_SIZE + MARGIN)
                    
                    # Draw empty background for every cell
                    draw_tile(0, x, y, CELL_SIZE)
                    
                    val = self.game.board[r][c]
                    if val != 0 and not self.animator.is_animating():
                         draw_tile(val, x, y, CELL_SIZE)

            # Animated Tiles
            if self.animator.is_animating():
                tiles = self.animator.get_render_tiles(CELL_SIZE, MARGIN)
                for t in tiles:
                    x = start_x + t['x']
                    y = start_y + t['y']
                    draw_tile(t['value'], 
                              x + (CELL_SIZE - int(CELL_SIZE*t['scale']))//2, 
                              y + (CELL_SIZE - int(CELL_SIZE*t['scale']))//2, 
                              int(CELL_SIZE*t['scale']), 
                              t['alpha'])

            # ===== BUTTONS =====
            # Back Button (Bottom Left)
            self.back_button.rect.x = 20
            self.back_button.rect.y = h - 60
            self.back_button.draw(surf)
            
            # Reset Button (Bottom Right)
            self.reset_button.rect.x = w - 140
            self.reset_button.rect.y = h - 60
            self.reset_button.draw(surf)

            # ===== GAME OVER =====
            if not self.game.has_moves_available():
                overlay = pygame.Surface((w, h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))
                surf.blit(overlay, (0,0))
                
                go_font = get_font(int(min(w,h)*0.1))
                go_txt = go_font.render("GAME OVER", False, (255, 50, 50))
                surf.blit(go_txt, go_txt.get_rect(center=(w//2, h//2 - 40)))
                
                sc_font = get_font(25)
                sc_txt = sc_font.render(f"FINAL SCORE: {self.game.score}", False, (255, 255, 255))
                surf.blit(sc_txt, sc_txt.get_rect(center=(w//2, h//2 + 30)))
                
                self.try_again_button.rect.center = (w//2, h//2 + 90)
                self.try_again_button.draw(surf)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error in PlayScreen.draw: {e}")
