"""
Bayesian Hyperparameter Optimization for DQN using Optuna.

This script uses Optuna to find optimal hyperparameters for the DQN agent
playing 2048. It optimizes:
- Learning rate, gamma, batch size, memory capacity
- Target network update frequency
- Neural network architecture (layers and sizes)

The optimization uses MedianPruner to stop underperforming trials early.

Usage:
    python optimize_dqn.py
    
Requirements:
    pip install optuna plotly
"""
import optuna
from optuna.pruners import MedianPruner
import torch
import numpy as np
from pathlib import Path
import json

from dqn_agent import DQNAgent, ACTIONS, calculate_reward
from game_2048 import Game2048


def objective(trial: optuna.Trial) -> float:
    """
    Objective function for Optuna optimization.
    
    This function is called for each trial. It:
    1. Suggests hyperparameters
    2. Creates and trains a DQN agent with those hyperparameters
    3. Returns a performance metric (average score)
    
    Args:
        trial: Optuna trial object
    
    Returns:
        Average score over last 50 episodes
    """
    # ========================================================================
    # 1. SUGGEST HYPERPARAMETERS
    # ========================================================================
    
    # Learning rate (log-uniform)
    lr = trial.suggest_float("lr", 1e-5, 1e-2, log=True)
    
    # Discount factor
    gamma = trial.suggest_float("gamma", 0.90, 0.999)
    
    # Batch size (categorical)
    batch_size = trial.suggest_categorical("batch_size", [32, 64, 128, 256])
    
    # Memory capacity (categorical)
    memory_capacity = trial.suggest_categorical("memory_capacity", [10000, 20000, 50000])
    
    # Target network update frequency
    target_update = trial.suggest_int("target_update", 5, 50)
    
    # Neural network architecture
    n_layers = trial.suggest_int("n_layers", 1, 3)
    hidden_sizes = []
    for i in range(n_layers):
        size = trial.suggest_int(f"n_units_l{i}", 64, 512)
        hidden_sizes.append(size)
    
    # ========================================================================
    # 2. CREATE AGENT WITH SUGGESTED HYPERPARAMETERS
    # ========================================================================
    
    agent = DQNAgent(
        lr=lr,
        gamma=gamma,
        memory_capacity=memory_capacity,
        hidden_sizes=hidden_sizes,
        epsilon_start=1.0,
        epsilon_end=0.01,
        epsilon_decay=0.995
    )
    
    # ========================================================================
    # 3. TRAINING LOOP
    # ========================================================================
    
    episodes = 100  # Short training for optimization (adjust based on time)
    max_steps = 10000
    
    episode_scores = []
    episode_max_tiles = []
    
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
            
            # Execute action
            old_board = [row[:] for row in game.board]
            moved = game.move(action)
            
            # Calculate reward
            game_over = not game.has_moves_available()
            reward = calculate_reward(old_board, game.board, moved, game_over)
            episode_reward += reward
            
            # Get next state
            next_state = agent.preprocess_state(game.board)
            
            # Store transition
            agent.memory.push(state, action_idx, reward, next_state, game_over)
            
            # Optimize
            if len(agent.memory) >= batch_size:
                agent.optimize_model(batch_size)
            
            state = next_state
            steps += 1
            
            if game_over:
                break
        
        # Record episode statistics
        max_tile = max(val for row in game.board for val in row)
        episode_scores.append(game.score)
        episode_max_tiles.append(max_tile)
        
        # Decay epsilon
        agent.decay_epsilon()
        
        # Update target network
        if episode % target_update == 0:
            agent.update_target_network()
        
        # ====================================================================
        # 4. PRUNING (MedianPruner)
        # ====================================================================
        
        # Report intermediate result for pruning
        if episode >= 20 and episode % 10 == 0:
            intermediate_score = np.mean(episode_scores[-10:])
            trial.report(intermediate_score, episode)
            
            # Check if trial should be pruned
            if trial.should_prune():
                raise optuna.TrialPruned()
    
    # ========================================================================
    # 5. RETURN FINAL METRIC
    # ========================================================================
    
    # Average score over last 50 episodes (or all if < 50)
    final_episodes = min(50, len(episode_scores))
    avg_score = np.mean(episode_scores[-final_episodes:])
    avg_max_tile = np.mean(episode_max_tiles[-final_episodes:])
    
    # Log metrics
    trial.set_user_attr("avg_max_tile", avg_max_tile)
    trial.set_user_attr("best_score", max(episode_scores))
    
    return avg_score


