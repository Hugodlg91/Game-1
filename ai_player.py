"""AI player for 2048.

Provides `choose_best_move(game)` which returns one of: "up", "down", "left", "right".

The AI scores resulting boards using a combination of heuristics:
 - monotonicity (higher better)
 - smoothness (lower neighboring differences better)
 - max tile in corner (boolean)
 - empty cell count

We apply each possible move to a copy of the board (without spawning a random tile)
and pick the move with the highest heuristic score.
"""
from __future__ import annotations

from typing import List, Tuple, Optional
import math


def _log2(v: int) -> float:
    return math.log2(v) if v > 0 else 0.0


def _apply_collapse_line(line: List[int]) -> Tuple[List[int], int]:
    """Replicate collapse logic from Game2048 for a single line.

    Returns (collapsed_line, gained_score).
    """
    filtered = [v for v in line if v != 0]
    merged: List[int] = []
    gained = 0
    idx = 0
    size = len(line)
    while idx < len(filtered):
        if idx + 1 < len(filtered) and filtered[idx] == filtered[idx + 1]:
            new_value = filtered[idx] * 2
            merged.append(new_value)
            gained += new_value
            idx += 2
        else:
            merged.append(filtered[idx])
            idx += 1
    merged.extend([0] * (size - len(merged)))
    return merged, gained


def apply_move_board(board: List[List[int]], direction: str) -> Tuple[List[List[int]], bool, int]:
    """Return (new_board, moved, gained) after applying move to board.

    This function does NOT spawn a new random tile (deterministic simulation).
    """
    size = len(board)
    moved = False
    total_gained = 0
    new_board = [[0] * size for _ in range(size)]

    for idx in range(size):
        if direction in {"left", "right"}:
            line = list(board[idx])
        else:
            line = [board[r][idx] for r in range(size)]

        if direction in {"right", "down"}:
            line = list(reversed(line))

        collapsed, gained = _apply_collapse_line(line)
        total_gained += gained

        if direction in {"right", "down"}:
            collapsed.reverse()

        if direction in {"left", "right"}:
            new_board[idx] = collapsed
            if collapsed != board[idx]:
                moved = True
        else:
            for r in range(size):
                new_board[r][idx] = collapsed[r]
            if collapsed != [board[r][idx] for r in range(size)]:
                moved = True

    return new_board, moved, total_gained


def _monotonicity(board: List[List[int]]) -> float:
    """Measure monotonicity: higher when rows/cols are consistently increasing/decreasing.

    We use log2 of tile values to compare magnitudes.
    """
    size = len(board)
    total = 0.0

    # Rows
    for r in range(size):
        values = [_log2(v) for v in board[r]]
        inc = 0.0
        dec = 0.0
        for i in range(size - 1):
            diff = values[i] - values[i + 1]
            if diff > 0:
                inc += diff
            else:
                dec += -diff
        total += max(inc, dec)

    # Columns
    for c in range(size):
        values = [_log2(board[r][c]) for r in range(size)]
        inc = 0.0
        dec = 0.0
        for i in range(size - 1):
            diff = values[i] - values[i + 1]
            if diff > 0:
                inc += diff
            else:
                dec += -diff
        total += max(inc, dec)

    return total


def _smoothness(board: List[List[int]]) -> float:
    """Lower neighboring differences are better; we return a positive score where
    larger is better (so we negate the sum of absolute differences).
    """
    size = len(board)
    score = 0.0
    for r in range(size):
        for c in range(size):
            v = _log2(board[r][c])
            if board[r][c] == 0:
                continue
            # right neighbor
            if c + 1 < size and board[r][c + 1] != 0:
                score -= abs(v - _log2(board[r][c + 1]))
            # down neighbor
            if r + 1 < size and board[r + 1][c] != 0:
                score -= abs(v - _log2(board[r + 1][c]))
    return score


def _max_tile_in_corner(board: List[List[int]]) -> int:
    size = len(board)
    corners = [board[0][0], board[0][size - 1], board[size - 1][0], board[size - 1][size - 1]]
    max_tile = max(v for row in board for v in row)
    return 1 if max_tile in corners else 0


def _empty_cells(board: List[List[int]]) -> int:
    return sum(1 for row in board for v in row if v == 0)


def score_board(board: List[List[int]]) -> float:
    """Compute the weighted score of a board according to heuristics described.
    Weights:
      1.0 * monotonicity
      0.1 * smoothness
      2.0 * max_tile_corner
      2.5 * empty_cells
    """
    mono = _monotonicity(board)
    smooth = _smoothness(board)
    corner = _max_tile_in_corner(board)
    empty = _empty_cells(board)

    total = 1.0 * mono + 0.1 * smooth + 2.0 * corner + 2.5 * empty
    return total


def choose_best_move(game) -> Optional[str]:
    """Given a `Game2048` instance, evaluate the four moves and return best move string.

    The function does not mutate the provided game object.
    """
    moves = ["up", "down", "left", "right"]
    best_move: Optional[str] = None
    best_score = float("-inf")

    board = game.board

    for m in moves:
        new_board, moved, _ = apply_move_board(board, m)
        if not moved:
            continue
        sc = score_board(new_board)
        if sc > best_score:
            best_score = sc
            best_move = m

    return best_move
