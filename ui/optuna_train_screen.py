"""
DQN Optimized Training Screen - Uses best hyperparameters from Optuna.
"""
import pygame
import json
from pathlib import Path
from ui.screens import Screen
from dqn_agent import DQNAgent, ACTIONS, calculate_reward
from game_2048 import Game2048
import numpy as np


class OptunaTrainScreen(Screen):
    """Training screen using Optuna-optimized hyperparameters."""
    
    def __init__(self, manager):
        super().__init__(manager)
        
        # Load best hyperparameters
        params_file = Path("optuna_results/best_hyperparameters.json")
        if not params_file.exists():
            self.error_msg = "No Optuna results found! Run optimize_dqn.py first."
            self.agent = None
            return
        
        with open(params_file, 'r') as f:
            params = json.load(f)
        
        # Extract architecture
        n_layers = params['n_layers']
        hidden_sizes = [params[f'n_units_l{i}'] for i in range(n_layers)]
        
        # Create agent with optimized params
        self.agent = DQNAgent(
            lr=params['lr'],
            gamma=params['gamma'],
            memory_capacity=params['memory_capacity'],
            hidden_sizes=hidden_sizes
        )
        
        self.batch_size = params['batch_size']
        self.target_update = params['target_update']
        
        # Training state
        self.episode = 0
        self.max_episodes = 5000  # Can be changed
        self.step_in_episode = 0
        self.game = Game2048()
        self.state = self.agent.preprocess_state(self.game.board)
        
        # Statistics
        self.episode_scores = []
        self.episode_max_tiles = []
        
        # UI control
        self.paused = False
        self.speed = 5  # steps per frame (1-10)
        
        # Save settings
        self.save_dir = Path("optuna_results/best_model")
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        self.error_msg = None
        
        # Display params
        self.params_display = params
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from ui.menu import MainMenuScreen
                self.manager.set_screen(MainMenuScreen(self.manager))
            elif event.key == pygame.K_SPACE:
                self.paused = not self.paused
            elif event.key == pygame.K_UP:
                self.speed = min(100, self.speed + 5)  # +5 per press, max 100
            elif event.key == pygame.K_DOWN:
                self.speed = max(1, self.speed - 5)  # -5 per press, min 1
            elif event.key == pygame.K_PAGEUP:
                self.speed = min(100, self.speed + 20)  # Fast increase
            elif event.key == pygame.K_PAGEDOWN:
                self.speed = max(1, self.speed - 20)  # Fast decrease
    
    def update(self):
        if self.agent is None or self.paused:
            return
        
        # Training steps
        for _ in range(self.speed):
            if self.episode >= self.max_episodes:
                return
            
            # Select action
            action_idx = self.agent.select_action(self.state)
            action = ACTIONS[action_idx]
            
            # Execute
            old_board = [row[:] for row in self.game.board]
            moved = self.game.move(action)
            game_over = not self.game.has_moves_available()
            
            # Reward
            reward = calculate_reward(old_board, self.game.board, moved, game_over)
            next_state = self.agent.preprocess_state(self.game.board)
            
            # Store
            self.agent.memory.push(self.state, action_idx, reward, next_state, game_over)
            
            # Optimize
            if len(self.agent.memory) >= self.batch_size:
                self.agent.optimize_model(self.batch_size)
            
            self.state = next_state
            self.step_in_episode += 1
            
            # Episode end
            if game_over or self.step_in_episode > 10000:
                max_tile = max(val for row in self.game.board for val in row)
                self.episode_scores.append(self.game.score)
                self.episode_max_tiles.append(max_tile)
                
                # Decay epsilon
                self.agent.decay_epsilon()
                
                # Update target network
                if self.episode % self.target_update == 0:
                    self.agent.update_target_network()
                
                # Save checkpoint
                if (self.episode + 1) % 50 == 0:
                    save_path = self.save_dir / f"optuna_best_ep_{self.episode + 1}.pth"
                    self.agent.save(str(save_path))
                
                # Reset
                self.episode += 1
                self.step_in_episode = 0
                self.game = Game2048()
                self.state = self.agent.preprocess_state(self.game.board)
    
    def draw(self):
        screen = self.manager.surface
        screen.fill((250, 248, 239))
        
        if self.error_msg:
            # Show error
            font = pygame.font.Font(None, 36)
            text = font.render(self.error_msg, True, (119, 110, 101))
            rect = text.get_rect(center=(screen.get_width() // 2, 200))
            screen.blit(text, rect)
            
            hint_font = pygame.font.Font(None, 24)
            hint = hint_font.render("Press ESC to return to menu", True, (119, 110, 101))
            hint_rect = hint.get_rect(center=(screen.get_width() // 2, 250))
            screen.blit(hint, hint_rect)
            return
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("DQN Training (Optuna Optimized)", True, (119, 110, 101))
        title_rect = title.get_rect(centerx=screen.get_width() // 2, y=20)
        screen.blit(title, title_rect)
        
        # Stats (left column)
        stats_font = pygame.font.Font(None, 28)
        y = 90
        x_left = 30
        
        stats = [
            f"Episode: {self.episode}/{self.max_episodes}",
            f"Step: {self.step_in_episode}",
            f"Epsilon: {self.agent.epsilon:.3f}",
            f"Memory: {len(self.agent.memory)}/{self.agent.memory.memory.maxlen}",
            "",
            f"Avg Score (50): {np.mean(self.episode_scores[-50:]):.1f}" if len(self.episode_scores) >= 50 else "Avg Score: N/A",
            f"Avg Tile (50): {np.mean(self.episode_max_tiles[-50:]):.0f}" if len(self.episode_max_tiles) >= 50 else "Avg Tile: N/A",
            f"Current Score: {self.game.score}",
            "",
            f"Speed: {self.speed}x {'(PAUSED)' if self.paused else ''}",
        ]
        
        for stat in stats:
            text = stats_font.render(stat, True, (119, 110, 101))
            screen.blit(text, (x_left, y))
            y += 35
        
        # Optimized params (right column)
        params_font = pygame.font.Font(None, 26)
        y = 90
        x_right = screen.get_width() - 380
        
        param_title = pygame.font.Font(None, 32)
        title_text = param_title.render("Optimized Parameters:", True, (119, 110, 101))
        screen.blit(title_text, (x_right, y))
        y += 45
        
        if self.params_display:
            param_lines = [
                f"LR: {self.params_display['lr']:.6f}",
                f"Gamma: {self.params_display['gamma']:.4f}",
                f"Batch: {self.params_display['batch_size']}",
                f"Memory: {self.params_display['memory_capacity']}",
                f"Target Update: {self.params_display['target_update']}",
                f"Layers: {self.params_display['n_layers']}",
            ]
            
            # Add layer sizes
            for i in range(self.params_display['n_layers']):
                param_lines.append(f"  L{i}: {self.params_display[f'n_units_l{i}']} units")
            
            for line in param_lines:
                text = params_font.render(line, True, (119, 110, 101))
                screen.blit(text, (x_right, y))
                y += 32
        
        # Current board (centered below stats)
        board_y = 500
        self._draw_board(screen, board_y)
        
        # Controls (bottom)
        controls_font = pygame.font.Font(None, 22)
        controls_y = screen.get_height() - 35
        controls = "ESC: Menu | SPACE: Pause | ↑↓: Speed ±5 | PgUp/PgDn: Speed ±20"
        controls_text = controls_font.render(controls, True, (119, 110, 101))
        controls_rect = controls_text.get_rect(centerx=screen.get_width() // 2, y=controls_y)
        screen.blit(controls_text, controls_rect)
    
    def _draw_board(self, screen, y):
        """Draw current game board centered."""
        cell_size = 70
        gap = 12
        board_size = 4 * cell_size + 5 * gap
        
        # Center horizontally
        x = (screen.get_width() - board_size) // 2
        
        # Background
        board_bg = pygame.Rect(x, y, board_size, board_size)
        pygame.draw.rect(screen, (187, 173, 160), board_bg, border_radius=8)
        
        # Tiles
        for i in range(4):
            for j in range(4):
                value = self.game.board[i][j]
                rect = pygame.Rect(
                    x + gap + j * (cell_size + gap),
                    y + gap + i * (cell_size + gap),
                    cell_size,
                    cell_size
                )
                
                # Color
                colors = {
                    0: (205, 193, 180),
                    2: (238, 228, 218),
                    4: (237, 224, 200),
                    8: (242, 177, 121),
                    16: (245, 149, 99),
                    32: (246, 124, 95),
                    64: (246, 94, 59),
                    128: (237, 207, 114),
                    256: (237, 204, 97),
                    512: (237, 200, 80),
                    1024: (237, 197, 63),
                    2048: (237, 194, 46),
                }
                color = colors.get(value, (60, 58, 50))
                pygame.draw.rect(screen, color, rect, border_radius=5)
                
                # Value
                if value != 0:
                    font_size = 42 if value < 1000 else 36 if value < 10000 else 28
                    font = pygame.font.Font(None, font_size)
                    text_color = (119, 110, 101) if value <= 4 else (249, 246, 242)
                    text = font.render(str(value), True, text_color)
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
