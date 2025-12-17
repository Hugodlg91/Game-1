# DQN Hyperparameter Optimization Guide

## Overview

Use Bayesian optimization with Optuna to find optimal hyperparameters for your DQN agent.

## Quick Start

### 1. Install Dependencies

```bash
.\.venv\Scripts\pip install optuna plotly
```

### 2. Run Optimization

```bash
# Run 30 trials (default)
.\.venv\Scripts\python optimize_dqn.py

# Run with more trials for better results
.\.venv\Scripts\python optimize_dqn.py --n-trials 50

# Run and train final model with best params
.\.venv\Scripts\python optimize_dqn.py --n-trials 30 --train-best --episodes 1000
```

## What Gets Optimized

### Hyperparameters

- **Learning rate (lr)**: Log-uniform between 1e-5 and 1e-2
- **Gamma (γ)**: Float between 0.90 and 0.999
- **Batch size**: Categorical [32, 64, 128, 256]
- **Memory capacity**: Categorical [10,000, 20,000, 50,000]
- **Target update frequency**: Integer between 5 and 50

### Neural Network Architecture

- **Number of layers**: 1 to 3 hidden layers
- **Layer sizes**: 64 to 512 neurons per layer

## How It Works

### 1. Search Space

Optuna suggests hyperparameters from defined ranges:

```python
lr = trial.suggest_float("lr", 1e-5, 1e-2, log=True)
n_layers = trial.suggest_int("n_layers", 1, 3)
hidden_sizes = [trial.suggest_int(f"n_units_l{i}", 64, 512) 
                for i in range(n_layers)]
```

### 2. Training & Evaluation

For each trial:
- Creates DQN agent with suggested hyperparameters
- Trains for 100 episodes (quick evaluation)
- Returns average score as performance metric

### 3. Pruning

**MedianPruner** stops unpromising trials early:
- Waits 20 episodes before pruning (warmup)
- Compares intermediate results to other trials
- Stops if performing below median

This saves ~50% of computation time!

### 4. Best Parameters

After optimization completes:
- Best hyperparameters saved to `optuna_results/best_hyperparameters.json`
- Optionally trains full model with those parameters

## Output

### Console Output

```
Episode 30/100 | Avg Score: 1234.5 | Avg Max Tile: 128
Trial 5 finished with value: 1456.7
Best trial so far: #3 with score 1678.9
```

### Files Created

```
optuna_results/
├── best_hyperparameters.json        # JSON with best params
├── plots/
│   ├── optimization_history.html    # Score progression
│   ├── param_importances.html       # Which params matter most
│   └── parallel_coordinate.html     # Trial comparisons
└── best_model/
    ├── best_dqn_optuna.pth          # Trained model (if --train-best)
    └── checkpoint_*.pth             # Training checkpoints
```

## Visualization

Open the HTML files in `optuna_results/plots/` to see:

1. **Optimization History**: How the best score improves over trials
2. **Parameter Importances**: Which hyperparameters affect performance most
3. **Parallel Coordinate**: Visual comparison of all trials

## Advanced Usage

### Customize Optimization

Edit `optimize_dqn.py` to:

```python
# Change number of training episodes per trial
episodes = 200  # More episodes = better evaluation, slower

# Modify search space
lr = trial.suggest_float("lr", 1e-4, 1e-3)  # Narrower range

# Add new hyperparameters
dropout = trial.suggest_float("dropout", 0.0, 0.5)
```

### Use Best Parameters Manually

```python
import json
from dqn_agent import DQNAgent

# Load best params
with open("optuna_results/best_hyperparameters.json") as f:
    params = json.load(f)

# Extract architecture
n_layers = params["n_layers"]
hidden_sizes = [params[f"n_units_l{i}"] for i in range(n_layers)]

# Create agent
agent = DQNAgent(
    lr=params["lr"],
    gamma=params["gamma"],
    memory_capacity=params["memory_capacity"],
    hidden_sizes=hidden_sizes
)

# Train...
```

## Tips

### Performance

- **Quick test**: `--n-trials 10` (~1-2 hours)
- **Good results**: `--n-trials 30` (~3-6 hours)
- **Best results**: `--n-trials 50+` (~6-12 hours)

### Parallel Execution

```bash
# Use all CPU cores (much faster!)
python optimize_dqn.py --n-trials 30 --n-jobs -1
```

⚠️ **Warning**: May use a lot of RAM

### Tweaking the Objective

If trials are too slow, reduce episodes in `objective()`:

```python
episodes = 50  # Instead of 100
```

If results are too noisy, increase:

```python
episodes = 200  # More stable evaluation
```

## Example Output

```
========================================================================
DQN HYPERPARAMETER OPTIMIZATION WITH OPTUNA
========================================================================

Starting 30 trials...
Using MedianPruner to stop underperforming trials early.

Trial 0: Score = 1234.5
Trial 1: Score = 1456.7 (pruned)
Trial 2: Score = 1678.9
...
Trial 29: Score = 2345.6

========================================================================
OPTIMIZATION COMPLETE!
========================================================================

Number of finished trials: 30
Number of pruned trials: 12

Best trial: #15
  Average Score: 2456.7
  Average Max Tile: 256
  Best Score: 4512

Best hyperparameters:
  lr: 0.000543
  gamma: 0.975
  batch_size: 128
  memory_capacity: 20000
  target_update: 12
  n_layers: 2
  n_units_l0: 256
  n_units_l1: 128

Best hyperparameters saved to: optuna_results/best_hyperparameters.json
```

## Troubleshooting

### Out of Memory

- Reduce `memory_capacity` max value
- Reduce `n_trials`
- Don't use `--n-jobs -1`

### Too Slow

- Reduce `episodes` in objective function
- Use fewer trials
- Use `--n-jobs` for parallelization

### Poor Results

- Increase `n_trials` (more exploration)
- Increase `episodes` in objective (better evaluation)
- Widen hyperparameter ranges

## Next Steps

1. Run optimization: `python optimize_dqn.py --n-trials 30`
2. Check visualizations in `optuna_results/plots/`
3. Train full model: `python optimize_dqn.py --train-best --episodes 1000`
4. Play with optimized agent!

Good luck optimizing! 🚀
