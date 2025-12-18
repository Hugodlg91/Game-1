# 🔍 Analyse des Limitations du DQN pour 2048

## Diagnostic des Performances

### Scores Typiques Actuels

Selon vos résultats Optuna :
- **Score moyen après 100 épisodes** : ~1200
- **Meilleur score** : ~3000
- **Tuile max moyenne** : ~116 (entre 64 et 128)

### Comparaison avec Autres IA

| IA | Score Typique | Tuile Max | Pourquoi Meilleur ? |
|----|---------------|-----------|---------------------|
| **Heuristic** | 2000-4000 | 256-512 | Heuristiques expertes codées |
| **Expectimax** | 4000-8000 | 512-1024 | Recherche arborescente profonde |
| **DQN (actuel)** | 1200-3000 | 64-128 | Apprentissage incomplet ⚠️ |

## 🎯 Problèmes Identifiés

### 1. Learning Rate TROP Faible

**Actuel** : `lr = 0.000149`

**Impact** :
- ❌ Apprentissage **extrêmement lent**
- ❌ Besoin de **10000-50000 épisodes** pour converger
- ❌ Vous n'avez entraîné que pour **~100-1000 épisodes**

**Solution** :
```python
lr = 0.0005  # 3-4x plus rapide, tout en restant stable
```

### 2. Reward Shaping Inadapté

Le reward actuel dans `dqn_agent.py` :

```python
def calculate_reward(old_board, new_board, moved, game_over):
    if not moved:
        return -1.0  # Pénalité mouvement invalide
    
    score_gain = new_sum - old_sum  # Gain de score
    tile_bonus = math.log2(max_tile) * 0.1  # Bonus tuile max (TROP FAIBLE!)
    game_over_penalty = -10.0 if game_over else 0.0
    
    return score_gain + tile_bonus + game_over_penalty
```

**Problèmes** :
- ❌ Bonus tuile max trop faible (0.1 * log2)
- ❌ Pas de bonus pour tuiles adjacentes
- ❌ Pas de bonus pour espaces vides
- ❌ Pas de pénalité pour désordre

### 3. State Representation Limitée

**Actuel** : Grille 4x4 flat (16 valeurs)

```python
state = [log2(val + 1) for val in board]  # Simple mais perd l'info spatiale
```

**Problème** :
- ❌ Perd information de position
- ❌ Ne capture pas les patterns (coins, monotonie)

### 4. Architecture du Réseau

**Optuna a trouvé** : `[297, 433, 198]` (pyramide inversée)

**Problème** :
- ⚠️ Peut-être pas optimal pour 2048
- ⚠️ Pas de convolutions (pas de détection de patterns spatiaux)

## 💡 Solutions Proposées

### Solution 1 : Reward Shaping Amélioré (Impact +200%)

Créons une meilleure fonction de reward :

```python
def calculate_reward_improved(old_board, new_board, moved, game_over):
    if not moved:
        return -5.0  # Pénalité plus forte
    
    # Score gain (base)
    old_sum = sum(val for row in old_board for val in row)
    new_sum = sum(val for row in new_board for val in row)
    score_gain = new_sum - old_sum
    
    # Bonus ÉNORME pour grosse tuile
    max_tile = max(val for row in new_board for val in row)
    tile_bonus = max_tile * 0.1  # Au lieu de log2!
    
    # Bonus espaces vides (crucial!)
    empty_cells = sum(1 for row in new_board for val in row if val == 0)
    empty_bonus = empty_cells * 10
    
    # Bonus monotonie (tuiles en ordre)
    monotonicity_bonus = calculate_monotonicity(new_board) * 5
    
    # Pénalité game over MASSIVE
    game_over_penalty = -100.0 if game_over else 0.0
    
    total = score_gain + tile_bonus + empty_bonus + monotonicity_bonus + game_over_penalty
    return total / 10  # Normaliser
```

### Solution 2 : Learning Rate + Episodes

**Recommandation** :
```python
# Augmenter LR
lr = 0.0005  # Au lieu de 0.000149

# Entraîner BEAUCOUP plus
episodes = 10000  # Au lieu de 100-1000
```

**Résultat attendu** : Score 3000-6000 après 10000 épisodes

### Solution 3 : State Augmentation

Ajouter des features à la représentation :

```python
def preprocess_state_advanced(board):
    state = []
    
    # 1. Grille normalisée
    for row in board:
        for val in row:
            state.append(math.log2(val + 1))
    
    # 2. Max tile
    max_tile = max(val for row in board for val in row)
    state.append(math.log2(max_tile + 1))
    
    # 3. Espaces vides
    empty = sum(1 for row in board for val in row if val == 0)
    state.append(empty / 16)
    
    # 4. Monotonie
    mono = calculate_monotonicity(board)
    state.append(mono)
    
    # 5. Score actuel (normalisé)
    # ...
    
    return torch.tensor(state, dtype=torch.float32, device=device)
```

