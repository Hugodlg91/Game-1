"""
Optimize Expectimax heuristic weights using Bayesian Optimization (Optuna).

This script uses parallel game execution to efficiently find the best weights
for the monotonicity, smoothness, corner, and empty cell heuristics.

The optimization uses:
- Bayesian search (Tree-structured Parzen Estimator)
- Parallel game execution via ProcessPoolExecutor
- Multiple games per trial to reduce variance from randomness

Usage:
    python optimize_expectimax.py --n-trials 100 --n-games 10 --depth 2
"""
import argparse
import json
import time
from pathlib import Path
from typing import Dict, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

import optuna
from optuna.pruners import MedianPruner
import numpy as np

from game_2048 import Game2048
from ai_player import expectimax_choose_move, BITBOARD_AVAILABLE


# ============================================================================
# GAME RUNNER (must be at module level for multiprocessing)
# ============================================================================

def play_single_game(args: Tuple[Dict[str, float], int, int]) -> Tuple[int, int]:
    """
    Play a single game with given weights.
    
    Args:
        args: Tuple of (weights_dict, depth, game_seed)
    
    Returns:
        Tuple of (final_score, max_tile)
    """
    weights, depth, seed = args
    
    # Initialize game with SEED for reproducibility within a trial
    game = Game2048()
    if seed is not None:
        import random
        random.seed(seed)
        np.random.seed(seed)
    
    moves_count = 0
    max_moves = 10000  # Prevent infinite loops
    
    while game.has_moves_available() and moves_count < max_moves:
        # Get move from Expectimax with custom weights
        move = expectimax_choose_move(game, depth=depth, weights=weights)
        
        if move is None:
            break
        
        game.move(move)
        moves_count += 1
    
    max_tile = max(val for row in game.board for val in row)
    
    return game.score, max_tile


# ============================================================================
# OPTUNA OBJECTIVE FUNCTION
# ============================================================================

def objective(trial: optuna.Trial, n_games: int, depth: int, max_workers: int) -> float:
    """
    Objective function for Optuna optimization.
    
    Args:
        trial: Optuna trial object
        n_games: Number of games to play per trial
        depth: Search depth for Expectimax
        max_workers: Number of parallel workers
    
    Returns:
        Average score across all games
    """
    # Suggest hyperparameters
    weights = {
        'mono': trial.suggest_float('monotonicity_weight', 0.0, 10.0),
        'smooth': trial.suggest_float('smoothness_weight', 0.0, 5.0),
        'corner': trial.suggest_float('corner_weight', 0.0, 20.0),
        'empty': trial.suggest_float('empty_weight', 0.0, 20.0),
    }
    
    # Prepare arguments for parallel execution
    # Use different seeds for each game to avoid identical results
    game_args = [(weights, depth, trial.number * n_games + i) for i in range(n_games)]
    
    scores = []
    max_tiles = []
    
    # Execute games in parallel
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all games
        futures = {executor.submit(play_single_game, args): i for i, args in enumerate(game_args)}
        
        # Collect results as they complete
        for future in as_completed(futures):
            try:
                score, max_tile = future.result()
                scores.append(score)
                max_tiles.append(max_tile)
            except Exception as e:
                print(f"Game failed with error: {e}")
                # Use a poor score for failed games
                scores.append(0)
                max_tiles.append(0)
    
    # Compute metrics
    avg_score = np.mean(scores)
    avg_max_tile = np.mean(max_tiles)
    
    # Report intermediate values for pruning
    trial.report(avg_score, step=0)
    
    # Log progress
    print(f"Trial {trial.number}: weights={weights}")
    print(f"  Avg Score: {avg_score:.1f}, Avg Max Tile: {avg_max_tile:.1f}")
    
    # Optuna maximizes, we want to maximize average score
    return avg_score


# ============================================================================
# MAIN OPTIMIZATION LOOP
# ============================================================================

