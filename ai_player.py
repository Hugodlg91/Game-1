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


def score_board(board: List[List[int]], weights: Optional[dict] = None) -> float:
    """Compute the weighted score of a board according to heuristics.
    
    Args:
        board: 4x4 game board
        weights: Optional dict with keys 'mono', 'smooth', 'corner', 'empty'.
                 Default: {'mono': 1.0, 'smooth': 0.1, 'corner': 2.0, 'empty': 2.5}
    
    Returns:
        Weighted heuristic score
    """
    # Default weights (original values)
    if weights is None:
        weights = {
            'mono': 1.0,
            'smooth': 0.1,
            'corner': 2.0,
            'empty': 2.5
        }
    
    mono = _monotonicity(board)
    smooth = _smoothness(board)
    corner = _max_tile_in_corner(board)
    empty = _empty_cells(board)

    total = (
        weights.get('mono', 1.0) * mono +
        weights.get('smooth', 0.1) * smooth +
        weights.get('corner', 2.0) * corner +
        weights.get('empty', 2.5) * empty
    )
    return total


def choose_best_move(game, weights: Optional[dict] = None) -> Optional[str]:
    """Given a `Game2048` instance, evaluate the four moves and return best move string.

    The function does not mutate the provided game object.
    
    Args:
        game: Game2048 instance
        weights: Optional heuristic weights dict
    
    Returns:
        Best move direction or None
    """
    moves = ["up", "down", "left", "right"]
    best_move: Optional[str] = None
    best_score = float("-inf")

    board = game.board

    for m in moves:
        new_board, moved, _ = apply_move_board(board, m)
        if not moved:
            continue
        sc = score_board(new_board, weights=weights)
        if sc > best_score:
            best_score = sc
            best_move = m

    return best_move


# ============================================================================
# EXPECTIMAX AI WITH BITBOARDS
# ============================================================================

try:
    from bitboard_2048 import (
        board_to_bitboard,
        bitboard_to_board,
        move_left,
        move_right,
        move_up,
        move_down,
        get_empty_positions,
        count_empty,
        add_tile,
        is_game_over,
    )
    BITBOARD_AVAILABLE = True
except ImportError:
    BITBOARD_AVAILABLE = False


# Transposition table for caching evaluated states
_transposition_table: dict[int, float] = {}


def _clear_transposition_table() -> None:
    """Clear the transposition table to free memory."""
    global _transposition_table
    _transposition_table = {}


def score_board_from_bitboard(bb: int, weights: Optional[dict] = None) -> float:
    """
    Evaluate a bitboard using existing heuristics.
    
    Args:
        bb: Bitboard representation of the game state
        weights: Optional heuristic weights dict
    
    Returns:
        Heuristic score
    """
    board = bitboard_to_board(bb)
    return score_board(board, weights=weights)


def _expectimax_search(bb: int, depth: int, is_max_node: bool, alpha: float = float('-inf'), weights: Optional[dict] = None) -> float:
    """
    Recursive Expectimax search.
    
    Args:
        bb: Current bitboard state
        depth: Remaining search depth
        is_max_node: True for Max nodes (player), False for Chance nodes (computer)
        alpha: Alpha value for pruning (optional optimization)
        weights: Optional heuristic weights dict
    
    Returns:
        Expected value of the position
    """
    # Check cache
    if bb in _transposition_table:
        return _transposition_table[bb]
    
    # Base case: depth 0 or game over
    if depth == 0 or is_game_over(bb):
        score = score_board_from_bitboard(bb, weights=weights)
        _transposition_table[bb] = score
        return score
    
    if is_max_node:
        # MAX NODE: Player chooses the best move
        max_score = float('-inf')
        
        for move_func in [move_up, move_down, move_left, move_right]:
            new_bb, score_gained = move_func(bb)
            
            # Skip if move doesn't change the board
            if new_bb == bb:
                continue
            
            # Recursively evaluate the chance node
            expected_value = _expectimax_search(new_bb, depth, False, max_score, weights=weights)
            
            # Add the immediate score gained from merging
            total_score = expected_value + score_gained * 0.1  # Weight merge score
            
            max_score = max(max_score, total_score)
        
        # Cache and return
        if max_score != float('-inf'):
            _transposition_table[bb] = max_score
            return max_score
        else:
            # No valid moves
            score = score_board_from_bitboard(bb, weights=weights)
            _transposition_table[bb] = score
            return score
    
    else:
        # CHANCE NODE: Computer places random tile
        empty_positions = get_empty_positions(bb)
        
        if not empty_positions:
            # No empty cells
            score = score_board_from_bitboard(bb, weights=weights)
            _transposition_table[bb] = score
            return score
        
        expected_value = 0.0
        
        # For performance, limit the number of empty cells we consider
        # If there are many empty cells, sample a subset
        if len(empty_positions) > 6:
            # Only consider a subset of positions for better performance
            import random
            sample_positions = random.sample(empty_positions, 6)
        else:
            sample_positions = empty_positions
        
        for pos in sample_positions:
            # 90% chance of spawning a '2' (exp_value = 1)
            bb_with_2 = add_tile(bb, pos, 1)
            score_2 = _expectimax_search(bb_with_2, depth - 1, True, alpha, weights=weights)
            expected_value += 0.9 * score_2
            
            # 10% chance of spawning a '4' (exp_value = 2)
            bb_with_4 = add_tile(bb, pos, 2)
            score_4 = _expectimax_search(bb_with_4, depth - 1, True, alpha, weights=weights)
            expected_value += 0.1 * score_4
        
        # Average over all positions
        expected_value /= len(sample_positions)
        
        # Cache and return
        _transposition_table[bb] = expected_value
        return expected_value


def expectimax_choose_move(game, depth: int = 3, clear_cache: bool = True, weights: Optional[dict] = None) -> Optional[str]:
    """
    Choose the best move using Expectimax algorithm with bitboard optimization.
    
    This is the main entry point for the high-performance AI. It performs a
    multi-level lookahead search considering both player moves and random tile
    placements.
    
    Args:
        game: Game2048 instance
        depth: Search depth (recommended: 3-4 for real-time play, 5+ for analysis)
        clear_cache: Whether to clear the transposition table before search
        weights: Optional heuristic weights dict (mono, smooth, corner, empty)
    
    Returns:
        Best move direction ("up", "down", "left", "right") or None if no valid moves
    
    Example:
        >>> from game_2048 import Game2048
        >>> game = Game2048()
        >>> move = expectimax_choose_move(game, depth=3)
        >>> game.move(move)
    """
    if not BITBOARD_AVAILABLE:
        raise ImportError("Bitboard module not available. Cannot use Expectimax AI.")
    
    # Clear cache if requested
    if clear_cache:
        _clear_transposition_table()
    
    # Convert current board to bitboard
    bb = board_to_bitboard(game.board)
    
    # Try each direction and pick the best
    moves = [
        ("up", move_up),
        ("down", move_down),
        ("left", move_left),
        ("right", move_right),
    ]
    
    best_move: Optional[str] = None
    best_score = float('-inf')
    
    for move_name, move_func in moves:
        new_bb, score_gained = move_func(bb)
        
        # Skip if move doesn't change the board
        if new_bb == bb:
            continue
        
        # Evaluate this move using expectimax search
        expected_value = _expectimax_search(new_bb, depth, False, weights=weights)
        
        # Add immediate merge score
        total_score = expected_value + score_gained * 0.1
        
        if total_score > best_score:
            best_score = total_score
            best_move = move_name
    
    return best_move