### Solution 4 : Architecture CNN (Avancé)

Remplacer MLP par CNN pour capturer patterns spatiaux :

```python
class DQN_CNN(nn.Module):
    def __init__(self):
        super().__init__()
        # 4x4 grid → CNN
        self.conv1 = nn.Conv2d(1, 128, kernel_size=2)  # → 3x3
        self.conv2 = nn.Conv2d(128, 256, kernel_size=2)  # → 2x2
        self.fc1 = nn.Linear(256 * 2 * 2, 256)
        self.fc2 = nn.Linear(256, 4)
    
    def forward(self, x):
        # x shape: (batch, 16) → reshape to (batch, 1, 4, 4)
        x = x.view(-1, 1, 4, 4)
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)
```

## 🎯 Plan d'Action Recommandé

### Rapide (2h) - Impact Moyen (+50-100%)

1. **Augmenter LR** : 0.000149 → 0.0005
2. **Entraîner 5000 épisodes** sur GPU
3. Espérer score 2000-3000

### Moyen (4h) - Impact Fort (+100-200%)

1. **Améliorer reward function** (code ci-dessus)
2. **Augme
nter state** (features supplémentaires)
3. **Entraîner 10000 épisodes**
4. Espérer score 3000-5000

### Long (1 jour) - Impact Maximum (+200-400%)

1. **Implémenter CNN**
2. **Reward shaping expert**
3. **State augmentation complète**
4. **20000+ épisodes**
5. **Espérer score 5000-8000** (rivalise Expectimax)

## 📊 Pourquoi DQN est Difficile pour 2048

### Challenges Spécifiques

1. **Espace d'états énorme** : 2^16 états possibles
2. **Récompenses éparses** : Peu de feedback immédiat
3. **Besoin de planification long terme** : Expectimax regarde 3-5 coups à l'avance
4. **Patterns spatiaux cruciaux** : Coins, monotonie, etc.

### Pourquoi Heuristic/Expectimax Gagnent

**Heuristic** :
- ✅ Règles expertes codées (monotonie, corners, etc.)
- ✅ Pas besoin d'apprentissage
- ✅ Consultation immédiate

**Expectimax** :
- ✅ Recherche arborescente (voit le futur)
- ✅ Combine heuristiques + lookahead
- ✅ Déterministe et optimal localement

**DQN** :
- ❌ Doit **apprendre** ces patterns
- ❌ Pas de lookahead explicite
- ❌ Besoin de **dizaines de milliers** d'épisodes

## 🔬 Tests Recommandés

### Test 1 : Reward Impact

Modifiez `calculate_reward` avec la version améliorée, entraînez 1000 épisodes, comparez.

### Test 2 : LR Impact

Testez avec `lr = 0.0005` vs `lr = 0.000149`, 2000 épisodes chacun.

### Test 3 : CNN vs MLP

Implémentez CNN simple, comparez après 5000 épisodes.

## 💡 Recommandation Immédiate

**Pour améliorer RAPIDEMENT** (1-2h de travail) :

1. **Créez `dqn_agent_improved.py`** avec :
   - `lr = 0.0005`
   - reward amélioré (ci-dessus)
   - state augmenté

2. **Entraînez 10000 épisodes** sur GPU
   ```bash
   # ~2-3h sur RTX 4070
   .\.venv_gpu\Scripts\python train_improved_dqn.py
   ```

3. **Attendez score 3000-5000** au lieu de 1200

## 🎮 Réalité sur DQN pour 2048

**Verdict** : 
- ✅ DQN **peut** atteindre 4000-8000 avec bon tuning
- ⚠️ Nécessite **beaucoup** d'épisodes (10000-50000)
- ⚠️ Reward engineering crucial
- ⚠️ Plus dur que Atari (espace d'états plus grand)

**Alternatives** :
1. **Continuer DQN** avec améliorations (patient mais pédagogique)
2. **Utiliser Expectimax** pour meilleurs scores immédiats
3. **Combiner** : DQN pour apprendre, Expectimax pour exploiter

---

**TL;DR** : Votre DQN est limité par :
1. ❌ LR trop faible (0.000149)
2. ❌ Pas assez d'épisodes (~1000 au lieu de 10000+)
3. ❌ Reward trop simple
4. ❌ State representation basique

**Solution rapide** : LR à 0.0005 + 10000 épisodes = Score 3000-5000 attendu ! 🚀
