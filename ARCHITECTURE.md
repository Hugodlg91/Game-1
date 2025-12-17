# Architecture du Projet 2048 - Nettoyée

## Structure Finale

```
Game-1/
├── Core Game Logic
│   ├── game_2048.py                    # Logique principale du jeu
│   └── settings.py                     # Gestion des paramètres
│
├── AI Implementations
│   ├── ai_player.py                    # Heuristic + Expectimax AI
│   ├── bitboard_2048.py                # Moteur bitboard optimisé
│   ├── dqn_agent.py                    # Deep Q-Network avec PyTorch
│   └── optimize_dqn.py                 # Optimisation bayésienne (Optuna)
│
├── UI Screens
│   ├── ui/menu.py                      # Menu principal
│   ├── ui/play_screen.py               # Jeu manuel
│   ├── ui/heuristic_screen.py          # Autoplay heuristique
│   ├── ui/dqn_train_screen.py          # Entraînement DQN
│   ├── ui/dqn_play_screen.py           # Jeu avec DQN
│   ├── ui/settings_screen.py           # Configuration
│   ├── ui/screens.py                   # Classe de base
│   ├── ui/buttons.py                   # Composant bouton
│   ├── ui/animations.py                # Système d'animations
│   └── ui/ui_utils.py                  # Utilitaires UI
│
├── Demos & Tests
│   ├── demo_dqn.py                     # Démonstration DQN
│   ├── demo_expectimax.py              # Démonstration Expectimax
│   ├── test_ai_comparison.py           # Benchmark des IA
│   └── tests/                          # Tests unitaires
│
├── Documentation
│   ├── README.md                       # Guide principal
│   ├── DQN_README.md                   # Guide DQN
│   ├── EXPECTIMAX_README.md            # Guide Expectimax
│   └── OPTIMIZATION_README.md          # Guide optimisation
│
├── Assets
│   └── ui/reset_icon.png               # Icône de reset
│
├── Configuration
│   ├── requirements.txt                # Dépendances Python
│   ├── settings.json                   # Paramètres utilisateur
│   └── .gitignore                      # Fichiers Git ignorés
│
└── Generated Data
    └── dqn_checkpoints/                # Modèles DQN sauvegardés
```

## Fichiers Supprimés (Obsolètes)

### ❌ Ancien Q-Learning
- `q_learning_agent.py` - Remplacé par DQN
- `qtable.pkl` (1.1 MB) - Table Q sauvegardée
- `ui/qlearning_train_screen.py` - Écran d'entraînement
- `ui/qlearning_play_screen.py` - Écran de jeu

### ❌ Fichiers Temporaires
- `create_icon_script.py` - Script usage unique (icône créée)
- `dqn_test/` - Dossier de tests temporaires

**Gain d'espace** : ~1.2 MB

## Composants Principaux

### 1. Logique du Jeu
- **game_2048.py** : Classe `Game2048` avec gestion des mouvements, tuiles, et score
- **settings.py** : Configuration des touches clavier

### 2. Intelligence Artificielle

#### Heuristic AI
- Fonction : `ai_player.choose_best_move()`
- Vitesse : Très rapide
- Qualité : Bonne

#### Expectimax AI
- Fonction : `ai_player.expectimax_choose_move()`
- Moteur : Bitboards pour performance
- Qualité : Excellente

#### DQN (Deep Q-Network)
- Classe : `DQNAgent`
- Entraînement : Reinforcement Learning
- Optimisation : Optuna pour hyperparamètres

### 3. Interface Utilisateur

#### Menu Principal
Options disponibles :
1. Play (manual)
2. Autoplay (Heuristic AI)
3. DQN: Train
4. DQN: Play
5. Settings
6. Quit

#### Écrans de Jeu
- **PlayScreen** : Jeu manuel avec animations
- **HeuristicScreen** : IA heuristique (vitesse 2x, animations)
- **DQNTrainScreen** : Entraînement DQN en temps réel
- **DQNPlayScreen** : Jeu avec modèle DQN entraîné

### 4. Système d'Animations
- Classe `TileAnimator` dans `ui/animations.py`
- Gère les déplacements, fusions, et apparitions de tuiles
- Utilisé dans PlayScreen, HeuristicScreen, et DQNPlayScreen

## Dépendances

```
pygame>=2.0          # Interface graphique
torch>=2.0.0         # Deep Learning (DQN)
numpy>=1.24.0        # Calculs numériques
optuna>=3.0.0        # Optimisation bayésienne
plotly>=5.0.0        # Visualisations
```

## Points d'Entrée

### Lancer le Jeu
```bash
.\.venv\Scripts\python main.py
```

### Démos
```bash
# DQN
python demo_dqn.py

# Expectimax
python demo_expectimax.py

# Benchmark IA
python test_ai_comparison.py
```

### Optimisation
```bash
# Trouver meilleurs hyperparamètres
python optimize_dqn.py --n-trials 30

# Entraîner avec hyperparamètres optimaux
python optimize_dqn.py --train-best --episodes 1000
```

## Architecture Propre ✅

- ✅ Pas de code mort
- ✅ Organisation claire
- ✅ 3 systèmes d'IA distincts
- ✅ UI complète et fonctionnelle
- ✅ Documentation à jour
- ✅ Structure modulaire

Total : **17 fichiers Python** essentiels + UI + docs
