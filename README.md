# 2048 Ultimate

Une implémentation complète et optimisée du jeu 2048 en Python, incluant une interface graphique soignée et une intelligence artificielle performante (Expectimax).

## 🚀 Fonctionnalités

- **Jeu Complet** : Logique 2048 robuste avec gestion des scores et des états.
- **Interface Graphique (UI)** :
  - Menu principal interactif.
  - Animations fluides pour les déplacements et fusions de tuiles.
  - Écrans de jeu manuel et automatique.
  - Paramètres personnalisables (configuration des touches).
- **Intelligence Artificielle** :
  - **Heuristic AI** : IA rapide basée sur des règles simples.
  - **Expectimax AI** : IA avancée utilisant des **Bitboards** (opérations sur les bits) pour une performance maximale et une prédiction à plusieurs coups d'avance.

## 📦 Installation

Assurez-vous d'avoir Python 3.9+ installé.

1. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Comment Jouer

Lancez simplement le point d'entrée unique du projet :
```bash
python main.py
```
Cela ouvrira le menu principal où vous pourrez choisir :
- **Play (manual)** : Jouer vous-même.
- **Autoplay (Heuristic)** : Voir l'IA basique jouer (rapide).
- **Autoplay (Expectimax)** : Voir l'IA avancée jouer (haute performance).
- **Settings** : Configurer vos touches.

### Contrôles par défaut
- **Flèches directionnelles** ou **Z/Q/S/D** : Déplacer les tuiles.
- **Espace** : Mettre en pause (en mode Autoplay).
- **ESC** : Retour au menu ou quitter.

## 🔧 Scripts et Outils

Le projet contient des scripts utiles dans le dossier `scripts/` :

- **Démonstration IA console** :
  ```bash
  python scripts/demo_expectimax.py
  ```
- **Optimisation IA (Optuna)** :
  Lance une recherche d'hyperparamètres pour améliorer encore l'IA.
  ```bash
  python scripts/optimize_expectimax.py
  ```
  *(Les résultats sont sauvegardés dans `expectimax_optuna_results/`)*

## 📂 Structure du Projet

L'architecture a été simplifiée pour plus de clarté :

```
Game-1/
├── core/               # Cœur du jeu (Logique, IA, Bitboards)
│   ├── game_2048.py
│   ├── ai_player.py
│   └── bitboard_2048.py
├── ui/                 # Interface Graphique (Menus, Écrans)
├── scripts/            # Scripts utilitaires et démos
├── docs/               # Documentation technique
├── assets/             # Images et ressources
├── main.py             # Point d'entrée
└── requirements.txt    # Dépendances
```

Pour plus de détails techniques, consultez [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
