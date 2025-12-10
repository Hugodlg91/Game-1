# 2048 en console

Ce dépôt contient une petite implémentation du jeu 2048 jouable dans un terminal. Les déplacements se font avec les touches **W/A/S/D** (ou **U/L/D/R**), et le but est d'atteindre la tuile 2048.

## Prérequis
- Python 3.9+

## Lancer le jeu
```bash
python game_2048.py
```
Vous pouvez personnaliser le plateau et la génération aléatoire :

- `--size 5` : lance une grille 5x5.
- `--seed 123` : rend la partie reproductible (utile pour une démo ou un débogage).
- `--initial-tiles 4` : ajoute 4 tuiles au démarrage au lieu de 2.

## Tests
```bash
python -m unittest discover -s tests -p "test*.py"
```

## Idée de compilation en `.exe`
Pour partager facilement le jeu, vous pourrez utiliser un outil comme [PyInstaller](https://pyinstaller.org/). Une commande typique serait :
```bash
pyinstaller --onefile game_2048.py
```
PyInstaller générera un exécutable autonome dans le dossier `dist/`.

## Interface graphique (optionnelle)

Une version interactive basée sur `pygame` est fournie pour jouer sans taper `Enter` après chaque touche. Installez la dépendance puis lancez :

```bash
pip install -r requirements.txt
python game_2048_pygame.py
```

Contrôles : flèches ou `W/A/S/D` pour déplacer, `R` pour recommencer, `Esc` pour quitter.

## Mode IA

La version console peut jouer automatiquement avec l'IA intégrée : lancez

```bash
python game_2048.py --ai
```

L'IA choisit des déplacements en évaluant les plateaux possibles avec des heuristiques (monotonicité, similarité des voisins, tuiles libres, etc.).

La version `pygame` offre aussi un basculement dynamique : appuyez sur `A` pour activer/désactiver l'autoplay.

## Menu et Q-Learning

Un menu console a été ajouté. Lancez simplement :

```bash
python3 game_2048.py
```

Vous verrez le `2048 Main Menu` avec les options:
Vous verrez le `2048 Main Menu` avec les options:
- `Play (manual)` — jeu classique (graphical)
- `Autoplay (heuristic AI)` — joue avec l'heuristique (graphical)
- `Q-Learning AI` — entraîner et jouer avec l'agent tabulaire (graphical)
- `Settings (key bindings)` — reconfigurer et sauvegarder les touches (persisté dans `settings.json`)

Q-Learning:
- Le Q-table est sauvegardé dans `qtable.pkl`.
- Entraînement: le menu propose de saisir `episodes`, `alpha`, `gamma`, `epsilon`.
- Jeu avec Q-table: choisit actions de façon gloutonne (epsilon=0).

Keybindings:
- Les touches sont stockées dans `settings.json` sous la clé `keys`.
- Exemple:

```json
{
	"keys": { "up": "w", "down": "s", "left": "a", "right": "d" }
}
```

