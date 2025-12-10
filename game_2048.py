"""
Console-based 2048 implementation.

Run the game with:

    python game_2048.py

Use W/A/S/D keys (or U/L/D/R) to slide tiles.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Sequence

DIRECTIONS = {
    "w": "up",
    "u": "up",
    "a": "left",
    "l": "left",
    "s": "down",
    "d": "right",
    "r": "right",
}


@dataclass
class Game2048:
    """Basic game state and rules for 2048."""

    size: int = 4
    rng: random.Random = field(default_factory=random.Random)
    initial_tiles: int = 2

    def __post_init__(self) -> None:
        self.board: List[List[int]] = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.score: int = 0
        for _ in range(self.initial_tiles):
            self.add_random_tile()

    def add_random_tile(self) -> bool:
        """Add a 2 or 4 to a random empty cell. Returns True if a tile was added."""
        empties = [(row, col) for row in range(self.size) for col in range(self.size) if self.board[row][col] == 0]
        if not empties:
            return False
        row, col = self.rng.choice(empties)
        self.board[row][col] = 4 if self.rng.random() < 0.1 else 2
        return True

    def has_moves_available(self) -> bool:
        """Return True if at least one move is possible."""
        if any(0 in row for row in self.board):
            return True
        for row in range(self.size):
            for col in range(self.size):
                if row + 1 < self.size and self.board[row][col] == self.board[row + 1][col]:
                    return True
                if col + 1 < self.size and self.board[row][col] == self.board[row][col + 1]:
                    return True
        return False

    def _collapse_line(self, line: Sequence[int]) -> tuple[list[int], int]:
        """Collapse a single row/column toward the front.

        Returns the collapsed line and the score gained during merges.
        """
        filtered = [value for value in line if value]
        merged: list[int] = []
        gained = 0
        idx = 0
        while idx < len(filtered):
            if idx + 1 < len(filtered) and filtered[idx] == filtered[idx + 1]:
                new_value = filtered[idx] * 2
                merged.append(new_value)
                gained += new_value
                idx += 2
            else:
                merged.append(filtered[idx])
                idx += 1
        merged.extend([0] * (self.size - len(merged)))
        return merged, gained

    def move(self, direction: str) -> bool:
        """Slide tiles toward the given direction.

        Returns True if the board changed.
        """
        direction = direction.lower()
        if direction not in {"up", "down", "left", "right"}:
            raise ValueError("Invalid direction. Use up, down, left, or right.")

        moved = False
        total_gained = 0

        def set_line(idx: int, new_line: list[int]) -> None:
            if direction in {"left", "right"}:
                self.board[idx] = new_line
            else:
                for row in range(self.size):
                    self.board[row][idx] = new_line[row]

        for idx in range(self.size):
            if direction in {"left", "right"}:
                line = self.board[idx]
            else:
                line = [self.board[row][idx] for row in range(self.size)]

            if direction in {"right", "down"}:
                line = list(reversed(line))

            collapsed, gained = self._collapse_line(line)
            total_gained += gained

            if direction in {"right", "down"}:
                collapsed.reverse()

            if direction in {"left", "right"}:
                changed = collapsed != self.board[idx]
            else:
                changed = collapsed != [self.board[row][idx] for row in range(self.size)]

            if changed:
                moved = True
                set_line(idx, collapsed)

        if moved:
            self.score += total_gained
            self.add_random_tile()
        return moved

    def render(self) -> str:
        """Return a pretty string representation of the board."""
        border = "+" + "+".join(["----"] * self.size) + "+"
        rows = [border]
        for row in self.board:
            cells = "|" + "|".join(f"{value:^4}" if value else "    " for value in row) + "|"
            rows.append(cells)
            rows.append(border)
        rows.append(f"Score: {self.score}")
        return "\n".join(rows)

    def has_won(self) -> bool:
        return any(value >= 2048 for row in self.board for value in row)


def prompt_move() -> str:
    print("Enter move (W/A/S/D or Q to quit): ", end="", flush=True)
    choice = input().strip().lower()
    if choice == "q":
        raise KeyboardInterrupt
    if choice in DIRECTIONS:
        return DIRECTIONS[choice]
    raise ValueError("Input must be one of W/A/S/D (or U/L/D/R)")


def play_game(size: int = 4, seed: int | None = None, initial_tiles: int = 2) -> None:
    """Launch an interactive 2048 game."""

    rng = random.Random(seed)
    game = Game2048(size=size, rng=rng, initial_tiles=initial_tiles)
    print("Welcome to 2048! Reach 2048 to win.\n")
    try:
        while True:
            print(game.render())
            if game.has_won():
                print("Congratulations, you reached 2048! Continue playing or press Ctrl+C to exit.")
            if not game.has_moves_available():
                print("No moves left. Game over!")
                break
            try:
                direction = prompt_move()
            except ValueError as error:
                print(error)
                continue
            game.move(direction)
    except KeyboardInterrupt:
        print("\nThanks for playing!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Play the 2048 game in your terminal.")
    parser.add_argument("--size", type=int, default=4, help="Board dimension (default: 4)")
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed for the random generator to make runs reproducible (default: random)",
    )
    parser.add_argument(
        "--initial-tiles",
        type=int,
        default=2,
        help="How many tiles to spawn at game start (default: 2)",
    )

    args = parser.parse_args()
    if args.size < 2:
        raise SystemExit("Board size must be at least 2.")
    if args.initial_tiles < 0 or args.initial_tiles > args.size**2:
        raise SystemExit("Initial tiles must be between 0 and the number of cells.")

    play_game(size=args.size, seed=args.seed, initial_tiles=args.initial_tiles)