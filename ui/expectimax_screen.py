"""
Expectimax AI autoplay screen.

Automatically loads optimized weights from Optuna if available,
otherwise uses default weights.
"""
from __future__ import annotations

import pygame
import json
from pathlib import Path
from ui.screens import Screen
from ui.buttons import Button
from ui.animations import TileAnimator
from ui.ui_utils import tile_color, EMPTY_COLOR
from game_2048 import Game2048
from ai_player import expectimax_choose_move, BITBOARD_AVAILABLE


class ExpectimaxScreen(Screen):
    """
    Screen showing Expectimax AI playing automatically.
    
    Features:
    - Auto-loads optimized weights from expectimax_optuna_results/best_weights.json
    - Falls back to default weights if file not found
    - Smooth tile animations
    - Displays current weights and performance stats
    - Configurable depth and speed
    """
    
    def __init__(self, manager):
        super().__init__(manager)
        
        if not BITBOARD_AVAILABLE:
            self.error_msg = "Bitboard module not available. Cannot use Expectimax AI."
            self.game = None
            return
        
        self.surface = manager.surface
        self.bg = (187, 173, 160)
        w, h = self.surface.get_size()
        
        # Back button
        self.back_button = Button(
            pygame.Rect(20, h - 60, 120, 40),
            "Back",
            lambda: manager.set_screen(__import__("ui.menu").menu.MainMenuScreen(manager))
        )
        
        # Load optimized weights if available
        self.weights = self._load_optimized_weights()
        self.weights_source = "Optuna Optimized" if self.weights else "Default"
        
        # Game state
        self.game = Game2048()
        self.animator = TileAnimator()
        
        # AI settings
        self.depth = 3  # Can be adjusted
        self.moves_per_second = 2.0
        self.time_since_last_move = 0.0
        
        # Statistics
        self.moves_count = 0
        self.games_played = 0
        self.total_score = 0
        self.last_move_time = 0.0  # Track actual move calculation time
        
        self.error_msg = None
    
    def _load_optimized_weights(self) -> dict | None:
        """Load optimized weights from Optuna results if available."""
        weights_file = Path("expectimax_optuna_results/best_weights.json")
        
        if weights_file.exists():
            try:
                with open(weights_file, 'r') as f:
                    weights = json.load(f)
                print(f"✓ Loaded optimized Expectimax weights: {weights}")
                return weights
            except Exception as e:
                print(f"⚠ Failed to load weights: {e}")
                return None
        else:
            print("ℹ No optimized weights found, using defaults")
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
                # Return to menu
                from ui.menu import MainMenuScreen
                self.manager.set_screen(MainMenuScreen(self.manager))
            elif event.key == pygame.K_UP:
                # Increase speed target
                self.moves_per_second = min(10.0, self.moves_per_second + 0.5)
            elif event.key == pygame.K_DOWN:
                # Decrease speed target
                self.moves_per_second = max(0.5, self.moves_per_second - 0.5)
            elif event.key == pygame.K_LEFT:
                # Decrease depth
                self.depth = max(2, self.depth - 1)
            elif event.key == pygame.K_RIGHT:
                # Increase depth
                self.depth = min(5, self.depth + 1)
            elif event.key == pygame.K_r:
                # Reset game
                self._reset_game()
    
    def _reset_game(self):
        """Start a new game."""
        if self.game and self.game.score > 0:
            self.total_score += self.game.score
            self.games_played += 1
        
        self.game = Game2048()
        self.animator = TileAnimator()
        self.moves_count = 0
        self.time_since_last_move = 0.0
    
    def update(self):
        if self.game is None:
            return
        
        # Update animations (60 FPS)
        dt_ms = 1000 / 60
        self.animator.update(dt_ms)
        
        # Skip if animating
        if self.animator.is_animating():
            return
        
        # Check if game over
        if not self.game.has_moves_available():
            # Auto-restart after 1 second
            self.time_since_last_move += 0.016  # ~60 FPS
            if self.time_since_last_move > 1.0:
                self._reset_game()
            return
        
        # Time-based move execution
        self.time_since_last_move += 0.016  # ~60 FPS
        
        if self.time_since_last_move >= (1.0 / self.moves_per_second):
            self.time_since_last_move = 0.0
            
            # Track move calculation time
            import time
            start_time = time.time()
            
            # Get AI move
            move = expectimax_choose_move(
                self.game,
                depth=self.depth,
                weights=self.weights
            )
            
            # Record actual calculation time
            self.last_move_time = time.time() - start_time
            
            if move:
                # Capture old state for animation
                old_board = [row[:] for row in self.game.board]
                
                # Execute move
                self.game.move(move)
                self.moves_count += 1
                
                # Start animation with direction
                self.animator.start_move_animation(old_board, self.game.board, move)
    
    def draw(self):
        surf = self.surface
        surf.fill(self.bg)
        
        if self.error_msg:
            # Show error
            font = pygame.font.Font(None, 36)
            text = font.render(self.error_msg, True, (119, 110, 101))
            rect = text.get_rect(center=(surf.get_width() // 2, 200))
            surf.blit(text, rect)
            
            hint_font = pygame.font.Font(None, 24)
            hint = hint_font.render("Press ESC to return to menu", True, (119, 110, 101))
            hint_rect = hint.get_rect(center=(surf.get_width() // 2, 250))
            surf.blit(hint, hint_rect)
            return
        
        # Title
        title_font = pygame.font.Font(None, 42)
        title = title_font.render(f"Expectimax AI ({self.weights_source})", True, (119, 110, 101))
        title_rect = title.get_rect(centerx=surf.get_width() // 2, y=10)
        surf.blit(title, title_rect)
        
        # Stats panel (left side)
        stats_font = pygame.font.Font(None, 26)
        y = 60
        x_left = 20
        
        # Calculate actual speed
        actual_speed = f"{1.0/self.last_move_time:.1f}" if self.last_move_time > 0 else "--"
        
        stats = [
            f"Score: {self.game.score}",
            f"Moves: {self.moves_count}",
            f"Games: {self.games_played}",
            "",
            f"Depth: {self.depth}",
            f"Target: {self.moves_per_second:.1f} moves/s",
            f"Actual: {actual_speed} moves/s",
            f"Calc: {self.last_move_time:.2f}s/move" if self.last_move_time > 0 else "Calc: --",
        ]
        
        if self.games_played > 0:
            stats.insert(3, f"Avg Score: {self.total_score / self.games_played:.0f}")
        
        for stat in stats:
            text = stats_font.render(stat, True, (119, 110, 101))
            surf.blit(text, (x_left, y))
            y += 32
        
        # Weights panel (right side)
        y = 60
        x_right = surf.get_width() - 300
        
        weights_title = pygame.font.Font(None, 28)
        title_text = weights_title.render("Heuristic Weights:", True, (119, 110, 101))
        surf.blit(title_text, (x_right, y))
        y += 35
        
        # Display weights (optimized or default)
        if self.weights:
            weight_lines = [
                f"Monotonicity: {self.weights.get('mono', 1.0):.2f}",
                f"Smoothness: {self.weights.get('smooth', 0.1):.2f}",
                f"Corner: {self.weights.get('corner', 2.0):.2f}",
                f"Empty: {self.weights.get('empty', 2.5):.2f}",
            ]
        else:
            weight_lines = [
                "Monotonicity: 1.00 (default)",
                "Smoothness: 0.10 (default)",
                "Corner: 2.00 (default)",
                "Empty: 2.50 (default)",
            ]
        
        weight_font = pygame.font.Font(None, 22)
        for line in weight_lines:
            text = weight_font.render(line, True, (119, 110, 101))
            surf.blit(text, (x_right, y))
            y += 28
        
        # Game board (centered)
        board_y = 260
        self._draw_board(surf, board_y)
        
        # Controls (split into multiple lines for better visibility)
        controls_font = pygame.font.Font(None, 22)
        controls_y = surf.get_height() - 80
        
        if not self.game.has_moves_available():
            # Game over message
            text = controls_font.render("GAME OVER - Auto-restarting...", True, (200, 50, 50))
            text_rect = text.get_rect(centerx=surf.get_width() // 2, y=controls_y)
            surf.blit(text, text_rect)
        else:
            # Normal controls display (ASCII only for compatibility)
            controls = [
                "UP/DOWN: Speed  |  LEFT/RIGHT: Depth  |  R: Reset  |  ESC: Menu"
            ]
            
            for i, ctrl in enumerate(controls):
                text = controls_font.render(ctrl, True, (119, 110, 101))
                text_rect = text.get_rect(centerx=surf.get_width() // 2, y=controls_y + i * 25)
                surf.blit(text, text_rect)
    
    def _draw_board(self, screen, y):
        """Draw the game board with animations."""
        cell_size = 90
        gap = 15
        board_size = 4 * cell_size + 5 * gap
        
        # Center horizontally
        x = (screen.get_width() - board_size) // 2
        
        # Background
        board_bg = pygame.Rect(x, y, board_size, board_size)
        pygame.draw.rect(screen, (187, 173, 160), board_bg, border_radius=10)
        
        # Draw empty cell backgrounds
        for i in range(4):
            for j in range(4):
                rect = pygame.Rect(
                    x + gap + j * (cell_size + gap),
                    y + gap + i * (cell_size + gap),
                    cell_size,
                    cell_size
                )
                pygame.draw.rect(screen, EMPTY_COLOR, rect, border_radius=8)
        
        # Draw tiles (animated or static)
        if self.animator.is_animating():
            # Get animated tiles
            tiles_to_render = self.animator.get_render_tiles(cell_size, gap)
            
            for tile_data in tiles_to_render:
                value = tile_data['value']
                tile_x = x + tile_data['x']
                tile_y = y + tile_data['y']
                scale = tile_data['scale']
                alpha = tile_data['alpha']
                
                # Calculate scaled size
                scaled_size = cell_size * scale
                offset = (cell_size - scaled_size) / 2
                
                # Draw tile
                color = tile_color(value)
                tile_surf = pygame.Surface((scaled_size, scaled_size), pygame.SRCALPHA)
                pygame.draw.rect(tile_surf, (*color, alpha), (0, 0, scaled_size, scaled_size), border_radius=int(8 * scale))
                
                # Draw number
                if value and alpha > 50:
                    font_size = int((48 if value < 1000 else 40 if value < 10000 else 32) * scale)
                    font = pygame.font.Font(None, font_size)
                    text_color = (119, 110, 101) if value <= 4 else (249, 246, 242)
                    text = font.render(str(value), True, text_color)
                    text_rect = text.get_rect(center=(scaled_size/2, scaled_size/2))
                    tile_surf.blit(text, text_rect)
                
                screen.blit(tile_surf, (tile_x + offset, tile_y + offset))
        else:
            # Static rendering when not animating
            for i in range(4):
                for j in range(4):
                    value = self.game.board[i][j]
                    if value == 0:
                        continue
                    
                    rect = pygame.Rect(
                        x + gap + j * (cell_size + gap),
                        y + gap + i * (cell_size + gap),
                        cell_size,
                        cell_size
                    )
                    
                    # Color
                    color = tile_color(value)
                    pygame.draw.rect(screen, color, rect, border_radius=8)
                    
                    # Value
                    font_size = 48 if value < 1000 else 40 if value < 10000 else 32
                    font = pygame.font.Font(None, font_size)
                    text_color = (119, 110, 101) if value <= 4 else (249, 246, 242)
                    text = font.render(str(value), True, text_color)
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