def run_optimization(
    n_trials: int = 50,
    n_jobs: int = 1,
    study_name: str = "dqn_2048_optimization"
) -> optuna.Study:
    """
    Run Bayesian optimization to find best hyperparameters.
    
    Args:
        n_trials: Number of trials to run
        n_jobs: Number of parallel jobs (-1 for all cores)
        study_name: Name of the optimization study
    
    Returns:
        Optuna study object with results
    """
    print("=" * 70)
    print("DQN HYPERPARAMETER OPTIMIZATION WITH OPTUNA")
    print("=" * 70)
    print(f"\nStarting {n_trials} trials...")
    print("Using MedianPruner to stop underperforming trials early.\n")
    
    # Create Optuna study with MedianPruner
    study = optuna.create_study(
        study_name=study_name,
        direction="maximize",  # Maximize average score
        pruner=MedianPruner(
            n_startup_trials=5,  # Don't prune first 5 trials
            n_warmup_steps=20    # Wait at least 20 episodes before pruning
        )
    )
    
    # Run optimization
    study.optimize(objective, n_trials=n_trials, n_jobs=n_jobs, show_progress_bar=True)
    
    # ========================================================================
    # RESULTS
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("OPTIMIZATION COMPLETE!")
    print("=" * 70)
    
    print(f"\nNumber of finished trials: {len(study.trials)}")
    print(f"Number of pruned trials: {len([t for t in study.trials if t.state == optuna.trial.TrialState.PRUNED])}")
    
    # Best trial
    best_trial = study.best_trial
    print(f"\nBest trial: #{best_trial.number}")
    print(f"  Average Score: {best_trial.value:.1f}")
    print(f"  Average Max Tile: {best_trial.user_attrs.get('avg_max_tile', 'N/A')}")
    print(f"  Best Score: {best_trial.user_attrs.get('best_score', 'N/A')}")
    
    print("\nBest hyperparameters:")
    for key, value in best_trial.params.items():
        print(f"  {key}: {value}")
    
    # ========================================================================
    # SAVE BEST HYPERPARAMETERS
    # ========================================================================
    
    save_path = Path("optuna_results")
    save_path.mkdir(exist_ok=True)
    
    # Save best params as JSON
    best_params_file = save_path / "best_hyperparameters.json"
    with open(best_params_file, 'w') as f:
        json.dump(best_trial.params, f, indent=2)
    print(f"\nBest hyperparameters saved to: {best_params_file}")
    
    return study


