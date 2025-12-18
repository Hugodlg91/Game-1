"""
Script to analyze DQN training progress from saved checkpoints.

Shows learning curves and performance improvements over episodes.
"""
import os
from pathlib import Path
import torch
from dqn_agent import DQNAgent, ACTIONS, choose_action_from_dqn
from game_2048 import Game2048
import numpy as np


def analyze_checkpoints(checkpoint_dir="dqn_checkpoints", num_games=10):
    """
    Analyze DQN training progress from checkpoint files.
    
    Args:
        checkpoint_dir: Directory containing .pth checkpoint files
        num_games: Number of games to play per checkpoint for evaluation
    """
    checkpoint_path = Path(checkpoint_dir)
    
    if not checkpoint_path.exists():
        print(f"❌ Checkpoint directory '{checkpoint_dir}' not found!")
        return
    
    # Get all checkpoint files
    checkpoints = sorted([f for f in checkpoint_path.glob("*.pth")])
    
    if not checkpoints:
        print(f"❌ No checkpoint files found in '{checkpoint_dir}'")
        return
    
    print("=" * 70)
    print("DQN TRAINING PROGRESS ANALYSIS")
    print("=" * 70)
    print(f"\nFound {len(checkpoints)} checkpoints\n")
    
    # Analyze each checkpoint
    results = []
    
    for i, checkpoint_file in enumerate(checkpoints):
        episode_num = checkpoint_file.stem.split('_')[-1]
        
        print(f"Analyzing {checkpoint_file.name}...")
        
        # Load model
        agent = DQNAgent()
        try:
            agent.load(str(checkpoint_file))
        except Exception as e:
            print(f"  ⚠️  Error loading: {e}")
            continue
        
        # Play games
        scores = []
        max_tiles = []
        
        for game_num in range(num_games):
            game = Game2048()
            moves = 0
            
            while game.has_moves_available() and moves < 10000:
                action = choose_action_from_dqn(game, agent)
                game.move(action)
                moves += 1
            
            max_tile = max(val for row in game.board for val in row)
            scores.append(game.score)
            max_tiles.append(max_tile)
        
        avg_score = np.mean(scores)
        avg_tile = np.mean(max_tiles)
        best_score = max(scores)
        best_tile = max(max_tiles)
        
        results.append({
            'episode': episode_num,
            'file': checkpoint_file.name,
            'avg_score': avg_score,
            'avg_tile': avg_tile,
            'best_score': best_score,
            'best_tile': best_tile,
            'epsilon': agent.epsilon
        })
        
        print(f"  Avg Score: {avg_score:.1f} | Avg Tile: {avg_tile:.0f} | "
              f"Best: {best_score} ({best_tile}) | ε={agent.epsilon:.3f}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("TRAINING PROGRESS SUMMARY")
    print("=" * 70)
    
    if len(results) >= 2:
        first = results[0]
        last = results[-1]
        
        score_improvement = ((last['avg_score'] - first['avg_score']) / first['avg_score']) * 100
        tile_improvement = ((last['avg_tile'] - first['avg_tile']) / first['avg_tile']) * 100
        
        print(f"\n📊 Progress from Episode {first['episode']} → {last['episode']}:")
        print(f"  Average Score:    {first['avg_score']:.1f} → {last['avg_score']:.1f} "
              f"({score_improvement:+.1f}%)")
        print(f"  Average Max Tile: {first['avg_tile']:.0f} → {last['avg_tile']:.0f} "
              f"({tile_improvement:+.1f}%)")
        print(f"  Best Score:       {first['best_score']} → {last['best_score']}")
        print(f"  Best Tile:        {first['best_tile']} → {last['best_tile']}")
        print(f"  Epsilon:          {first['epsilon']:.3f} → {last['epsilon']:.3f}")
        
        # Learning trend
        if score_improvement > 0:
            print(f"\n✅ Agent is learning! Score improved by {score_improvement:.1f}%")
        else:
            print(f"\n⚠️  No improvement yet. May need more training.")
    
    # Best checkpoint
    best_checkpoint = max(results, key=lambda x: x['avg_score'])
    print(f"\n🏆 Best Checkpoint: {best_checkpoint['file']}")
    print(f"  Average Score: {best_checkpoint['avg_score']:.1f}")
    print(f"  Average Tile:  {best_checkpoint['avg_tile']:.0f}")
    
    return results


def quick_analysis():
    """Quick analysis showing only first and last checkpoints."""
    checkpoint_path = Path("dqn_checkpoints")
    
    if not checkpoint_path.exists():
        print("No checkpoints found. Train the DQN first!")
        return
    
    checkpoints = sorted([f for f in checkpoint_path.glob("dqn_episode_*.pth")])
    
    if len(checkpoints) < 2:
        print(f"Found only {len(checkpoints)} checkpoint(s). Need at least 2 to compare progress.")
        return
    
    print("Quick Progress Check (comparing first vs last checkpoint)")
    print("-" * 70)
    
    for checkpoint_file in [checkpoints[0], checkpoints[-1]]:
        episode = checkpoint_file.stem.split('_')[-1]
        agent = DQNAgent()
        agent.load(str(checkpoint_file))
        
        # Play 5 quick games
        scores = []
        for _ in range(5):
            game = Game2048()
            while game.has_moves_available():
                action = choose_action_from_dqn(game, agent)
                if not game.move(action):
                    break
            scores.append(game.score)
        
        print(f"Episode {episode}: Avg={np.mean(scores):.0f}, Best={max(scores)}, ε={agent.epsilon:.3f}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_analysis()
    else:
        print("Analyzing all checkpoints (this may take a few minutes)...")
        print("For quick analysis, use: python analyze_dqn_progress.py --quick\n")
        analyze_checkpoints(num_games=10)
