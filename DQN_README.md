# DQN Agent for 2048 - Quick Start Guide

## Overview

Deep Q-Network (DQN) agent using PyTorch that learns to play 2048 from raw grid states without manual heuristics.

## Installation

Dependencies are already added to `requirements.txt`:
```bash
.\.venv\Scripts\pip install torch numpy
```

## Quick Start

### 1. Train a New Agent

```python
from dqn_agent import train_dqn

# Train for 1000 episodes (recommended)
agent = train_dqn(episodes=1000, save_dir="my_dqn_model")
```

**Training time**: ~1-4 hours for 1000 episodes on CPU

### 2. Use Trained Agent

```python
from dqn_agent import DQNAgent, choose_action_from_dqn
from game_2048 import Game2048

# Load trained agent
agent = DQNAgent()
agent.load("my_dqn_model/dqn_final.pth")

# Play a game
game = Game2048()
while game.has_moves_available():
    action = choose_action_from_dqn(game, agent)
    game.move(action)

print(f"Final score: {game.score}")
```

### 3. Run Demo

```bash
.\.venv\Scripts\python demo_dqn.py
```

Choose from:
- Train new agent (50 episodes - quick test)
- Play with trained agent
- Compare DQN vs Heuristic AI
- Extended training (200 episodes)

## Architecture

### Neural Network
- **Input**: 16 values (4×4 grid, log2 normalized)
- **Hidden**: 2 layers × 128 neurons + ReLU
- **Output**: 4 Q-values (up, down, left, right)

### Key Features
- **Experience Replay**: 10K transition buffer
- **Target Network**: Updated every 10 episodes
- **Epsilon-Greedy**: 1.0 → 0.01 decay
- **Optimizer**: Adam (lr=0.001)
- **Loss**: Smooth L1 (Huber loss)

## Files Created

- **dqn_agent.py**: Complete DQN implementation
- **demo_dqn.py**: Demo and comparison scripts
- **dqn_checkpoints/**: Training checkpoints (auto-created)

## Training Tips

### Hyperparameters

Default values work well, but you can adjust:

```python
agent = train_dqn(
    episodes=1000,           # More = better (1000-5000 recommended)
    batch_size=64,           # Larger = more stable
    update_target_every=10,  # Lower = more stable, higher = faster
    save_every=50           # Checkpoint frequency
)
```

### Monitoring Progress

Training prints progress every 10 episodes:
```
Episode 100/1000 | Avg Score: 2456.3 | Avg Max Tile: 256 | Epsilon: 0.605
```

Look for:
- ✅ **Increasing scores** over time
- ✅ **Higher max tiles** (128 → 256 → 512)
- ✅ **Decreasing epsilon** (1.0 → 0.01)

### Performance Expectations

After training:
- **100 episodes**: Basic strategy, avg score ~1500-2500
- **500 episodes**: Good performance, avg score ~3000-5000
- **1000+ episodes**: Strong play, reaching 512-1024 tiles regularly

## Integration with UI

Use the `DQNTrainer` class for incremental training in the UI:

```python
from dqn_agent import DQNTrainer

trainer = DQNTrainer(episodes=1000)

# In your UI update loop:
def update(self):
    finished = trainer.step()
    if finished:
        print("Training complete!")
    
    # Display current game
    board = trainer.current_board()
    
    # Show
 stats
    status = trainer.status()
    print(f"Episode: {status['episode']}, Epsilon: {status['epsilon']:.3f}")
```

## Comparison with Other AIs

| AI Type | Speed | Quality | Training Required |
|---------|-------|---------|-------------------|
| Heuristic | Very fast | Good | None |
| Expectimax | Slow | Excellent | None |
| Q-Learning | Fast | Decent | Hours (tabular) |
| **DQN** | Fast | **Good-Excellent** | **Hours-Days** |

DQN advantages:
- ✅ Learns from raw state (no feature engineering)
- ✅ Scalable (can handle complex patterns)
- ✅ Improves with more training

## Troubleshooting

### Out of Memory
- Reduce `batch_size` (try 32 or 16)
- Reduce `memory_capacity` in DQNAgent init

### Slow Training
- Training on CPU is slow but functional
- GPU would be much faster (requires CUDA-enabled PyTorch)

### Poor Performance
- Train for more episodes (1000+ recommended)
- Check that epsilon is decaying properly
- Verify checkpoints are being saved

## Advanced Usage

### Custom Reward Shaping

Edit `calculate_reward()` in `dqn_agent.py`:

```python
def calculate_reward(old_board, new_board, moved, game_over):
    # Add your custom reward logic
    # Example: bonus for keeping max tile in corner
    pass
```

### Load Checkpoint and Continue Training

```python
agent = DQNAgent()
agent.load("dqn_checkpoints/dqn_episode_500.pth")

# Continue training
# (manually implement or modify train_dqn function)
```

## Next Steps

1. **Train longer**: 1000-5000 episodes for best results
2. **Experiment with hyperparameters**: Try different learning rates, batch sizes
3. **Add to UI**: Integrate `DQNTrainer` into a new screen
4. **Compare**: Benchmark against Expectimax and heuristic AIs

Good luck training! 🚀
