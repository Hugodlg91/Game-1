"""
Test and benchmark script for comparing AI implementations.

This script runs multiple games with different AI strategies and compares:
- Average score achieved
- Maximum tile reached
- Number of moves per game
- Time per move

Usage:
    python test_ai_comparison.py
"""
from __future__ import annotations

import time
from typing import List, Dict, Any
from game_2048 import Game2048
from ai_player import choose_best_move, expectimax_choose_move, BITBOARD_AVAILABLE
import random


def run_single_game(ai_function, depth: int = 3, max_moves: int = 10000, seed: int = None) -> Dict[str, Any]:
    """
    Run a single game with the specified AI.
    
    Args:
        ai_function: Function to choose moves (choose_best_move or expectimax_choose_move)
        depth: Search depth for expectimax (ignored for heuristic AI)
        max_moves: Maximum number of moves before terminating
        seed: Random seed for reproducibility
    
    Returns:
        Dict with game statistics
    """
    rng = random.Random(seed) if seed is not None else random.Random()
    game = Game2048(rng=rng)
    
    moves_made = 0
    total_time = 0.0
    move_times: List[float] = []
    
    while game.has_moves_available() and moves_made < max_moves:
        start_time = time.time()
        
        # Choose move based on AI
        if ai_function == expectimax_choose_move:
            move = ai_function(game, depth=depth, clear_cache=(moves_made % 10 == 0))
        else:
            move = ai_function(game)
        
        elapsed = time.time() - start_time
        move_times.append(elapsed)
        total_time += elapsed
        
        if move is None:
            break
        
        moved = game.move(move)
        if not moved:
            break
        
        moves_made += 1
    
    # Get max tile
    max_tile = max(val for row in game.board for val in row)
    
    return {
        'score': game.score,
        'max_tile': max_tile,
        'moves': moves_made,
        'total_time': total_time,
        'avg_time_per_move': total_time / moves_made if moves_made > 0 else 0,
        'min_time': min(move_times) if move_times else 0,
        'max_time': max(move_times) if move_times else 0,
    }


def run_benchmark(num_games: int = 5, expectimax_depth: int = 3) -> None:
    """
    Run benchmark comparing heuristic AI vs Expectimax AI.
    
    Args:
        num_games: Number of games to run for each AI
        expectimax_depth: Depth for Expectimax search
    """
    print("=" * 70)
    print("2048 AI COMPARISON BENCHMARK")
    print("=" * 70)
    print(f"\nRunning {num_games} games with each AI...\n")
    
    # Test 1: Heuristic AI (greedy)
    print("Testing Heuristic AI (greedy)...")
    heuristic_results = []
    for i in range(num_games):
        print(f"  Game {i+1}/{num_games}...", end=" ", flush=True)
        result = run_single_game(choose_best_move, seed=42 + i, max_moves=5000)
        heuristic_results.append(result)
        print(f"Score: {result['score']}, Max Tile: {result['max_tile']}, "
              f"Moves: {result['moves']}, Avg Time: {result['avg_time_per_move']:.3f}s")
    
    # Test 2: Expectimax AI
    if BITBOARD_AVAILABLE:
        print(f"\nTesting Expectimax AI (depth={expectimax_depth})...")
        expectimax_results = []
        for i in range(num_games):
            print(f"  Game {i+1}/{num_games}...", end=" ", flush=True)
            result = run_single_game(expectimax_choose_move, depth=expectimax_depth, 
                                   seed=42 + i, max_moves=5000)
            expectimax_results.append(result)
            print(f"Score: {result['score']}, Max Tile: {result['max_tile']}, "
                  f"Moves: {result['moves']}, Avg Time: {result['avg_time_per_move']:.3f}s")
    else:
        print("\n⚠️  Expectimax AI not available (bitboard module not found)")
        expectimax_results = []
    
    # Display comparison
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    # Heuristic AI stats
    print("\n📊 Heuristic AI (Greedy):")
    avg_score_h = sum(r['score'] for r in heuristic_results) / len(heuristic_results)
    avg_moves_h = sum(r['moves'] for r in heuristic_results) / len(heuristic_results)
    avg_time_h = sum(r['avg_time_per_move'] for r in heuristic_results) / len(heuristic_results)
    max_tile_h = max(r['max_tile'] for r in heuristic_results)
    
    print(f"  Average Score:        {avg_score_h:.1f}")
    print(f"  Average Moves:        {avg_moves_h:.1f}")
    print(f"  Best Tile Reached:    {max_tile_h}")
    print(f"  Avg Time per Move:    {avg_time_h:.4f}s")
    
    # Expectimax AI stats
    if expectimax_results:
        print(f"\n🚀 Expectimax AI (Depth {expectimax_depth}):")
        avg_score_e = sum(r['score'] for r in expectimax_results) / len(expectimax_results)
        avg_moves_e = sum(r['moves'] for r in expectimax_results) / len(expectimax_results)
        avg_time_e = sum(r['avg_time_per_move'] for r in expectimax_results) / len(expectimax_results)
        max_tile_e = max(r['max_tile'] for r in expectimax_results)
        
        print(f"  Average Score:        {avg_score_e:.1f}")
        print(f"  Average Moves:        {avg_moves_e:.1f}")
        print(f"  Best Tile Reached:    {max_tile_e}")
        print(f"  Avg Time per Move:    {avg_time_e:.4f}s")
        
        # Comparison
        print(f"\n📈 Improvement:")
        score_improvement = ((avg_score_e - avg_score_h) / avg_score_h) * 100
        time_ratio = avg_time_e / avg_time_h
        print(f"  Score:                {score_improvement:+.1f}%")
        print(f"  Time per Move:        {time_ratio:.1f}x slower")
    
    print("\n" + "=" * 70)


def test_single_move() -> None:
    """Quick test: single move with both AIs."""
    print("\n🧪 Quick Test: Single Move Comparison\n")
    
    # Create a test board
    game = Game2048(rng=random.Random(123))
    
    # Make a few moves to get a non-trivial board
    for _ in range(5):
        game.move(random.choice(["up", "down", "left", "right"]))
    
    print("Current Board:")
    print(game.render())
    print()
    
    # Test heuristic AI
    print("Heuristic AI recommendation:")
    start = time.time()
    move_h = choose_best_move(game)
    time_h = time.time() - start
    print(f"  Move: {move_h}")
    print(f"  Time: {time_h:.4f}s")
    
    # Test Expectimax AI
    if BITBOARD_AVAILABLE:
        print("\nExpectimax AI recommendation (depth=3):")
        start = time.time()
        move_e = expectimax_choose_move(game, depth=3)
        time_e = time.time() - start
        print(f"  Move: {move_e}")
        print(f"  Time: {time_e:.4f}s")
        print(f"  Slowdown: {time_e/time_h:.1f}x")
    else:
        print("\n⚠️  Expectimax AI not available")


if __name__ == "__main__":
    # Quick single-move test
    test_single_move()
    
    # Full benchmark
    print("\n" + "=" * 70)
    response = input("\nRun full benchmark? (y/n, default=y): ").strip().lower()
    
    if response in ["", "y", "yes"]:
        run_benchmark(num_games=3, expectimax_depth=3)
    else:
        print("\nSkipping full benchmark.")
    
    print("\n✅ Tests complete!")