def optimize_expectimax_weights(
    n_trials: int = 50,
    n_games: int = 5,
    depth: int = 2,
    max_workers: int = None,
    output_dir: str = "expectimax_optuna_results"
):
    """
    Run Bayesian optimization to find best heuristic weights.
    
    Args:
        n_trials: Number of Optuna trials
        n_games: Number of games per trial (for averaging)
        depth: Expectimax search depth (2-3 recommended for speed)
        max_workers: Number of parallel workers (default: CPU count)
        output_dir: Directory to save results
    """
    if not BITBOARD_AVAILABLE:
        raise ImportError("Bitboard module required for Expectimax optimization")
    
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()
    
    print("=" * 70)
    print("EXPECTIMAX HEURISTIC WEIGHTS OPTIMIZATION")
    print("=" * 70)
    print(f"Configuration:")
    print(f"  Trials: {n_trials}")
    print(f"  Games per trial: {n_games}")
    print(f"  Expectimax depth: {depth}")
    print(f"  Parallel workers: {max_workers}")
    print(f"  Total games: {n_trials * n_games}")
    print("=" * 70)
    print()
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create Optuna study
    study = optuna.create_study(
        direction='maximize',  # Maximize average score
        pruner=MedianPruner(n_startup_trials=5, n_warmup_steps=0),
        study_name='expectimax_weights'
    )
    
    # Run optimization
    start_time = time.time()
    
    try:
        study.optimize(
            lambda trial: objective(trial, n_games, depth, max_workers),
            n_trials=n_trials,
            show_progress_bar=True,
        )
    except KeyboardInterrupt:
        print("\nOptimization interrupted by user.")
    
    elapsed_time = time.time() - start_time
    
    # Print results
    print()
    print("=" * 70)
    print("OPTIMIZATION COMPLETE!")
    print("=" * 70)
    print()
    print(f"Total time: {elapsed_time / 60:.1f} minutes")
    print(f"Trials completed: {len(study.trials)}")
    print(f"Best trial: #{study.best_trial.number}")
    print(f"Best average score: {study.best_value:.1f}")
    print()
    print("Best hyperparameters:")
    for key, value in study.best_params.items():
        print(f"  {key}: {value:.4f}")
    print()
    
    # Save best weights
    best_weights_path = output_path / "best_weights.json"
    with open(best_weights_path, 'w') as f:
        json.dump({
            'mono': study.best_params['monotonicity_weight'],
            'smooth': study.best_params['smoothness_weight'],
            'corner': study.best_params['corner_weight'],
            'empty': study.best_params['empty_weight'],
        }, f, indent=2)
    
    print(f"✓ Best weights saved to: {best_weights_path}")
    
    # Save full optimization results
    results_path = output_path / "optimization_results.json"
    with open(results_path, 'w') as f:
        json.dump({
            'best_params': study.best_params,
            'best_value': study.best_value,
            'n_trials': len(study.trials),
            'elapsed_time_minutes': elapsed_time / 60,
            'config': {
                'n_games_per_trial': n_games,
                'depth': depth,
                'max_workers': max_workers,
            }
        }, f, indent=2)
    
    print(f"✓ Full results saved to: {results_path}")
    
    # Optional: Generate visualizations if plotly is installed
    try:
        import plotly
        
        plots_dir = output_path / "plots"
        plots_dir.mkdir(exist_ok=True)
        
        # Optimization history
        fig = optuna.visualization.plot_optimization_history(study)
        fig.write_html(str(plots_dir / "optimization_history.html"))
        print(f"✓ Optimization history saved to: {plots_dir / 'optimization_history.html'}")
        
        # Parameter importances
        fig = optuna.visualization.plot_param_importances(study)
        fig.write_html(str(plots_dir / "param_importances.html"))
        print(f"✓ Parameter importances saved to: {plots_dir / 'param_importances.html'}")
        
        # Parallel coordinate plot
        fig = optuna.visualization.plot_parallel_coordinate(study)
        fig.write_html(str(plots_dir / "parallel_coordinate.html"))
        print(f"✓ Parallel coordinate plot saved to: {plots_dir / 'parallel_coordinate.html'}")
        
    except ImportError:
        print("⚠ Plotly not installed. Skipping visualizations.")
    
    print()
    print("=" * 70)
    print("To use the optimized weights in your game:")
    print("=" * 70)
    print()
    print("import json")
    print("with open('expectimax_optuna_results/best_weights.json') as f:")
    print("    weights = json.load(f)")
    print("move = expectimax_choose_move(game, depth=3, weights=weights)")
    print()
    
    return study


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Optimize Expectimax heuristic weights')
    parser.add_argument('--n-trials', type=int, default=50,
                        help='Number of Optuna trials (default: 50)')
    parser.add_argument('--n-games', type=int, default=5,
                        help='Number of games per trial (default: 5)')
    parser.add_argument('--depth', type=int, default=2,
                        help='Expectimax search depth (default: 2, recommend 2-3)')
    parser.add_argument('--workers', type=int, default=None,
                        help='Number of parallel workers (default: CPU count)')
    parser.add_argument('--output-dir', type=str, default='expectimax_optuna_results',
                        help='Output directory (default: expectimax_optuna_results)')
    
    args = parser.parse_args()
    
    optimize_expectimax_weights(
        n_trials=args.n_trials,
        n_games=args.n_games,
        depth=args.depth,
        max_workers=args.workers,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
