"""
Quick training script for DQN - Optimized for speed and longer training.

This script continues training from the last checkpoint and saves progress regularly.
"""
from pathlib import Path
import torch
from dqn_agent import DQNAgent, train_dqn

def continue_training(episodes=2000, checkpoint_dir="dqn_checkpoints"):
    """
    Continue training from last checkpoint or start fresh.
    
    Args:
        episodes: Total episodes to train
        checkpoint_dir: Directory with checkpoints
    """
    checkpoint_path = Path(checkpoint_dir)
    
    # Find last checkpoint
    if checkpoint_path.exists():
        checkpoints = sorted([f for f in checkpoint_path.glob("dqn_episode_*.pth")])
        if checkpoints:
            last_checkpoint = checkpoints[-1]
            episode_num = int(last_checkpoint.stem.split('_')[-1])
            print(f"Found checkpoint at episode {episode_num}")
            print(f"Continuing training for {episodes} more episodes...\n")
        else:
            print("No checkpoints found. Starting fresh training...\n")
    else:
        print("Starting fresh training...\n")
    
    # Train
    train_dqn(
        episodes=episodes,
        batch_size=128,  # Larger for faster training
        update_target_every=10,
        save_every=50,
        save_dir=checkpoint_dir
    )

if __name__ == "__main__":
    import sys
    
    # Default: 2000 episodes
    episodes = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    
    print("=" * 70)
    print(f"DQN EXTENDED TRAINING - {episodes} EPISODES")
    print("=" * 70)
    print("\nOptimizations:")
    print("  - Larger batch size (128) for faster learning")
    print("  - Saves every 50 episodes")
    print("  - Can be interrupted with Ctrl+C (progress saved)")
    print()
    
    try:
        continue_training(episodes=episodes)
    except KeyboardInterrupt:
        print("\n\nTraining interrupted. Progress saved!")
