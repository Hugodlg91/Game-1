"""
Demo script for DQN agent training and evaluation.

This script provides easy-to-use functions for:
- Training a new DQN agent
- Loading and testing a trained agent
- Comparing DQN performance with other AIs
"""
from dqn_agent import train_dqn, DQNAgent, choose_action_from_dqn
from game_2048 import Game2048
import ai_player
import time


def demo_train():
    """Demonstrate DQN training with a small number of episodes."""
    print("=" * 70)
    print("DQN TRAINING DEMO")
    print("=" * 70)
    print("\nThis will train a DQN agent for 50 episodes (~5-10 minutes)")
    print("For better results, train for 1000+ episodes (several hours)\n")
    
    response = input("Continue? (y/n, default=y): ").strip().lower()
    if response in ["n", "no"]:
        print("Training cancelled.")
        return
    
    # Train
    agent = train_dqn(
        episodes=50,
        batch_size=32,
        update_target_every=5,
        save_every=10,
        save_dir="dqn_demo"
    )
    
    print("\nTraining complete! Model saved to dqn_demo/dqn_final.pth")
    return agent


def demo_play(model_path="dqn_demo/dqn_final.pth", num_games=5):
    """
    Play games using a trained DQN agent.
    
    Args:
        model_path: Path to trained model
        num_games: Number of games to play
    """
    print("=" * 70)
    print("DQN PLAY DEMO")
    print("=" * 70)
    
    # Load agent
    print(f"\nLoading model from {model_path}...")
    agent = DQNAgent()
    try:
        agent.load(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please train a model first with demo_train()")
        return
    
    print(f"Playing {num_games} games with trained DQN agent...\n")
    
    scores = []
    max_tiles = []
    
    for i in range(num_games):
        game = Game2048()
        moves = 0
        
        while game.has_moves_available() and moves < 10000:
            action = choose_action_from_dqn(game, agent)
            game.move(action)
            moves += 1
        
        max_tile = max(val for row in game.board for val in row)
        scores.append(game.score)
        max_tiles.append(max_tile)
        
        print(f"Game {i+1}: Score={game.score}, Max Tile={max_tile}, Moves={moves}")
    
    print(f"\nAverage Score: {sum(scores) / len(scores):.1f}")
    print(f"Average Max Tile: {sum(max_tiles) / len(max_tiles):.0f}")
    print(f"Best Score: {max(scores)}")
    print(f"Best Max Tile: {max(max_tiles)}")


def demo_compare():
    """Compare DQN with heuristic AI."""
    print("=" * 70)
    print("AI COMPARISON: DQN vs Heuristic")
    print("=" * 70)
    
    # Load DQN
    print("\nLoading DQN agent...")
    dqn_agent = DQNAgent()
    try:
        dqn_agent.load("dqn_demo/dqn_final.pth")
    except:
        print("No trained DQN model found. Please run demo_train() first.")
        return
    
    num_games = 3
    print(f"\nPlaying {num_games} games with each AI...\n")
    
    # DQN games
    print("DQN Agent:")
    dqn_scores = []
    dqn_max_tiles = []
    
    for i in range(num_games):
        game = Game2048()
        moves = 0
        while game.has_moves_available() and moves < 10000:
            action = choose_action_from_dqn(game, dqn_agent)
            game.move(action)
            moves += 1
        
        max_tile = max(val for row in game.board for val in row)
        dqn_scores.append(game.score)
        dqn_max_tiles.append(max_tile)
        print(f"  Game {i+1}: Score={game.score}, Max Tile={max_tile}")
    
    # Heuristic AI games
    print("\nHeuristic AI:")
    heur_scores = []
    heur_max_tiles = []
    
    for i in range(num_games):
        game = Game2048()
        moves = 0
        while game.has_moves_available() and moves < 10000:
            action = ai_player.choose_best_move(game)
            if action:
                game.move(action)
            moves += 1
        
        max_tile = max(val for row in game.board for val in row)
        heur_scores.append(game.score)
        heur_max_tiles.append(max_tile)
        print(f"  Game {i+1}: Score={game.score}, Max Tile={max_tile}")
    
    # Results
    print("\n" + "=" * 70)
    print("RESULTS:")
    print("=" * 70)
    
    dqn_avg_score = sum(dqn_scores) / len(dqn_scores)
    heur_avg_score = sum(heur_scores) / len(heur_scores)
    
    print(f"\nDQN Average Score:       {dqn_avg_score:.1f}")
    print(f"Heuristic Average Score: {heur_avg_score:.1f}")
    
    if dqn_avg_score > heur_avg_score:
        improvement = ((dqn_avg_score - heur_avg_score) / heur_avg_score) * 100
        print(f"DQN is {improvement:.1f}% better! ✓")
    else:
        print("Heuristic is better (DQN may need more training)")


def demo_training_progress():
    """Train and plot learning curve (requires training for more episodes)."""
    print("=" * 70)
    print("EXTENDED TRAINING WITH PROGRESS TRACKING")
    print("=" * 70)
    print("\nThis will train for 200 episodes and show learning progress.")
    print("Estimated time: 20-40 minutes\n")
    
    response = input("Continue? (y/n, default=n): ").strip().lower()
    if response not in ["y", "yes"]:
        print("Cancelled.")
        return
    
    print("\nStarting training...")
    agent = train_dqn(
        episodes=200,
        batch_size=64,
        update_target_every=10,
        save_every=20,
        save_dir="dqn_extended"
    )
    
    print("\nTraining complete!")
    print("Model saved to dqn_extended/dqn_final.pth")


if __name__ == "__main__":
    print("DQN Agent Demo - 2048")
    print("=" * 70)
    print()
    print("Available demos:")
    print("1. Train a new DQN agent (50 episodes)")
    print("2. Play with a trained agent")
    print("3. Compare DQN vs Heuristic AI")
    print("4. Extended training (200 episodes)")
    print()
    
    choice = input("Select demo (1-4) or 'q' to quit: ").strip()
    
    if choice == "1":
        demo_train()
    elif choice == "2":
        demo_play()
    elif choice == "3":
        demo_compare()
    elif choice == "4":
        demo_training_progress()
    elif choice == "q":
        print("Goodbye!")
    else:
        print("Invalid choice. Run again and select 1-4.")
