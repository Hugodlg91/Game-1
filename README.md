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
