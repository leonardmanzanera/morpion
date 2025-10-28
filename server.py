"""Asynchronous TCP server to play Tic-Tac-Toe over the network."""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from typing import Optional

from app.game.board import Board, Move

WELCOME = "Bienvenue sur le serveur de morpion !"
INSTRUCTIONS = (
    "Les coups s\u00e9crivent sous la forme 'ligne,colonne' avec des valeurs entre 0 et 2.\n"
    "Entrez QUIT pour abandonner."
)


@dataclass
class Player:
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    name: str
    symbol: str = ""
    finished: asyncio.Event = field(default_factory=asyncio.Event)

    async def send(self, message: str) -> None:
        if self.writer.is_closing():
            raise ConnectionError("connexion ferm\u00e9e")
        self.writer.write((message + "\n").encode())
        await self.writer.drain()

    async def recv(self) -> Optional[str]:
        data = await self.reader.readline()
        if not data:
            return None
        return data.decode().strip()

    async def close(self) -> None:
        if not self.writer.is_closing():
            try:
                self.writer.write("Au revoir !\n".encode())
                await self.writer.drain()
            except Exception:  # pragma: no cover - la connexion peut \u00eatre d\u00e9j\u00e0 coup\u00e9e
                pass
            self.writer.close()
        self.finished.set()
        try:
            await self.writer.wait_closed()
        except Exception:
            pass


waiting_players: "asyncio.Queue[Player]" = asyncio.Queue()


async def run_game(player_x: Player, player_o: Player) -> None:
    board = Board()
    player_x.symbol = "X"
    player_o.symbol = "O"
    await asyncio.gather(player_x.send(WELCOME), player_o.send(WELCOME))
    await asyncio.gather(player_x.send(INSTRUCTIONS), player_o.send(INSTRUCTIONS))
    await asyncio.gather(
        player_x.send("Vous jouez avec les X. Vous commencez."),
        player_o.send("Vous jouez avec les O. Attendez votre tour."),
    )

    players = {"X": player_x, "O": player_o}

    try:
        while board.winner is None:
            current = players[board.current_player]
            other = players["O" if board.current_player == "X" else "X"]

            await current.send("\n" + board.render())
            await current.send("C'est \u00e0 vous de jouer :")
            await other.send("\n" + board.render())
            await other.send("L'autre joueur r\u00e9fl\u00e9chit...")

            move_raw = await current.recv()
            if move_raw is None or move_raw.upper() == "QUIT":
                await other.send("Votre adversaire a quitt\u00e9 la partie.")
                return
            try:
                row_str, col_str = move_raw.split(",")
                move = Move(int(row_str), int(col_str))
                board.play(move)
            except Exception as exc:  # ValueError ou autre
                await current.send(f"Coup invalide ({exc}). Essayez de nouveau.")
                continue

        await players["X"].send("\n" + board.render())
        await players["O"].send("\n" + board.render())
        if board.winner == "draw":
            await asyncio.gather(
                player_x.send("Match nul !"),
                player_o.send("Match nul !"),
            )
        else:
            winner_player = players[board.winner]
            loser_player = players["O" if board.winner == "X" else "X"]
            await winner_player.send("Bravo, vous avez gagn\u00e9 !")
            await loser_player.send("Dommage, vous avez perdu.")
    finally:
        await asyncio.gather(player_x.close(), player_o.close())


async def player_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    peer = writer.get_extra_info("peername")
    name = f"{peer[0]}:{peer[1]}" if peer else "joueur"
    player = Player(reader, writer, name)
    await player.send(WELCOME)
    await player.send("En attente d'un adversaire...")
    await waiting_players.put(player)
    await player.finished.wait()


async def game_dispatcher() -> None:
    while True:
        player_x = await waiting_players.get()
        player_o = await waiting_players.get()
        asyncio.create_task(run_game(player_x, player_o))


async def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    host = "0.0.0.0"
    server = await asyncio.start_server(player_handler, host, port)
    addr = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
    print(f"Serveur en \u00e9coute sur {addr}")

    dispatcher = asyncio.create_task(game_dispatcher())

    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            pass
        finally:
            dispatcher.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Arr\u00eat du serveur.")
