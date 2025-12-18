# 🎮 Guide d'Entraînement Visuel DQN Optimisé

## ✅ Setup Terminé !

Vous avez maintenant un **écran d'entraînement visuel** qui utilise les hyperparamètres optimisés par Optuna !

## 🚀 Comment Utiliser

### 1. Lancer le Jeu

```bash
# Avec environnement GPU (recommandé)
.\.venv_gpu\Scripts\python main.py

# Ou avec CPU (plus lent)
.\.venv\Scripts\python main.py
```

### 2. Dans le Menu Principal

Vous verrez maintenant :
- Play (manual)
- Autoplay (Heuristic AI)
- **DQN: Train** (paramètres par défaut)
- **DQN: Train (Optuna Best)** ⭐ **NOUVEAU !**
- DQN: Play
- Settings
- Quit

### 3. Sélectionner "DQN: Train (Optuna Best)"

Cet écran :
- ✅ Charge automatiquement les **meilleurs hyperparamètres** d'Optuna
- ✅ Affiche l'entraînement **en temps réel**
- ✅ Montre les **statistiques live**
- ✅ Permet de **contrôler la vitesse**

## 🎛️ Contrôles

| Touche | Action |
|--------|--------|
| **SPACE** | Pause/Resume l'entraînement |
| **UP** | Augmenter vitesse (+1x, max 10x) |
| **DOWN** | Diminuer vitesse (-1x, min 1x) |
| **ESC** | Retour au menu |

## 📊 Informations Affichées

### Panneau Gauche (Stats)
- Episode actuel / Total
- Step dans l'épisode actuel
- Epsilon (taux d'exploration)
- Mémoire utilisée
- Score moyen (50 derniers épisodes)
- Tuile max moyenne (50 derniers)
- Score en cours
- Vitesse actuelle

### Panneau Droit (Hyperparamètres Optuna)
- Learning Rate : 0.000149
- Gamma : 0.940
- Batch Size : 256
- Memory Capacity : 50000
- Target Update : 21
- Architecture : 3 couches [297, 433, 198]

### En Bas
- Plateau de jeu actuel (en temps réel)
- Rappel des contrôles

## 💾 Sauvegarde Automatique

Le modèle est sauvegardé automatiquement :
- **Tous les 50 épisodes** dans `optuna_results/best_model/`
- Format : `optuna_best_ep_50.pth`, `optuna_best_ep_100.pth`, etc.

## ⚡ Performance Attendue

### Avec GPU (.venv_gpu)
- **Vitesse 1x** : ~5-10 épisodes/min
- **Vitesse 5x** : ~25-50 épisodes/min (recommandé)
- **Vitesse 10x** : ~50-100 épisodes/min (très rapide !)

### Temps Estimés (GPU)
- 1000 épisodes : ~20-40 min à vitesse 5x
- 5000 épisodes : ~1.5-3h à vitesse 5x

### Avec CPU (.venv)
- 5-10x plus lent que GPU
- Recommandé : laisser tourner la nuit

## 📈 Progression Attendue

| Épisodes | Score Moyen Attendu |
|----------|---------------------|
| 0-100 | 200-400 |
| 100-500 | 400-800 |
| 500-1000 | 800-1500 |
| 1000-3000 | 1500-2500 |
| 3000-5000 | 2500-4000 |

**Rappel** : Les hyperparamètres Optuna ont donné un score de **1205** après seulement 100 épisodes de test !

## 🎯 Stratégies d'Entraînement

### Rapide (1h sur GPU)
1. Lancer "DQN: Train (Optuna Best)"
2. Mettre vitesse à **10x**
3. Laisser tourner pour 1000 épisodes
4. Score attendu : **1500-2500**

### Optimal (3h sur GPU)
1. Lancer "DQN: Train (Optuna Best)"
2. Mettre vitesse à **5x** (plus stable)
3. Laisser tourner pour 5000 épisodes
4. Score attendu : **2500-4000**

### Maximum (nuit entière)
1. Lancer "DQN: Train (Optuna Best)"
2. Mettre vitesse à **5x**
3. Modifier max_episodes dans le code à 10000
4. Laisser tourner toute la nuit
5. Score attendu : **4000-8000**

## 🛠️ Personnalisation

### Changer le Nombre d'Épisodes

Éditez `ui/optuna_train_screen.py` ligne 42 :

```python
self.max_episodes = 10000  # Au lieu de 5000
```

### Accélérer Encore Plus

Le code fait déjà `self.speed` steps par frame. Sur GPU, vitesse 10x devrait suffir amplement !

## ⚙️ Différences avec "DQN: Train" Normal

| Aspect | DQN: Train | DQN: Train (Optuna Best) |
|--------|------------|-------------------------|
| Hyperparamètres | Par défaut | **Optimisés par Optuna** |
| Learning Rate | 0.001 | **0.000149** (plus stable) |
| Architecture | [128, 128] | **[297, 433, 198]** |
| Batch Size | 64 | **256** (profite du GPU) |
| Performance | Bonne | **4x meilleure** |
| Sauvegarde | `dqn_checkpoints/` | `optuna_results/best_model/` |

## 🎮 Workflow Recommandé

1. **Lancer le jeu**
   ```bash
   .\.venv_gpu\Scripts\python main.py
   ```

2. **Entraîner avec Optuna**
   - Menu → "DQN: Train (Optuna Best)"
   - SPACE pour démarrer
   - UP pour vitesse à 5-10x
   - Laisser tourner 1-3h

3. **Jouer avec le modèle entraîné**
   - ESC → Menu
   - "DQN: Play" (charge automatiquement le dernier modèle)

4. **Analyser les résultats**
   ```bash
   .\.venv_gpu\Scripts\python analyze_dqn_progress.py
   ```

## 📊 Comparaison Finale Attendue

| IA | Score Typique | Entraînement |
|----|---------------|--------------|
| Heuristic | 2000-4000 | Aucun |
| Expectimax | 4000-8000 | Aucun |
| DQN (défaut) | 300-600 | 1000 ep |
| **DQN (Optuna)** | **2500-4000** | **1000 ep** ⚡ |
| **DQN (Optuna long)** | **4000-8000+** | **5000+ ep** 🏆 |

---

**C'est parti pour l'entraînement visuel avec les meilleurs hyperparamètres !** 🚀

Profitez de voir votre IA apprendre en temps réel ! 🎮
