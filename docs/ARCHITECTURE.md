# Architecture du Projet 2048 - Simplifiée

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
│   └── optimize_expectimax.py          # Optimisation bayésienne (Optuna)
│
├── UI Screens
│   ├── ui/menu.py                      # Menu principal
│   ├── ui/play_screen.py               # Jeu manuel
│   ├── ui/heuristic_screen.py          # Autoplay heuristique
│   ├── ui/expectimax_screen.py         # Autoplay Expectimax
│   ├── ui/settings_screen.py           # Configuration
│   ├── ui/screens.py                   # Classe de base
│   ├── ui/buttons.py                   # Composant bouton
│   ├── ui/animations.py                # Système d'animations
│   └── ui/ui_utils.py                  # Utilitaires UI
│
├── Demos & Tests
│   ├── demo_expectimax.py              # Démonstration Expectimax
│   └── tests/                          # Tests unitaires
│
├── Documentation
│   └── README.md                       # Guide principal
│
├── Assets
│   └── ui/reset_icon.png               # Icône de reset
│    └── game_icon.png                   # Icône du jeu
│
├── Configuration
│   ├── requirements.txt                # Dépendances Python
│   ├── settings.json                   # Paramètres utilisateur
│   └── .gitignore                      # Fichiers Git ignorés
│
└── Generated Data
    └── expectimax_optuna_results/      # Résultats d'optimisation Expectimax
```

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
- Optimisation : Script `optimize_expectimax.py` pour trouver les meilleurs poids via Optuna

### 3. Interface Utilisateur

#### Menu Principal
Options disponibles :
1. Play (manual)
2. Autoplay (Heuristic AI)
3. Autoplay (Expectimax)
4. Settings
5. Quit

#### Écrans de Jeu
- **PlayScreen** : Jeu manuel avec animations
- **HeuristicScreen** : IA heuristique (vitesse 2x, animations)
- **ExpectimaxScreen** : IA Expectimax (hautes performances)

### 4. Système d'Animations
- Classe `TileAnimator` dans `ui/animations.py`
- Gère les déplacements, fusions, et apparitions de tuiles
- Utilisé dans tous les écrans de jeu

## Dépendances

```
pygame>=2.0          # Interface graphique
numpy>=1.24.0        # Calculs numériques
optuna>=3.0.0        # Optimisation bayésienne (pour optimize_expectimax.py)
plotly>=5.0.0        # Visualisations (opitonnel)
```

## Points d'Entrée

### Lancer le Jeu
```bash
.\.venv\Scripts\python main.py
```

### Démos
```bash
# Expectimax
python demo_expectimax.py
```

### Optimisation
```bash
# Trouver meilleurs hyperparamètres pour Expectimax
python optimize_expectimax.py --n-trials 50
```

## Architecture Propre ✅

- ✅ Organisation claire
- ✅ IA Heuristique et Expectimax performantes
- ✅ UI complète et responsive
- ✅ Structure modulaire
