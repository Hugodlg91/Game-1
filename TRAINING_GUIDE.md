# 🚀 Guide d'Entraînement Rapide DQN

## ⚠️ Commandes Importantes

**TOUJOURS** utiliser l'environnement virtuel :

```bash
# ❌ INCORRECT (ne trouve pas les dépendances)
python analyze_dqn_progress.py

# ✅ CORRECT (utilise .venv avec torch, optuna, etc.)
.\.venv\Scripts\python analyze_dqn_progress.py
```

## 🎯 Entraînement Rapide

### Option 1 : Entraînement Standard (Recommandé)

```bash
# 2000 épisodes (~6-8h sur CPU)
.\.venv\Scripts\python train_dqn_fast.py 2000

# 5000 épisodes (~15-20h sur CPU)
.\.venv\Scripts\python train_dqn_fast.py 5000
```

**Optimisations incluses** :
- Batch size augmenté à 128 (2x plus rapide)
- Sauvegarde tous les 50 épisodes
- Peut être interrompu avec Ctrl+C

### Option 2 : Depuis l'UI

1. Lancez le jeu : `.\.venv\Scripts\python main.py`
2. Cliquez sur **"DQN: Train"**
3. Contrôles :
   - **SPACE** : Pause/Resume
   - **UP/DOWN** : Vitesse ±1 (max 10x)
4. Laissez tourner en arrière-plan

### Option 3 : Optimisation Bayésienne

Pour trouver les MEILLEURS hyperparamètres :

```bash
# 30 essais (~6-10h)
.\.venv\Scripts\python optimize_dqn.py --n-trials 30

# Puis entraîner avec les meilleurs params trouvés
.\.venv\Scripts\python optimize_dqn.py --train-best --episodes 3000
```

## 📊 Analyse des Progrès

```bash
# Analyse rapide (2 minutes)
.\.venv\Scripts\python analyze_dqn_progress.py --quick

# Analyse complète (10-20 minutes)
.\.venv\Scripts\python analyze_dqn_progress.py
```

## ⚡ Accélération Maximale

### Méthode 1 : Batch Size Plus Grand

Modifiez `train_dqn_fast.py` ligne 39 :
```python
batch_size=256,  # Au lieu de 128 (mais plus de RAM)
```

### Méthode 2 : Moins de Validation (Risqué)

Dans `dqn_agent.py`, réduisez la fréquence d'affichage ligne 442 :
```python
if (episode + 1) % 100 == 0:  # Au lieu de % 10
```

## 🎮 Tester l'Agent Actuel

```bash
# Voir l'agent jouer
.\.venv\Scripts\python main.py
# → Cliquez sur "DQN: Play"
```

## 📈 Temps d'Entraînement Estimés

| Épisodes | Temps (CPU) | Performance Attendue |
|----------|-------------|----------------------|
| 1000 (actuel) | ~4h | Score ~300 |
| 2000 | ~8h | Score ~400-600 |
| 5000 | ~20h | Score ~800-1500 |
| Optimisé (Optuna + 3000) | ~2 jours | Score ~2000+ |

## 💡 Conseils

1. **Laissez tourner la nuit** : L'entraînement est interruptible (Ctrl+C)
2. **Vérifiez les checkpoints** : `dir dqn_checkpoints`
3. **Analysez régulièrement** : Tous les 500 épisodes
4. **Optimisez d'abord** : Optuna peut diviser le temps d'entraînement par 2-3x

## 🚨 Dépannage

### "No module named 'torch'"
```bash
# Réinstallez les dépendances
.\.venv\Scripts\pip install -r requirements.txt
```

### Trop lent
```bash
# Utilisez batch_size plus grand
.\.venv\Scripts\python train_dqn_fast.py 2000
# (déjà optimisé avec batch_size=128)
```

### Manque de RAM
```bash
# Réduisez batch_size dans train_dqn_fast.py
batch_size=64,  # Au lieu de 128
```

## 🎯 Objectif Recommandé

1. **Maintenant** : `.\.venv\Scripts\python train_dqn_fast.py 2000`
2. **Demain** : Analyser les progrès
3. **Après-demain** : Lancer Optuna si besoin d'optimisation

Bon entraînement ! 🚀
