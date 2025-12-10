"""Lightweight Q-learning agent for 2048.

Implements a tabular Q-table on a small hand-crafted feature vector.
Q is stored as a dict mapping (feature_tuple, action) -> float and pickled to disk.
"""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import Dict, Tuple, Any, List
import random

import math

from game_2048 import Game2048
import ai_player

QFILE = Path("qtable.pkl")
ACTIONS = ["up", "down", "left", "right"]


def extract_features(board: List[List[int]]) -> Tuple[int, int, float, float]:
    """Return feature tuple: (empty_count, max_tile, monotonicity, smoothness).

Monotonicity and smoothness reuse ai_player helpers.
"""
    empty = sum(1 for row in board for v in row if v == 0)
    max_tile = max(v for row in board for v in row)
    mono = ai_player._monotonicity(board)
    smooth = ai_player._smoothness(board)
    # discretize floats to reduce state space
    mono_bucket = round(mono, 2)
    smooth_bucket = round(smooth, 2)
    return (empty, int(max_tile), mono_bucket, smooth_bucket)


def load_qtable() -> Dict[Tuple[Any, str], float]:
    if QFILE.exists():
        try:
            with QFILE.open("rb") as fh:
                return pickle.load(fh)
        except Exception:
            return {}
    return {}


def save_qtable(qtable: Dict[Tuple[Any, str], float]) -> None:
    with QFILE.open("wb") as fh:
        pickle.dump(qtable, fh)


def select_action(qtable: Dict, features: Tuple, epsilon: float) -> str:
    # epsilon-greedy
    if random.random() < epsilon:
        return random.choice(ACTIONS)
    # pick best Q among actions
    best_a = None
    best_q = float("-inf")
    for a in ACTIONS:
        q = qtable.get((features, a), 0.0)
        if q > best_q:
            best_q = q
            best_a = a
    if best_a is None:
        return random.choice(ACTIONS)
    return best_a


def update_q_value(qtable: Dict, features, action: str, reward: float, next_features, alpha: float, gamma: float) -> None:
    key = (features, action)
    q = qtable.get(key, 0.0)
    # estimate max next Q
    max_next = max(qtable.get((next_features, a), 0.0) for a in ACTIONS)
    q_new = q + alpha * (reward + gamma * max_next - q)
    qtable[key] = q_new


def train_q_learning(episodes: int = 1000, alpha: float = 0.1, gamma: float = 0.9, epsilon: float = 0.2) -> Dict:
    # legacy blocking trainer kept for compatibility
    qtable: Dict[Tuple[Any, str], float] = load_qtable()
    for ep in range(episodes):
        game = Game2048()
        features = extract_features(game.board)
        steps = 0
        while game.has_moves_available():
            action = select_action(qtable, features, epsilon)
            new_board, moved, reward = ai_player.apply_move_board(game.board, action)
            if not moved:
                reward = -1.0
                next_features = features
            else:
                g2 = Game2048(size=game.size, rng=random.Random())
                g2.board = [row.copy() for row in new_board]
                g2.add_random_tile()
                next_features = extract_features(g2.board)

            update_q_value(qtable, features, action, reward, next_features, alpha, gamma)
            if moved:
                game.move(action)
            steps += 1
            if steps > 10000:
                break
        if (ep + 1) % 50 == 0:
            save_qtable(qtable)
    save_qtable(qtable)
    return qtable


class Trainer:
    """Incremental trainer for use by UI. Call step() repeatedly.

    The trainer maintains an internal episode/game state and performs small updates.
    """
    def __init__(self, episodes: int = 1000, alpha: float = 0.1, gamma: float = 0.9, epsilon: float = 0.2):
        self.episodes = episodes
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.qtable = load_qtable()
        self.episode = 0
        self.step_in_episode = 0
        self.game = Game2048()
        self.features = extract_features(self.game.board)

    def step(self) -> bool:
        """Perform a single action-step in training. Returns True if training finished."""
        if self.episode >= self.episodes:
            return True
        action = select_action(self.qtable, self.features, self.epsilon)
        new_board, moved, reward = ai_player.apply_move_board(self.game.board, action)
        if not moved:
            reward = -1.0
            next_features = self.features
        else:
            # create realistic next features
            g2 = Game2048(size=self.game.size, rng=random.Random())
            g2.board = [row.copy() for row in new_board]
            g2.add_random_tile()
            next_features = extract_features(g2.board)

        update_q_value(self.qtable, self.features, action, reward, next_features, self.alpha, self.gamma)
        if moved:
            self.game.move(action)
            self.features = extract_features(self.game.board)

        self.step_in_episode += 1
        if not self.game.has_moves_available() or self.step_in_episode > 10000:
            # episode done
            self.episode += 1
            self.step_in_episode = 0
            self.game = Game2048()
            self.features = extract_features(self.game.board)
            # periodically save
            if self.episode % 50 == 0:
                save_qtable(self.qtable)

        return self.episode >= self.episodes

    def status(self):
        return {"episode": self.episode, "episodes": self.episodes, "step": self.step_in_episode, "epsilon": self.epsilon, "qsize": len(self.qtable)}

    def current_board(self):
        return self.game.board



def choose_action_from_q(game: Game2048, qtable: Dict) -> str:
    features = extract_features(game.board)
    # epsilon = 0 for greedy play
    return select_action(qtable, features, epsilon=0.0)
