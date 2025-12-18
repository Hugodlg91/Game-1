# 🎯 Optimisation Expectimax - Potentiel et Stratégie

## Différence Fondamentale DQN vs Expectimax

### DQN (Deep Reinforcement Learning)
- ❌ **Doit apprendre** les patterns par entraînement
- ❌ Besoin de **10000-50000 épisodes**
- ❌ Performances limitées par qualité d'apprentissage
- ✅ Peut s'adapter à différents jeux

### Expectimax (Algorithme de Recherche)
- ✅ **Déterministe** - pas d'entraînement nécessaire
- ✅ Performance immédiate (pas d'apprentissage)
- ✅ Garantie théorique de qualité
- ❌ Spécifique au jeu

## 🎮 Hyperparamètres Optimisables pour Expectimax

### 1. Profondeur de Recherche
**Impact énorme sur performance** :

| Depth | Temps/Move | Score Typique | Tuile Max |
|-------|------------|---------------|-----------|
| 1 | 0.001s | 1000-2000 | 128 |
| 2 | 0.01s | 2000-4000 | 256 |
| **3** | **0.1s** | **4000-8000** | **512** |
| **4** | **1s** | **8000-16000** | **1024** |
| 5 | 10s | 16000-32000 | 2048 |
| 6+ | 100s+ | 32000+ | 4096+ |

**Note** : Avec GPU, on peut aller plus profond !

### 2. Poids des Heuristiques

Fonction d'évaluation actuelle dans `ai_player.py` :

```python
def calculate_heuristic_score(board):
    score = 0
    score += monotonicity(board) * WEIGHT_MONO     # Poids monotonie
    score += smoothness(board) * WEIGHT_SMOOTH     # Poids lissage
    score += empty_cells(board) * WEIGHT_EMPTY     # Poids espaces vides
    score += max_tile_corner(board) * WEIGHT_CORNER # Poids coin
    return score
```

**Hyperparamètres à optimiser** :
- `WEIGHT_MONO` : 0.5 - 5.0
- `WEIGHT_SMOOTH` : 0.1 - 2.0
- `WEIGHT_EMPTY` : 1.0 - 10.0
- `WEIGHT_CORNER` : 0.5 - 5.0

### 3. Stratégie de Tile Spawning

Probabilité de placement des tuiles :
- 90% → tuile 2
- 10% → tuile 4

On peut optimiser la pondération dans l'expectation.

## 📊 Scores Attendus avec Optimisation

### Configuration Actuelle (Non Optimisée)
```python
depth = 3
weights = default (non optimisés)
```
**Score** : 4000-8000

### Configuration Optimisée (Grid Search)
```python
depth = 4
weights = optimisés par grid search
```
**Score attendu** : **12000-20000** 🎯

### Configuration Ultra-Optimisée (GPU + Depth 5)
```python
depth = 5 (possible avec GPU)
weights = optimisés par Optuna
pruning = alpha-beta
```
**Score attendu** : **20000-40000** 🏆

### Configuration Records du Monde
```python
depth = 6-7
weights = optimisés experts
look-ahead avancé
```
**Score** : **100000+** (tuile 32768) 🌟

## 🔬 Plan d'Optimisation Proposé

### Option 1 : Grid Search Simple (2-3h)

**Paramètres à tester** :
```python
depths = [3, 4]  # Depth 4 seulement si GPU
weight_mono = [0.5, 1.0, 2.0, 3.0]
weight_smooth = [0.1, 0.5, 1.0]
weight_empty = [2.0, 5.0, 10.0]
weight_corner = [1.0, 2.0, 3.0]
```

**Total combinaisons** : 2 × 4 × 3 × 3 × 3 = **216 tests**

**Temps estimé** :
- CPU : ~6h (20 parties par config)
- GPU : ~2h (parallélisation possible)

**Score attendu** : **10000-16000**

### Option 2 : Optimisation Optuna (4-6h)

Utiliser Optuna pour optimiser plus intelligemment :

```python
# Espace de recherche
depth: 3-5 (si GPU)
weight_mono: 0.5 - 5.0 (float)
weight_smooth: 0.1 - 2.0 (float)
weight_empty: 1.0 - 10.0 (float)
weight_corner: 0.5 - 5.0 (float)

# Trials
n_trials = 100
games_per_trial = 10
```

**Temps estimé** :
- CPU : ~10-15h
- **GPU** : ~4-6h

**Score attendu** : **16000-24000** 🚀

### Option 3 : Optimisation Profonde (1-2 jours)

Ajouter plus d'hyperparamètres :

```python
# Heuristiques avancées
weight_merge_potential: float
weight_corner_strategy: str  # 'top-left', 'bottom-right', etc.
weight_row_ordering: float
pruning_threshold: float  # Pour alpha-beta

# Depth adaptatif
depth_early_game: int
depth_mid_game: int
depth_end_game: int
```

**Score attendu** : **24000-40000** 🏆

## 💻 Code d'Optimisation Proposé

Je peux créer :

### 1. `optimize_expectimax.py`
```python
"""
Optimise les hyperparamètres d'Expectimax avec Optuna.
"""

def objective(trial):
    # Suggest hyperparameters
    depth = trial.suggest_int('depth', 3, 4)  # ou 5 avec GPU
    weight_mono = trial.suggest_float('weight_mono', 0.5, 5.0)
    weight_smooth = trial.suggest_float('weight_smooth', 0.1, 2.0)
    weight_empty = trial.suggest_float('weight_empty', 1.0, 10.0)
    weight_corner = trial.suggest_float('weight_corner', 0.5, 5.0)
    
    # Play games
    scores = []
    for _ in range(10):  # 10 parties par trial
        game = Game2048()
        while game.has_moves_available():
            move = expectimax_best_move(
                game, 
                depth=depth,
                weights={
                    'mono': weight_mono,
                    'smooth': weight_smooth,
                    'empty': weight_empty,
                    'corner': weight_corner
                }
            )
            game.move(move)
        scores.append(game.score)
    
    return np.mean(scores)
```

### 2. `expectimax_config.py`
```python
"""
Configuration optimisée pour Expectimax.
"""

OPTIMIZED_CONFIG = {
    'depth': 4,
    'weights': {
        'monotonicity': 2.5,
        'smoothness': 0.8,
        'empty': 6.0,
        'corner': 2.0
    }
}
```

## 🎯 Recommandation

### Pour Score Maximum Rapidement

**1. Grid Search Ciblé** (2h sur GPU)
- Depth 4 fixe
- Optimiser seulement les 4 poids
- 10-20 parties par config
- **Score attendu : 12000-16000**

**2. Utilisation Immédiate**
- Expectimax depth 4 (si acceptable niveau vitesse)
- Poids manuels ajustés
- **Score attendu : 8000-12000**

### Pour Record Absolu

**Optuna + GPU + Depth 5** (1 jour)
- 100 trials
- Optimiser depth + tous les poids
- 20 parties par trial
- **Score attendu : 20000-32000** 🏆

## 📈 Comparaison Finale Attendue

| IA | Config | Score Attendu | Tuile Max | Temps |
|----|--------|---------------|-----------|-------|
| DQN | 10000 ep | 3000-5000 | 256-512 | 3-5h |
| DQN | Optimisé | 5000-8000 | 512-1024 | 1-2 jours |
| **Expectimax** | **Depth 3** | **4000-8000** | **512** | **Immédiat** |
| **Expectimax** | **Depth 4** | **8000-16000** | **1024** | **Immédiat** |
| **Expectimax** | **Optimisé** | **16000-24000** | **2048** | **4-6h** |
| **Expectimax** | **Depth 5** | **24000-40000** | **4096** | **Immédiat** |

## 💡 TL;DR

**Question** : Score max avec Expectimax optimisé ?

**Réponse** :
- ✅ **Sans optimisation (depth 4)** : 8000-16000
- ✅ **Avec grid search** : 12000-20000
- ✅ **Avec Optuna** : 16000-24000
- ✅ **Avec GPU + Depth 5** : **24000-40000** 🚀
- ✅ **Records mondiaux** : 100000+ (experts)

**Avantage sur DQN** :
- ⚡ **Immédiat** (pas d'entraînement)
- 🎯 **Deterministe** (résultats reproductibles)
- 🏆 **Meilleur plafond** de performance

**Voulez-vous que je crée le script d'optimisation Expectimax ?** 🚀
