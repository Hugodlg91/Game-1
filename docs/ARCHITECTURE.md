# Architecture du Projet 2048 - Simplifiée

## Structure Finale

```
Game-1/
├── core/               # Cœur du jeu (Logique, IA, Bitboards)
│   ├── game_2048.py                    # Logique principale du jeu
│   ├── ai_player.py                    # Heuristic + Expectimax AI
│   ├── bitboard_2048.py                # Moteur bitboard optimisé
│   └── settings.py                     # Gestion des paramètres
│
├── ui/                 # Interface Graphique (Menus, Écrans)
│   ├── menu.py                         # Menu principal
│   ├── play_screen.py                  # Jeu manuel
│   ├── heuristic_screen.py             # Autoplay heuristique
│   ├── expectimax_screen.py            # Autoplay Expectimax
│   ├── settings_screen.py              # Configuration
│   ├── screens.py                      # Classe de base
│   ├── buttons.py                      # Composant bouton
│   ├── animations.py                   # Système d'animations
│   └── ui_utils.py                     # Utilitaires UI
│
├── scripts/            # Scripts utilitaires et démos
│
├── scripts/            # Scripts utilitaires et démos (non distribués)
│
├── docs/               # Documentation
│   └── ARCHITECTURE.md                 # Ce fichier
│   
├── assets/             # Ressources
│   └── game_icon.png                   # Icône du jeu
│
├── main.py             # Point d'entrée unique
└── requirements.txt    # Dépendances
```

## Composants Principaux

### 1. Logique du Jeu (`core/`)
- **core/game_2048.py** : Classe `Game2048` avec gestion des mouvements, tuiles, et score.
- **core/settings.py** : Configuration des touches clavier et persistance JSON.

### 2. Intelligence Artificielle (`core/`)

#### Heuristic AI
- Fonction : `ai_player.choose_best_move()`
- Vitesse : Très rapide
- Qualité : Bonne

#### Expectimax AI
- Fonction : `ai_player.expectimax_choose_move()`
- Moteur : Bitboards pour performance (`core/bitboard_2048.py`)
- Qualité : Excellente
- Optimisation : Script `scripts/optimize_expectimax.py` (dev only) pour ajuster les poids.

### 3. Interface Utilisateur (`ui/`)

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
plotly>=5.0.0        # Visualisations (optionnel)
```

## Points d'Entrée

### Lancer le Jeu
```bash
python main.py
```

### Démos
```bash
# Expectimax
python scripts/demo_expectimax.py
```

### Optimisation
```bash
# Trouver meilleurs hyperparamètres pour Expectimax
python scripts/optimize_expectimax.py --n-trials 50
```

## Architecture Propre ✅

- ✅ Organisation claire (`core`, `ui`, `scripts`)
- ✅ Racine du projet propre
- ✅ IA Heuristique et Expectimax performantes
- ✅ Structure modulaire et maintenable
