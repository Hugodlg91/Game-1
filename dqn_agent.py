"""
Deep Q-Network (DQN) agent for 2048 using PyTorch.

This module implements a neural network-based reinforcement learning agent
that learns to play 2048 from raw grid states without manual heuristics.

Key components:
- DQN neural network (Multi-layer perceptron)
- Experience replay buffer
- Target network for stable training
- Epsilon-greedy exploration
- Training loop with reward shaping
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
import math
from collections import deque, namedtuple
from pathlib import Path
from typing import List, Tuple, Optional

from game_2048 import Game2048

# Actions mapping
ACTIONS = ["up", "down", "left", "right"]

# Transition named tuple for replay memory
Transition = namedtuple('Transition', ('state', 'action', 'reward', 'next_state', 'done'))


# ============================================================================
# NEURAL NETWORK
# ============================================================================

class DQN(nn.Module):
    """
    Deep Q-Network for 2048.
    
    Architecture:
    - Input: 16 values (4x4 grid, preprocessed with log2)
    - Hidden: 2 layers of 128 neurons with ReLU activation
    - Output: 4 Q-values (one per action)
    """
    
    def __init__(self, input_size: int = 16, hidden_sizes: List[int] = None, output_size: int = 4):
        super(DQN, self).__init__()
        
        if hidden_sizes is None:
            hidden_sizes = [128, 128]
        
        layers = []
        prev_size = input_size
        
        # Build hidden layers
        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            prev_size = hidden_size
        
        # Output layer
        layers.append(nn.Linear(prev_size, output_size))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        """Forward pass through the network."""
        return self.network(x)


# ============================================================================
# REPLAY MEMORY
# ============================================================================

class ReplayMemory:
    """
    Experience replay buffer for storing and sampling transitions.
    
    Stores (state, action, reward, next_state, done) tuples and samples
    random batches to break temporal correlations during training.
    """
    
    def __init__(self, capacity: int = 10000):
        self.memory = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """Store a transition in the buffer."""
        self.memory.append(Transition(state, action, reward, next_state, done))
    
    def sample(self, batch_size: int) -> List[Transition]:
        """Sample a random batch of transitions."""
        return random.sample(self.memory, batch_size)
    
    def __len__(self):
        return len(self.memory)


# ============================================================================
# DQN AGENT
# ============================================================================

class DQNAgent:
    """
    Deep Q-Learning agent with experience replay and target network.
    
    Features:
    - Epsilon-greedy exploration
    - Experience replay for stable training
    - Target network updated periodically
    - State preprocessing (log2 normalization)
    """
    
    def __init__(
        self,
        lr: float = 0.001,
        gamma: float = 0.99,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.01,
        epsilon_decay: float = 0.995,
        memory_capacity: int = 10000,
        hidden_sizes: List[int] = None,
        device: str = None
    ):
        """
        Initialize DQN agent.
        
        Args:
            lr: Learning rate for Adam optimizer
            gamma: Discount factor for future rewards
            epsilon_start: Initial exploration rate
            epsilon_end: Minimum exploration rate
            epsilon_decay: Multiplicative decay per episode
            memory_capacity: Size of replay buffer
            hidden_sizes: List of hidden layer sizes (default: [128, 128])
            device: 'cuda' or 'cpu' (auto-detected if None)
        """
        # Device setup
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        print(f"Using device: {self.device}")
        
        # Networks
        self.policy_net = DQN(hidden_sizes=hidden_sizes).to(self.device)
        self.target_net = DQN(hidden_sizes=hidden_sizes).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()  # Target network in eval mode
        
        # Optimizer
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        
        # Replay memory
        self.memory = ReplayMemory(capacity=memory_capacity)
        
        # Hyperparameters
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        
        # Statistics
        self.steps_done = 0
    
    def preprocess_state(self, board: List[List[int]]) -> torch.Tensor:
        """
        Convert 4x4 board to normalized tensor.
        
        Uses log2(value + 1) to normalize tile values to roughly [0, 11] range.
        
        Args:
            board: 4x4 list of tile values
        
        Returns:
            Tensor of shape [16] with normalized values
        """
        state = []
        for row in board:
            for val in row:
                # log2(val + 1) normalization
                normalized = math.log2(val + 1) if val > 0 else 0
                state.append(normalized)
        
        return torch.tensor(state, dtype=torch.float32, device=self.device)
    
    def select_action(self, state: torch.Tensor, epsilon: Optional[float] = None) -> int:
        """
        Select action using epsilon-greedy policy.
        
        Args:
            state: Preprocessed state tensor [16]
            epsilon: Exploration rate (uses self.epsilon if None)
        
        Returns:
            Action index (0=up, 1=down, 2=left, 3=right)
        """
        if epsilon is None:
            epsilon = self.epsilon
        
        # Epsilon-greedy
        if random.random() < epsilon:
            return random.randint(0, 3)
        else:
            with torch.no_grad():
                # Get Q-values and pick best action
                q_values = self.policy_net(state.unsqueeze(0))
                return q_values.argmax(dim=1).item()
    
    def optimize_model(self, batch_size: int = 64):
        """
        Perform one step of optimization on the policy network.
        
        Samples a batch from replay memory and updates the network using
        the Bellman equation: Q(s,a) = r + γ * max_a' Q'(s', a')
        
        Args:
            batch_size: Number of transitions to sample
        """
        if len(self.memory) < batch_size:
            return
        
        # Sample batch
        transitions = self.memory.sample(batch_size)
        batch = Transition(*zip(*transitions))
        
        # Convert to tensors
        state_batch = torch.stack(batch.state)
        action_batch = torch.tensor(batch.action, device=self.device)
        reward_batch = torch.tensor(batch.reward, dtype=torch.float32, device=self.device)
        next_state_batch = torch.stack(batch.next_state)
        done_batch = torch.tensor(batch.done, dtype=torch.bool, device=self.device)
        
        # Compute Q(s, a) - the model computes Q(s), then we select columns of actions taken
        state_action_values = self.policy_net(state_batch).gather(1, action_batch.unsqueeze(1))
        
        # Compute V(s') = max_a Q'(s', a) for all next states using target network
        with torch.no_grad():
            next_state_values = torch.zeros(batch_size, device=self.device)
            # Only compute for non-terminal states
            non_final_mask = ~done_batch
            if non_final_mask.any():
                next_state_values[non_final_mask] = self.target_net(
                    next_state_batch[non_final_mask]
                ).max(1)[0]
        
        # Compute expected Q values: r + γ * max_a' Q'(s', a')
        expected_state_action_values = reward_batch + (self.gamma * next_state_values)
        
        # Compute Huber loss (smoother than MSE for RL)
        loss = nn.functional.smooth_l1_loss(
            state_action_values.squeeze(),
            expected_state_action_values
        )
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping to prevent exploding gradients
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()
        
        self.steps_done += 1
    
    def update_target_network(self):
        """Copy weights from policy network to target network."""
        self.target_net.load_state_dict(self.policy_net.state_dict())
    
    def decay_epsilon(self):
        """Decay epsilon for exploration schedule."""
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
    
    def save(self, path: str):
        """
        Save model and training state to file.
        
        Args:
            path: File path to save to (e.g., 'model.pth')
        """
        torch.save({
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'steps_done': self.steps_done,
        }, path)
        print(f"Model saved to {path}")
    
    def load(self, path: str):
        """
        Load model and training state from file.
        
        Args:
            path: File path to load from
        """
        checkpoint = torch.load(path, map_location=self.device)
        self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.steps_done = checkpoint['steps_done']
        print(f"Model loaded from {path}")


# ============================================================================
# TRAINING UTILITIES
# ============================================================================

def calculate_reward(old_board: List[List[int]], new_board: List[List[int]], 
                    moved: bool, game_over: bool) -> float:
    """
    Calculate reward for a transition.
    
    Reward components:
    1. Score gain from merges
    2. Bonus for high tiles (encourages progress)
    3. Penalty for invalid moves
    4. Penalty for game over (optional)
    
    Args:
        old_board: Board before move
        new_board: Board after move
        moved: Whether the move changed the board
        game_over: Whether game ended
    
    Returns:
        Total reward
    """
    if not moved:
        return -1.0  # Penalty for invalid move
    
    # Calculate score gain (simplified - actual merges)
    old_sum = sum(val for row in old_board for val in row)
    new_sum = sum(val for row in new_board for val in row)
    score_gain = new_sum - old_sum
    
    # Bonus for reaching higher tiles
    max_tile = max(val for row in new_board for val in row)
    tile_bonus = math.log2(max_tile) * 0.1 if max_tile > 0 else 0
    
    # Game over penalty (optional - can help avoid risky moves)
    game_over_penalty = -10.0 if game_over else 0.0
    
    return score_gain + tile_bonus + game_over_penalty


# ============================================================================
# TRAINING LOOP
# ============================================================================

def train_dqn(
    episodes: int = 1000,
    max_steps: int = 10000,
    batch_size: int = 64,
    update_target_every: int = 10,
    save_every: int = 50,
    save_dir: str = "dqn_checkpoints"
) -> DQNAgent:
    """
    Train DQN agent on 2048.
    
    Args:
        episodes: Number of games to play
        max_steps: Maximum steps per episode
        batch_size: Batch size for optimization
        update_target_every: Update target network every N episodes
        save_every: Save checkpoint every N episodes
        save_dir: Directory to save checkpoints
    
    Returns:
        Trained DQNAgent
    """
    # Create save directory
    Path(save_dir).mkdir(exist_ok=True)
    
    # Initialize agent
    agent = DQNAgent()
    
    # Statistics
    episode_scores = []
    episode_max_tiles = []
    
    print(f"Starting DQN training for {episodes} episodes...")
    print(f"Device: {agent.device}")
    print("-" * 60)
    
    for episode in range(episodes):
        # Reset game
        game = Game2048()
        state = agent.preprocess_state(game.board)
        
        episode_reward = 0
        steps = 0
        
        for step in range(max_steps):
            # Select action
            action_idx = agent.select_action(state)
            action = ACTIONS[action_idx]
            
            # Save old board
            old_board = [row[:] for row in game.board]
            
            # Execute action
            moved = game.move(action)
            
            # Calculate reward
            game_over = not game.has_moves_available()
            reward = calculate_reward(old_board, game.board, moved, game_over)
            episode_reward += reward
            
            # Get next state
            next_state = agent.preprocess_state(game.board)
            
            # Store transition
            agent.memory.push(state, action_idx, reward, next_state, game_over)
            
            # Optimize model
            if len(agent.memory) >= batch_size:
                agent.optimize_model(batch_size)
            
            # Move to next state
            state = next_state
            steps += 1
            
            if game_over:
                break
        
        # Episode finished
        max_tile = max(val for row in game.board for val in row)
        episode_scores.append(game.score)
        episode_max_tiles.append(max_tile)
        
        # Decay epsilon
        agent.decay_epsilon()
        
        # Update target network
        if episode % update_target_every == 0:
            agent.update_target_network()
        
        # Print progress
        if (episode + 1) % 10 == 0:
            avg_score = np.mean(episode_scores[-10:])
            avg_max_tile = np.mean(episode_max_tiles[-10:])
            print(f"Episode {episode + 1}/{episodes} | "
                  f"Avg Score: {avg_score:.1f} | "
                  f"Avg Max Tile: {avg_max_tile:.0f} | "
                  f"Epsilon: {agent.epsilon:.3f} | "
                  f"Memory: {len(agent.memory)}")
        
        # Save checkpoint
        if (episode + 1) % save_every == 0:
            save_path = Path(save_dir) / f"dqn_episode_{episode + 1}.pth"
            agent.save(str(save_path))
    
    # Final save
    final_path = Path(save_dir) / "dqn_final.pth"
    agent.save(str(final_path))
    
    print("-" * 60)
    print("Training complete!")
    print(f"Final epsilon: {agent.epsilon:.3f}")
    print(f"Average score (last 100): {np.mean(episode_scores[-100:]):.1f}")
    print(f"Best score: {max(episode_scores)}")
    
    return agent


# ============================================================================
# INCREMENTAL TRAINER FOR UI
# ============================================================================

class DQNTrainer:
    """
    Incremental DQN trainer for UI integration.
    
    Similar to q_learning_agent.Trainer, performs training step-by-step
    so the UI can remain responsive.
    """
    
    def __init__(
        self,
        episodes: int = 1000,
        batch_size: int = 64,
        update_target_every: int = 10,
        save_every: int = 50
    ):
        self.agent = DQNAgent()
        self.episodes = episodes
        self.batch_size = batch_size
        self.update_target_every = update_target_every
        self.save_every = save_every
        
        # Episode state
        self.episode = 0
        self.step_in_episode = 0
        self.game = Game2048()
        self.state = self.agent.preprocess_state(self.game.board)
        
        # Statistics
        self.episode_scores = []
        self.episode_max_tiles = []
        self.current_episode_reward = 0
    
    def step(self) -> bool:
        """
        Perform one training step.
        
        Returns:
            True if training is complete
        """
        if self.episode >= self.episodes:
            return True
        
        # Select and execute action
        action_idx = self.agent.select_action(self.state)
        action = ACTIONS[action_idx]
        
        old_board = [row[:] for row in self.game.board]
        moved = self.game.move(action)
        
        # Calculate reward
        game_over = not self.game.has_moves_available()
        reward = calculate_reward(old_board, self.game.board, moved, game_over)
        self.current_episode_reward += reward
        
        # Get next state
        next_state = self.agent.preprocess_state(self.game.board)
        
        # Store and optimize
        self.agent.memory.push(self.state, action_idx, reward, next_state, game_over)
        
        if len(self.agent.memory) >= self.batch_size:
            self.agent.optimize_model(self.batch_size)
        
        self.state = next_state
        self.step_in_episode += 1
        
        # Check if episode done
        if game_over or self.step_in_episode > 10000:
            # Record stats
            max_tile = max(val for row in self.game.board for val in row)
            self.episode_scores.append(self.game.score)
            self.episode_max_tiles.append(max_tile)
            
            # Decay epsilon
            self.agent.decay_epsilon()
            
            # Update target network
            if self.episode % self.update_target_every == 0:
                self.agent.update_target_network()
            
            # Save checkpoint
            if (self.episode + 1) % self.save_every == 0:
                Path("dqn_checkpoints").mkdir(exist_ok=True)
                self.agent.save(f"dqn_checkpoints/dqn_episode_{self.episode + 1}.pth")
            
            # Reset for next episode
            self.episode += 1
            self.step_in_episode = 0
            self.current_episode_reward = 0
            self.game = Game2048()
            self.state = self.agent.preprocess_state(self.game.board)
        
        return self.episode >= self.episodes
    
    def status(self):
        """Get current training status."""
        avg_score = np.mean(self.episode_scores[-10:]) if self.episode_scores else 0
        avg_max_tile = np.mean(self.episode_max_tiles[-10:]) if self.episode_max_tiles else 0
        
        return {
            'episode': self.episode,
            'episodes': self.episodes,
            'step': self.step_in_episode,
            'epsilon': self.agent.epsilon,
            'memory_size': len(self.agent.memory),
            'avg_score': avg_score,
            'avg_max_tile': avg_max_tile,
        }
    
    def current_board(self):
        """Get current game board for visualization."""
        return self.game.board


# ============================================================================
# PLAY WITH TRAINED MODEL
# ============================================================================

def choose_action_from_dqn(game: Game2048, agent: DQNAgent) -> str:
    """
    Choose action using trained DQN agent (greedy policy).
    
    Args:
        game: Current game state
        agent: Trained DQN agent
    
    Returns:
        Action string ("up", "down", "left", "right")
    """
    state = agent.preprocess_state(game.board)
    action_idx = agent.select_action(state, epsilon=0.0)  # Greedy (no exploration)
    return ACTIONS[action_idx]


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Train for a small number of episodes
    print("DQN Agent for 2048")
    print("=" * 60)
    print()
    
    # Quick test training
    print("Running quick training test (10 episodes)...")
    agent = train_dqn(episodes=10, save_every=5, save_dir="dqn_test")
    
    print("\nTest complete! To train for real, run:")
    print("  from dqn_agent import train_dqn")
    print("  agent = train_dqn(episodes=1000)")
