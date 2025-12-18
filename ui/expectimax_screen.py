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
            if event.key == pygame.K_UP:
                # Increase speed
                self.moves_per_second = min(10.0, self.moves_per_second + 0.5)
            elif event.key == pygame.K_DOWN:
                # Decrease speed
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
        
        # Update animations
        self.animator.update()
        
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
            
            # Get AI move
            move = expectimax_choose_move(
                self.game,
                depth=self.depth,
                weights=self.weights
            )
            
            if move:
                # Capture old state for animation
                old_board = [row[:] for row in self.game.board]
                
                # Execute move
                self.game.move(move)
                self.moves_count += 1
                
                # Start animation
                self.animator.start_animation(old_board, self.game.board)
    
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
        
        stats = [
            f"Score: {self.game.score}",
            f"Moves: {self.moves_count}",
            f"Games: {self.games_played}",
            "",
            f"Depth: {self.depth}",
            f"Speed: {self.moves_per_second:.1f} moves/sec",
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
        
        # Controls
        controls_font = pygame.font.Font(None, 20)
        controls_y = surf.get_height() - 70
        controls = [
            "Controls: ↑↓ Speed | ←→ Depth | R: Reset | ESC: Menu",
        ]
        
        if not self.game.has_moves_available():
            controls.append("GAME OVER - Auto-restarting...")
        
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
        
        # Get animated board (or current board if not animating)
        if self.animator.is_animating():
            display_board = self.animator.get_interpolated_board()
        else:
            display_board = self.game.board
        
        # Draw tiles
        for i in range(4):
            for j in range(4):
                value = display_board[i][j]
                rect = pygame.Rect(
                    x + gap + j * (cell_size + gap),
                    y + gap + i * (cell_size + gap),
                    cell_size,
                    cell_size
                )
                
                # Color
                color = EMPTY_COLOR if value == 0 else tile_color(value)
                pygame.draw.rect(screen, color, rect, border_radius=8)
                
                # Value
                if value != 0:
                    font_size = 48 if value < 1000 else 40 if value < 10000 else 32
                    font = pygame.font.Font(None, font_size)
                    text_color = (119, 110, 101) if value <= 4 else (249, 246, 242)
                    text = font.render(str(value), True, text_color)
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
