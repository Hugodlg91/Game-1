"""
Simple demonstration script showing how to use the Expectimax AI.

This script shows basic usage with different configurations.
"""
from game_2048 import Game2048
from ai_player import choose_best_move, expectimax_choose_move
import time


def demo_basic_usage():
    """Demonstrate basic usage of both AIs."""
    print("=" * 60)
    print("DEMO: Basic AI Usage")
    print("=" * 60)
    
    # Create a new game
    game = Game2048()
    print("\nInitial Board:")
    print(game.render())
    
    # Make a few moves to get an interesting board state
    print("\nMaking some random moves to set up the board...")
    for move in ["up", "left", "up", "left"]:
        game.move(move)
    
    print("\nCurrent Board:")
    print(game.render())
    
    # Compare both AIs
    print("\n" + "-" * 60)
    print("AI RECOMMENDATIONS:")
    print("-" * 60)
    
    # Heuristic AI
    print("\n1. Heuristic AI (Greedy):")
    start = time.time()
    move_h = choose_best_move(game)
    time_h = time.time() - start
    print(f"   Recommended move: {move_h}")
    print(f"   Computation time: {time_h:.4f}s")
    
    # Expectimax AI (depth 2)
    print("\n2. Expectimax AI (depth=2):")
    start = time.time()
    move_e2 = expectimax_choose_move(game, depth=2)
    time_e2 = time.time() - start
    print(f"   Recommended move: {move_e2}")
    print(f"   Computation time: {time_e2:.4f}s")
    
    # Expectimax AI (depth 3)
    print("\n3. Expectimax AI (depth=3):")
    start = time.time()
    move_e3 = expectimax_choose_move(game, depth=3)
    time_e3 = time.time() - start
    print(f"   Recommended move: {move_e3}")
    print(f"   Computation time: {time_e3:.4f}s")
    
    print("\n" + "=" * 60)


def demo_play_game():
    """Play a complete game using Expectimax AI."""
    print("\n" + "=" * 60)
    print("DEMO: Full Game with Expectimax AI (depth=3)")
    print("=" * 60)
    
    game = Game2048()
    moves_made = 0
    max_moves = 100  # Limit for demo
    
    print(f"\nPlaying up to {max_moves} moves...")
    print("(Press Ctrl+C to stop early)\n")
    
    try:
        while game.has_moves_available() and moves_made < max_moves:
            # Get AI move
            move = expectimax_choose_move(game, depth=3, clear_cache=(moves_made % 10 == 0))
            
            if move is None:
                print("No valid moves available!")
                break
            
            # Execute move
            game.move(move)
            moves_made += 1
            
            # Print progress every 10 moves
            if moves_made % 10 == 0:
                max_tile = max(val for row in game.board for val in row)
                print(f"Move {moves_made}: Score={game.score}, Max Tile={max_tile}")
    
    except KeyboardInterrupt:
        print("\n\nGame stopped by user.")
    
    # Final results
    print("\n" + "-" * 60)
    print("GAME OVER")
    print("-" * 60)
    print(f"Final Score: {game.score}")
    print(f"Moves Made: {moves_made}")
    max_tile = max(val for row in game.board for val in row)
    print(f"Max Tile: {max_tile}")
    print("\nFinal Board:")
    print(game.render())
    print("=" * 60)


if __name__ == "__main__":
    # Basic usage demo
    demo_basic_usage()
    
    # Ask if user wants to see full game
    print("\n")
    response = input("Run full game demo? (y/n, default=n): ").strip().lower()
    
    if response in ["y", "yes"]:
        demo_play_game()
    else:
        print("\nSkipping full game demo.")
    
    print("\n✅ Demo complete!")
