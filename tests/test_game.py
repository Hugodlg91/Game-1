import pathlib
import random
import sys
import unittest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from game_2048 import Game2048


class Game2048Tests(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(0)

    def test_move_left_combines_tiles(self):
        game = Game2048(size=4, rng=self.rng, initial_tiles=0)
        game.board = [
            [2, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]

        moved = game.move("left")

        self.assertTrue(moved)
        self.assertEqual(game.board[0][:2], [4, 0])
        self.assertEqual(game.score, 4)

    def test_move_right_handles_double_merge(self):
        game = Game2048(size=4, rng=self.rng, initial_tiles=0)
        game.board = [
            [2, 2, 2, 2],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]

        moved = game.move("right")

        self.assertTrue(moved)
        self.assertEqual(game.board[0], [0, 0, 4, 4])
        self.assertEqual(game.score, 8)

    def test_move_returns_false_when_no_change(self):
        game = Game2048(size=4, rng=self.rng, initial_tiles=0)
        game.board = [
            [2, 4, 2, 4],
            [4, 2, 4, 2],
            [2, 4, 2, 4],
            [4, 2, 4, 2],
        ]

        moved = game.move("left")

        self.assertFalse(moved)
        self.assertEqual(game.score, 0)

    def test_has_won_detects_2048(self):
        game = Game2048(size=4, rng=self.rng, initial_tiles=0)
        game.board = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 2048],
        ]

        self.assertTrue(game.has_won())

    def test_initial_tiles_are_reproducible_with_seed(self):
        seeded_rng = random.Random(123)
        game = Game2048(size=4, rng=seeded_rng)

        self.assertEqual(game.score, 0)
        self.assertEqual(game.board, [
            [0, 2, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 2, 0, 0],
        ])


if __name__ == "__main__":
    unittest.main()
