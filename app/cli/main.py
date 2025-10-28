"""Command-line utilities for playing Tic-Tac-Toe locally."""
from __future__ import annotations

from typing import Callable

from app.game.board import Board, Move


def ask_move(input_fn: Callable[[str], str]) -> Move:
    while True:
        try:
            answer = input_fn("Entrez votre coup (ligne,colonne): ")
            row_str, col_str = answer.split(",")
            return Move(int(row_str), int(col_str))
        except ValueError:
            print("Format invalide. Utilisez 'ligne,colonne' avec des chiffres entre 0 et 2.")


def play_local() -> None:
    board = Board()
    print("Bienvenue dans le morpion ! Joueur X commence. Les indices vont de 0 à 2.")

    while board.winner is None:
        print("\n" + board.render())
        print(f"C'est au tour du joueur {board.current_player}.")
        move = ask_move(input)
        try:
            board.play(move)
        except ValueError as exc:
            print(f"Coup invalide: {exc}")
            continue

    print("\n" + board.render())
    if board.winner == "draw":
        print("Match nul !")
    else:
        print(f"Le joueur {board.winner} a gagné !")


if __name__ == "__main__":
    play_local()
