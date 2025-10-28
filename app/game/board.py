"""Core Tic-Tac-Toe game logic."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass
class Move:
    row: int
    col: int

    def __post_init__(self) -> None:
        if not (0 <= self.row <= 2 and 0 <= self.col <= 2):
            raise ValueError("Row and column must be between 0 and 2 inclusive")


class Board:
    """Represents a Tic-Tac-Toe board."""

    def __init__(self) -> None:
        self._cells: List[List[str]] = [[" " for _ in range(3)] for _ in range(3)]
        self.current_player: str = "X"
        self.winner: Optional[str] = None

    def available_moves(self) -> Iterable[Move]:
        for row in range(3):
            for col in range(3):
                if self._cells[row][col] == " ":
                    yield Move(row, col)

    def play(self, move: Move) -> None:
        if self.winner is not None:
            raise ValueError("Game is already over")
        if self._cells[move.row][move.col] != " ":
            raise ValueError("Cell already taken")
        self._cells[move.row][move.col] = self.current_player
        if self._has_winner(self.current_player):
            self.winner = self.current_player
        elif all(cell != " " for row in self._cells for cell in row):
            self.winner = "draw"
        else:
            self.current_player = "O" if self.current_player == "X" else "X"

    def _has_winner(self, player: str) -> bool:
        lines = []
        lines.extend(self._cells)
        lines.extend([[self._cells[r][c] for r in range(3)] for c in range(3)])
        lines.append([self._cells[i][i] for i in range(3)])
        lines.append([self._cells[i][2 - i] for i in range(3)])
        return any(all(cell == player for cell in line) for line in lines)

    def render(self) -> str:
        rows = [" | ".join(row) for row in self._cells]
        divider = "\n---------\n"
        return divider.join(rows)

    def clone(self) -> "Board":
        clone = Board()
        clone._cells = [row[:] for row in self._cells]
        clone.current_player = self.current_player
        clone.winner = self.winner
        return clone
