# 🚀 Setup GPU avec Python 3.11 - Guide Pas à Pas

## Étape 1 : Installer Python 3.11

### Option A : Via Microsoft Store (Recommandé - Plus Simple)
1. Ouvrir Microsoft Store
2. Chercher "Python 3.11"
3. Cliquer "Obtenir" / "Install"

### Option B : Via python.org
1. Aller sur : https://www.python.org/downloads/release/python-31113/
2. Télécharger : **Windows installer (64-bit)**
3. Lancer l'installeur
4. ✅ **Cocher "Add Python 3.11 to PATH"**
5. Cliquer "Install Now"

## Étape 2 : Créer Environnement GPU

```bash
# Vérifier que Python 3.11 est installé
py -3.11 --version

# Créer nouvel environnement virtuel
py -3.11 -m venv .venv_gpu

# Activer l'environnement GPU
.\.venv_gpu\Scripts\activate

# Devrait afficher : (.venv_gpu) au début de la ligne
```

## Étape 3 : Installer Dépendances

```bash
# S'assurer d'être dans .venv_gpu (voir (.venv_gpu) dans le prompt)

# Installer dépendances de base
pip install pygame numpy optuna plotly

# Installer PyTorch avec CUDA 12.1 (compatible RTX 4070)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## Étape 4 : Vérifier GPU

```bash
# Test CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

**Résultat attendu** :
```
CUDA: True
GPU: NVIDIA GeForce RTX 4070
```

Si vous voyez `CUDA: False`, redémarrez le terminal et réessayez.

## Étape 5 : Tester Entraînement GPU

```bash
# Petit test rapide (100 épisodes)
python train_dqn_fast.py 100
```

**Devrait afficher** :
```
Using device: cuda
```

Si vous voyez `Using device: cpu`, quelque chose ne va pas.

## Utilisation

### Avec GPU (rapide)
```bash
# Activer environnement GPU
.\.venv_gpu\Scripts\activate

# Entraîner
python train_dqn_fast.py 5000

# Optimiser
python optimize_dqn.py --n-trials 50
```

### Avec CPU (lent mais stable)
```bash
# Activer environnement CPU
.\.venv\Scripts\activate

# Entraîner
python train_dqn_fast.py 1000
```

## Partage des Checkpoints

✅ **Bonne nouvelle** : Les deux environnements partagent les mêmes fichiers !

- Checkpoints : `dqn_checkpoints/` (communs)
- Scripts : `.py` (communs)
- Seule différence : `.venv` vs `.venv_gpu`

Vous pouvez :
1. Entraîner sur `.venv_gpu` (GPU rapide)
2. Analyser sur `.venv` (CPU, pas de problème)

## Résolution de Problèmes

### "py -3.11 not found"
→ Python 3.11 pas installé
→ Installez via Microsoft Store ou python.org

### "CUDA: False" après installation
→ Redémarrez le terminal
→ Vérifiez : `pip show torch` → doit dire `cu121` pas `cpu`

### Erreur "CUDA out of memory"
→ Réduisez batch_size dans les scripts
→ Fermez autres applications

### Tout semble lent malgré GPU
→ Vérifiez que "Using device: cuda" s'affiche
→ Surveillez GPU avec : `nvidia-smi -l 1`

## Commandes Rapides (Copier-Coller)

```bash
# Installation complète (après avoir installé Python 3.11)
py -3.11 -m venv .venv_gpu
.\.venv_gpu\Scripts\activate
pip install pygame numpy optuna plotly
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
python -c "import torch; print('GPU Ready!' if torch.cuda.is_available() else 'Still CPU only')"
python train_dqn_fast.py 100
```

## Performance Attendue

| Tâche | CPU (.venv) | GPU (.venv_gpu) | Gain |
|-------|-------------|-----------------|------|
| 100 épisodes | 20 min | **2 min** | 10x |
| 1000 épisodes | 4h | **15-30 min** | 8-16x |
| 5000 épisodes | 20h | **1-2h** | 10-20x |
| Optuna 50 trials | 3h | **15-20 min** | 9-12x |

## Structure Finale

```
Game-1/
├── .venv/              # Python 3.13 + CPU (garde actuel)
├── .venv_gpu/          # Python 3.11 + CUDA (nouveau)
├── dqn_checkpoints/    # Partagé entre les deux
└── *.py                # Scripts (marchent dans les deux)
```

---

**Prochaine étape** : Installer Python 3.11 !

1. Microsoft Store → "Python 3.11" → Install
2. Ou télécharger : https://www.python.org/downloads/release/python-31113/

Dites-moi quand c'est fait ! 🚀