def train_best_model(study: optuna.Study, episodes: int = 1000) -> None:
    """
    Train a full model using the best hyperparameters found.
    
    Args:
        study: Optuna study with optimization results
        episodes: Number of episodes to train for
    """
    print("\n" + "=" * 70)
    print("TRAINING FINAL MODEL WITH BEST HYPERPARAMETERS")
    print("=" * 70)
    
    best_params = study.best_trial.params
    
    # Extract hyperparameters
    lr = best_params["lr"]
    gamma = best_params["gamma"]
    batch_size = best_params["batch_size"]
    memory_capacity = best_params["memory_capacity"]
    target_update = best_params["target_update"]
    
    # Extract architecture
    n_layers = best_params["n_layers"]
    hidden_sizes = [best_params[f"n_units_l{i}"] for i in range(n_layers)]
    
    print(f"\nHyperparameters:")
    print(f"  LR: {lr:.6f}")
    print(f"  Gamma: {gamma:.4f}")
    print(f"  Batch size: {batch_size}")
    print(f"  Memory: {memory_capacity}")
    print(f"  Target update: {target_update}")
    print(f"  Architecture: {hidden_sizes}")
    
    # Create agent
    agent = DQNAgent(
        lr=lr,
        gamma=gamma,
        memory_capacity=memory_capacity,
        hidden_sizes=hidden_sizes
    )
    
    # Training loop
    print(f"\nTraining for {episodes} episodes...")
    
    save_dir = Path("optuna_results/best_model")
    save_dir.mkdir(parents=True, exist_ok=True)
    
    episode_scores = []
    episode_max_tiles = []
    
    for episode in range(episodes):
        game = Game2048()
        state = agent.preprocess_state(game.board)
        
        for step in range(10000):
            action_idx = agent.select_action(state)
            action = ACTIONS[action_idx]
            
            old_board = [row[:] for row in game.board]
            moved = game.move(action)
            game_over = not game.has_moves_available()
            
            reward = calculate_reward(old_board, game.board, moved, game_over)
            next_state = agent.preprocess_state(game.board)
            
            agent.memory.push(state, action_idx, reward, next_state, game_over)
            
            if len(agent.memory) >= batch_size:
                agent.optimize_model(batch_size)
            
            state = next_state
            
            if game_over:
                break
        
        max_tile = max(val for row in game.board for val in row)
        episode_scores.append(game.score)
        episode_max_tiles.append(max_tile)
        
        agent.decay_epsilon()
        
        if episode % target_update == 0:
            agent.update_target_network()
        
        # Progress
        if (episode + 1) % 50 == 0:
            avg_score = np.mean(episode_scores[-50:])
            avg_tile = np.mean(episode_max_tiles[-50:])
            print(f"Episode {episode + 1}/{episodes} | "
                  f"Avg Score: {avg_score:.1f} | "
                  f"Avg Max Tile: {avg_tile:.0f} | "
                  f"Epsilon: {agent.epsilon:.3f}")
            
            # Save checkpoint
            agent.save(str(save_dir / f"checkpoint_{episode + 1}.pth"))
    
    # Final save
    final_path = save_dir / "best_dqn_optuna.pth"
    agent.save(str(final_path))
    
    print(f"\n✅ Training complete!")
    print(f"Final model saved to: {final_path}")
    print(f"Average score (last 100): {np.mean(episode_scores[-100:]):.1f}")
    print(f"Best score: {max(episode_scores)}")


def visualize_optimization(study: optuna.Study) -> None:
    """
    Create visualization plots for the optimization results.
    
    Args:
        study: Optuna study with results
    """
    try:
        import plotly
        
        print("\n" + "=" * 70)
        print("GENERATING VISUALIZATION")
        print("=" * 70)
        
        save_dir = Path("optuna_results/plots")
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Optimization history
        fig = optuna.visualization.plot_optimization_history(study)
        fig.write_html(str(save_dir / "optimization_history.html"))
        print(f"✓ Optimization history saved to: {save_dir}/optimization_history.html")
        
        # Parameter importances
        fig = optuna.visualization.plot_param_importances(study)
        fig.write_html(str(save_dir / "param_importances.html"))
        print(f"✓ Parameter importances saved to: {save_dir}/param_importances.html")
        
        # Parallel coordinate plot
        fig = optuna.visualization.plot_parallel_coordinate(study)
        fig.write_html(str(save_dir / "parallel_coordinate.html"))
        print(f"✓ Parallel coordinate plot saved to: {save_dir}/parallel_coordinate.html")
        
        print("\nOpen the HTML files in a browser to view the plots!")
        
    except ImportError:
        print("\nSkipping visualization (plotly not installed)")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Optimize DQN hyperparameters with Optuna")
    parser.add_argument("--n-trials", type=int, default=30, help="Number of optimization trials")
    parser.add_argument("--n-jobs", type=int, default=1, help="Number of parallel jobs")
    parser.add_argument("--train-best", action="store_true", help="Train final model with best params")
    parser.add_argument("--episodes", type=int, default=500, help="Episodes for final training")
    
    args = parser.parse_args()
    
    # Run optimization
    study = run_optimization(n_trials=args.n_trials, n_jobs=args.n_jobs)
    
    # Visualize results
    visualize_optimization(study)
    
    # Train final model if requested
    if args.train_best:
        train_best_model(study, episodes=args.episodes)
    else:
        print("\nTo train a full model with the best hyperparameters, run:")
        print(f"  python optimize_dqn.py --train-best --episodes 1000")
