"""Screen that runs the heuristic AI autoplay and visualizes the board."""
from __future__ import annotations

import pygame
from ui.screens import Screen
from ui.buttons import Button
from ui.ui_utils import tile_color, get_theme_colors, get_font, get_tile_text_info, calculate_layout
from ui.animations import TileAnimator
from core.game_2048 import Game2048
from core.ai_player import choose_best_move
from core.settings import load_settings


class HeuristicScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        self.surface = manager.surface
        self.game = Game2048()
        
        settings = load_settings()
        self.refresh_theme(settings)
        
        w, h = self.surface.get_size()
        
        # Back Button (Position updated in draw)
        self.back_button = Button(
            pygame.Rect(20, h - 70, 150, 50), 
            "BACK", 
            lambda: manager.set_screen(__import__("ui.menu").menu.MainMenuScreen(manager)),
            bg=(180, 50, 50), fg=(255, 255, 255)
        )
        
        self.speed = 2.0
        self.acc = 0.0
        self.animator = TileAnimator(duration_ms=150)
        self.high_score = settings.get("highscore", 0)

    def refresh_theme(self, settings):
        self.theme_name = settings.get("theme", "Classic")
        self.theme = get_theme_colors(self.theme_name)
        self.bg = self.theme["bg"]
        self.high_score = settings.get("highscore", 0)

    def handle_event(self, event):
        self.back_button.handle_event(event)

    def update(self):
        dt_ms = 1000 / 60.0
        self.animator.update(dt_ms)
        
        if not self.animator.is_animating():
            dt = 1 / 60.0
            self.acc += dt
            if self.acc >= 1.0 / max(0.01, self.speed):
                move = choose_best_move(self.game)
                if move:
                    old_score = self.game.score
                    old_board = [row[:] for row in self.game.board]
                    moved = self.game.move(move)
                    
                    if self.game.score > self.high_score:
                        self.high_score = self.game.score
                        
                    if moved:
                        self.animator.start_move_animation(old_board, self.game.board, move)
                self.acc = 0.0

    def draw(self):
        surf = self.surface
        w, h = surf.get_size()
        
        surf.fill(self.bg)
        
        # --- DYNAMIC LAYOUT ---
        size = self.game.size
        layout = calculate_layout(w, h, size)
        CELL_SIZE = layout["cell_size"]
        MARGIN = layout["margin"]
        board_px = layout["board_size_px"]
        start_x = layout["start_x"]
        
        # Header Offset
        header_height = int(max(80, h * 0.15))
        start_y = header_height + (h - header_height - board_px) // 2
        
        font_lg = layout["font_large"]
        font_md = layout["font_med"]
        font_sm = layout["font_small"]
        
        empty_color = self.theme["empty"]
        border_col = self.theme.get("border", (0, 0, 0))
        
        # --- HEADER ---
        header_y_top = int(h * 0.03)
        
        # 1. Title
        t_size = int(min(w,h) * 0.05) if w > 600 else 20
        title_font = get_font(t_size)
        title_col = self.theme.get("text_light", (255, 255, 255))
        title_txt = title_font.render("POWER 11", False, title_col)
        surf.blit(title_txt, (int(w*0.04), header_y_top))
        
        sub_font = get_font(int(t_size*0.5))
        sub_txt = sub_font.render("AI: HEURISTIC", False, self.theme.get("text_dark", (200, 200, 200)))
        surf.blit(sub_txt, (int(w*0.04), header_y_top + int(t_size * 1.5)))
        
        # 2. Score Boxes
        box_w = int(w * 0.15)
        if box_w < 120: box_w = 120
        box_h = int(box_w * 0.5)
        box_gap = int(w * 0.02)
        
        group_w = box_w * 2 + box_gap
        group_x = (w - group_w) // 2
        
        box_bg = self.theme.get("empty", (100, 100, 100))
        txt_lbl_col = self.theme.get("text_dark", (200, 200, 200))
        txt_val_col = self.theme.get("text_light", (255, 255, 255))
        
        def draw_box(lbl, val, x, y):
            r = pygame.Rect(x, y, box_w, box_h)
            pygame.draw.rect(surf, box_bg, r)
            pygame.draw.rect(surf, border_col, r, 3)
            
            lf = get_font(int(box_h*0.2))
            lt = lf.render(lbl, False, txt_lbl_col)
            surf.blit(lt, lt.get_rect(centerx=r.centerx, top=r.top+int(box_h*0.15)))
            
            vf = get_font(int(box_h*0.35))
            vt = vf.render(str(val), False, txt_val_col)
            surf.blit(vt, vt.get_rect(centerx=r.centerx, bottom=r.bottom-int(box_h*0.1)))

        draw_box("SCORE", self.game.score, group_x, header_y_top)
        draw_box("BEST", self.high_score, group_x + box_w + box_gap, header_y_top)
        
        # --- BOARD ---
        pygame.draw.rect(surf, empty_color, (start_x, start_y, board_px, board_px))
        pygame.draw.rect(surf, border_col, (start_x, start_y, board_px, board_px), 3)
        
        def draw_tile(val, x, y, size_px, alpha=255):
            rect = (x, y, size_px, size_px)
            if val == 0: col = empty_color
            else: col = tile_color(val, self.theme_name)
            
            if alpha < 255:
                s = pygame.Surface((size_px, size_px), pygame.SRCALPHA)
                pygame.draw.rect(s, (*col, alpha), (0,0,size_px,size_px))
                if val: pygame.draw.rect(s, (*border_col, alpha), (0,0,size_px,size_px), 2)
                surf.blit(s, (x, y))
            else:
                pygame.draw.rect(surf, col, rect)
                if val: pygame.draw.rect(surf, border_col, rect, 2)
            
            if val != 0:
                txt_col, _ = get_tile_text_info(val, self.theme_name)
                # Pick pre-calculated font
                if val < 100: f_sz = font_lg
                elif val < 1000: f_sz = font_md
                else: f_sz = font_sm
                
                # Scale for animation
                if size_px != CELL_SIZE:
                    f_sz = int(f_sz * (size_px / CELL_SIZE))
                
                font = get_font(f_sz)
                txt = font.render(str(val), False, txt_col)
                surf.blit(txt, txt.get_rect(center=(x + size_px/2, y + size_px/2)))

        # Static Grid
        for r in range(size):
            for c in range(size):
                x = start_x + MARGIN + c * (CELL_SIZE + MARGIN)
                y = start_y + MARGIN + r * (CELL_SIZE + MARGIN)
                draw_tile(0, x, y, CELL_SIZE)
                
                val = self.game.board[r][c]
                if val != 0 and not self.animator.is_animating():
                    draw_tile(val, x, y, CELL_SIZE)
        
        # Animated
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

        # --- GAME OVER OVERLAY ---
        if not self.game.has_moves_available():
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            surf.blit(overlay, (0,0))
            
            go_font = get_font(int(min(w,h)*0.1))
            go_txt = go_font.render("GAME OVER", False, (255, 50, 50))
            surf.blit(go_txt, go_txt.get_rect(center=(w//2, h//2)))
            
            sc_font = get_font(int(min(w,h)*0.05))
            sc_txt = sc_font.render(f"FINAL SCORE: {self.game.score}", False, (255, 255, 255))
            surf.blit(sc_txt, sc_txt.get_rect(center=(w//2, h//2 + 60)))

        # Draw UI
        self.back_button.rect.y = h - 70
        self.back_button.draw(surf)
