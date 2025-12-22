"""
Expectimax AI autoplay screen with Pixel Art style and Responsive Layout.
"""
from __future__ import annotations

import pygame
import json
import time
from pathlib import Path
from core.settings import *
from ui.screens import Screen
from ui.buttons import Button
from ui.animations import TileAnimator
from ui.ui_utils import tile_color, get_theme_colors, get_font, get_tile_text_info, calculate_layout, resource_path
from core.game_2048 import Game2048
from core.ai_player import expectimax_choose_move, BITBOARD_AVAILABLE


class ExpectimaxScreen(Screen):
    def __init__(self, manager):
        super().__init__(manager)
        
        if not BITBOARD_AVAILABLE:
            self.error_msg = "Bitboard module not available."
            self.game = None
            return
        
        self.surface = manager.surface
        
        self.settings = load_settings()
        self.theme_name = self.settings.get("theme", "Classic")
        self.theme = get_theme_colors(self.theme_name)
        self.bg = self.theme["bg"]
        self.text_color = self.theme.get("text_dark", (119, 110, 101))
        self.high_score = self.settings.get("highscore", 0)
        
        w, h = self.surface.get_size()
        
        # Back button
        self.back_button = Button(
            pygame.Rect(20, h - 70, 150, 50),
            "BACK",
            lambda: manager.set_screen(__import__("ui.menu").menu.MainMenuScreen(manager)),
            bg=(180, 50, 50), fg=(255, 255, 255)
        )
        
        # Weights
        self.weights = self._load_optimized_weights()
        self.weights_source = "OPTUNA" if self.weights else "DEFAULT"
        
        self.game = Game2048()
        self.animator = TileAnimator(duration_ms=150)
        
        self.depth = 3
        self.moves_per_second = 2.0
        self.time_since_last_move = 0.0
        
        self.moves_count = 0
        self.games_played = 0
        self.total_score = 0
        self.last_move_time = 0.0
        
        self.error_msg = None
    
    def _load_optimized_weights(self) -> dict | None:
        try:
            weights_path = Path(resource_path("expectimax_optuna_results/best_weights.json"))
            if not weights_path.exists():
                 weights_path = Path("expectimax_optuna_results/best_weights.json")
            if weights_path.exists():
                with open(weights_path, 'r') as f:
                    return json.load(f)
        except:
            pass
        return None
    
    def handle_event(self, event):
        if self.game is None:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from ui.menu import MainMenuScreen
                self.manager.set_screen(MainMenuScreen(self.manager))
            return
        
        self.back_button.handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from ui.menu import MainMenuScreen
                self.manager.set_screen(MainMenuScreen(self.manager))
            elif event.key == pygame.K_UP: self.moves_per_second = min(10.0, self.moves_per_second + 0.5)
            elif event.key == pygame.K_DOWN: self.moves_per_second = max(0.5, self.moves_per_second - 0.5)
            elif event.key == pygame.K_LEFT: self.depth = max(2, self.depth - 1)
            elif event.key == pygame.K_RIGHT: self.depth = min(5, self.depth + 1)
            elif event.key == pygame.K_r: self._reset_game()
    
    def _reset_game(self):
        if self.game and self.game.score > 0:
            self.total_score += self.game.score
            self.games_played += 1
        self.game = Game2048()
        self.animator = TileAnimator(duration_ms=150)
        self.moves_count = 0
        self.time_since_last_move = 0.0
    
    def update(self):
        if self.game is None: return
        dt_ms = 1000 / 60
        self.animator.update(dt_ms)
        if self.animator.is_animating(): return
        
        if not self.game.has_moves_available():
            self.time_since_last_move += 0.016
            if self.time_since_last_move > 1.0: self._reset_game()
            return
        
        self.time_since_last_move += 0.016
        if self.time_since_last_move >= (1.0 / self.moves_per_second):
            self.time_since_last_move = 0.0
            start_time = time.time()
            move = expectimax_choose_move(self.game, depth=self.depth, weights=self.weights)
            self.last_move_time = time.time() - start_time
            if move:
                old_board = [row[:] for row in self.game.board]
                self.game.move(move)
                self.moves_count += 1
                if self.game.score > self.high_score: self.high_score = self.game.score
                self.animator.start_move_animation(old_board, self.game.board, move)
    
    def draw(self):
        surf = self.surface
        surf.fill(self.bg)
        w, h = surf.get_size()
        
        if self.error_msg:
            font = get_font(30)
            txt = font.render(self.error_msg, False, (255, 0, 0))
            surf.blit(txt, txt.get_rect(center=(w//2, h//2)))
            return
        
        # --- DYNAMIC LAYOUT ---
        layout = calculate_layout(w, h, 4)
        CELL_SIZE = layout["cell_size"]
        MARGIN = layout["margin"]
        board_px = layout["board_size_px"]
        start_x = layout["start_x"]
        
        header_height = int(max(80, h * 0.15))
        start_y = header_height + (h - header_height - board_px) // 2
        
        font_lg = layout["font_large"]
        font_md = layout["font_med"]
        font_sm = layout["font_small"]
        
        # --- HEADER ---
        header_y = int(h * 0.03)
        t_size = int(min(w,h)*0.05) if w > 600 else 20
        title_font = get_font(t_size)
        title_col = self.theme.get("text_light", (255, 255, 255))
        title_txt = title_font.render("EXPECTIMAX", False, title_col)
        surf.blit(title_txt, (int(w*0.04), header_y))
        
        # Score Boxes
        box_w = int(w * 0.15); 
        if box_w < 120: box_w = 120
        box_h = int(box_w * 0.5)
        box_gap = int(w*0.02)
        
        group_x = (w - (box_w*2 + box_gap)) // 2
        
        box_bg = self.theme.get("empty", (100, 100, 100))
        border_col = self.theme.get("border", (0, 0, 0))
        txt_lbl = self.theme.get("text_dark", (200, 200, 200))
        txt_val = self.theme.get("text_light", (255, 255, 255))
        
        def draw_box(l, v, x, y):
            r = pygame.Rect(x, y, box_w, box_h)
            pygame.draw.rect(surf, box_bg, r)
            pygame.draw.rect(surf, border_col, r, 3)
            lf = get_font(int(box_h*0.2)); lt = lf.render(l, False, txt_lbl)
            surf.blit(lt, lt.get_rect(centerx=r.centerx, top=r.top+int(box_h*0.15)))
            vf = get_font(int(box_h*0.35)); vt = vf.render(str(v), False, txt_val)
            surf.blit(vt, vt.get_rect(centerx=r.centerx, bottom=r.bottom-int(box_h*0.1)))
        
        draw_box("SCORE", self.game.score, group_x, header_y)
        draw_box("BEST", self.high_score, group_x + box_w + box_gap, header_y)
        
        # --- BOARD ---
        empty_col = self.theme["empty"]
        pygame.draw.rect(surf, empty_col, (start_x, start_y, board_px, board_px))
        pygame.draw.rect(surf, border_col, (start_x, start_y, board_px, board_px), 3)
        
        def draw_tile(val, x, y, size_px, alpha=255):
            rect = (x, y, size_px, size_px)
            if val == 0: col = empty_col
            else: col = tile_color(val, self.theme_name)
            
            if alpha < 255:
                s = pygame.Surface((size_px, size_px), pygame.SRCALPHA)
                pygame.draw.rect(s, (*col, alpha), (0,0,size_px,size_px))
                if val: pygame.draw.rect(s, (*border_col, alpha), (0,0,size_px,size_px), 2)
                surf.blit(s, (x, y))
            else:
                pygame.draw.rect(surf, col, rect)
                if val: pygame.draw.rect(surf, border_col, rect, 2)
            
            if val:
                t_col, _ = get_tile_text_info(val, self.theme_name)
                if val < 100: f_sz = font_lg
                elif val < 1000: f_sz = font_md
                else: f_sz = font_sm
                if size_px != CELL_SIZE: f_sz = int(f_sz * (size_px/CELL_SIZE))
                
                ft = get_font(f_sz)
                tx = ft.render(str(val), False, t_col)
                surf.blit(tx, tx.get_rect(center=(x+size_px/2, y+size_px/2)))

        # Static Grid
        for r in range(4):
            for c in range(4):
                draw_tile(0, start_x + MARGIN + c*(CELL_SIZE+MARGIN), start_y + MARGIN + r*(CELL_SIZE+MARGIN), CELL_SIZE)
                v = self.game.board[r][c]
                if v and not self.animator.is_animating():
                     draw_tile(v, start_x + MARGIN + c*(CELL_SIZE+MARGIN), start_y + MARGIN + r*(CELL_SIZE+MARGIN), CELL_SIZE)
        
        # Animation
        if self.animator.is_animating():
            tiles = self.animator.get_render_tiles(CELL_SIZE, MARGIN)
            for t in tiles:
                draw_tile(t['value'], 
                          start_x + t['x'], start_y + t['y'], 
                          int(CELL_SIZE*t['scale']), t['alpha'])
        
        # --- SIDE STATS (Restored) ---
        side_f = get_font(int(min(w,h)*0.018))
        if side_f.get_height() < 12: side_f = get_font(12)
        txt_col = self.text_color
        
        # Left Side (Gameplay Stats)
        # Position to the left of board if space permits, else overlay top-left under title?
        # Let's align left, below "AI: Expectimax"
        stats_y = int(h * 0.15)
        left_x = int(w * 0.04)
        
        # If board is huge (small screen), we might overlap. 
        # Check start_x.
        if start_x > 140: # Enough space on left
            stats_list = [
                f"MOVES: {self.moves_count}",
                f"GAMES: {self.games_played}",
                f"DEPTH: {self.depth}",
                f"TARGET: {self.moves_per_second:.1f}/s",
                f"ACTUAL: {1.0/self.last_move_time:.1f}/s" if self.last_move_time>0 else "ACTUAL: --"
            ]
            for s in stats_list:
                t = side_f.render(s, False, txt_col)
                surf.blit(t, (left_x, stats_y))
                stats_y += int(min(w,h)*0.025) + 5
        
        # Right Side (Weights)
        right_x = w - int(w * 0.2) # Roughly
        stats_y = int(h * 0.15)
        
        if w - (start_x + board_px) > 120: # Enough space on right
            w_source = self.weights if self.weights else {"mono":1,"smooth":0.1,"corner":2,"empty":2.5}
            w_lines = [
                "WEIGHTS:",
                f"MONO: {w_source.get('mono',0):.1f}", 
                f"SMTH: {w_source.get('smooth',0):.1f}",
                f"CORN: {w_source.get('corner',0):.1f}",
                f"EMPT: {w_source.get('empty',0):.1f}"
            ]
            for s in w_lines:
                t = side_f.render(s, False, txt_col)
                surf.blit(t, (right_x, stats_y))
                stats_y += int(min(w,h)*0.025) + 5

        # --- CONTROLS GUIDE (Bottom) ---
        ctrl_y = h - 30
        ctrl_font = get_font(int(min(w,h)*0.015))
        if ctrl_font.get_height() < 10: ctrl_font = get_font(10)
        
        info_str = "ARROWS: Speed/Depth | R: Reset | ESC: Menu"
        info_txt = ctrl_font.render(info_str, False, txt_col)
        surf.blit(info_txt, info_txt.get_rect(centerx=w//2, bottom=h - 10))

        # Check Game Over
        if not self.game.has_moves_available():
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surf.blit(overlay, (0,0))
            go = get_font(50).render("GAME OVER", False, (255,50,50))
            surf.blit(go, go.get_rect(center=(w//2, h//2)))

        self.back_button.rect.y = h - 60
        self.back_button.draw(surf)
