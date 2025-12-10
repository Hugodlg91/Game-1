"""Console main menu for 2048.

Provides options to play manually, autoplay (heuristic), Q-learning train/play, and settings.
"""
from __future__ import annotations

import sys
from typing import Optional

from game_2048 import play_game, Game2048
import ai_player
import q_learning_agent
import settings


def _prompt(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def show_menu() -> None:
    while True:
        print("\n=== 2048 Main Menu ===")
        print("1. Play (manual)")
        print("2. Autoplay (heuristic AI)")
        print("3. Q-Learning AI")
        print("4. Settings (key bindings)")
        print("5. Quit")
        choice = _prompt("Choose an option [1-5]: ")
        if choice == "1":
            play_game()
        elif choice == "2":
            play_game(ai=True)
        elif choice == "3":
            q_learning_menu()
        elif choice == "4":
            settings.configure_keybindings()
        elif choice == "5" or choice.lower() in {"q", "quit"}:
            print("Goodbye")
            return
        else:
            print("Invalid choice")


def q_learning_menu() -> None:
    print("\nQ-Learning Menu")
    print("1. Train Q-table")
    print("2. Play using learned Q-table")
    print("3. Back")
    choice = _prompt("Choose [1-3]: ")
    if choice == "1":
        eps = int(_prompt("Episodes to train (e.g. 1000): ") or "1000")
        alpha = float(_prompt("Alpha (learning rate) [0.1]: ") or "0.1")
        gamma = float(_prompt("Gamma (discount) [0.9]: ") or "0.9")
        epsilon = float(_prompt("Epsilon (exploration) [0.2]: ") or "0.2")
        print("Training Q-table...")
        q_learning_agent.train_q_learning(episodes=eps, alpha=alpha, gamma=gamma, epsilon=epsilon)
        print("Training complete and saved to qtable.pkl")
    elif choice == "2":
        qtable = q_learning_agent.load_qtable()
        if not qtable:
            print("No Q-table found. Train first.")
            return
        print("Starting autoplay using Q-table (press Ctrl+C to stop)")
        game = Game2048()
        try:
            while True:
                print(game.render())
                if not game.has_moves_available():
                    print("Game over")
                    break
                action = q_learning_agent.choose_action_from_q(game, qtable)
                if action is None:
                    break
                game.move(action)
        except KeyboardInterrupt:
            print("Stopped")
    else:
        return


if __name__ == "__main__":
    show_menu()
