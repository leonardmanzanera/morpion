"""Simple terminal client to connect to the network Tic-Tac-Toe server."""
from __future__ import annotations

import asyncio
import sys


async def user_input(loop: asyncio.AbstractEventLoop) -> str:
    return await loop.run_in_executor(None, sys.stdin.readline)


async def handle_server(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    loop = asyncio.get_event_loop()
    print("Connect\u00e9 au serveur. Tapez QUIT pour quitter.")
    try:
        while True:
            server_task = asyncio.create_task(reader.readline())
            input_task = asyncio.create_task(user_input(loop))

            done, pending = await asyncio.wait(
                {server_task, input_task}, return_when=asyncio.FIRST_COMPLETED
            )

            if server_task in done:
                data = server_task.result()
                if not data:
                    print("Serveur d\u00e9connect\u00e9.")
                    return
                message = data.decode().rstrip()
                print(message)

            if input_task in done:
                user_line = input_task.result()
                if not user_line:
                    writer.write(b"QUIT\n")
                    await writer.drain()
                    return
                writer.write(user_line.strip().encode() + b"\n")
                await writer.drain()

            for task in pending:
                task.cancel()
    finally:
        writer.close()
        await writer.wait_closed()


async def main(host: str = "127.0.0.1", port: int = 8000) -> None:
    reader, writer = await asyncio.open_connection(host, port)
    await handle_server(reader, writer)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Client terminal pour le morpion en ligne")
    parser.add_argument("--host", default="127.0.0.1", help="Adresse du serveur")
    parser.add_argument("--port", type=int, default=8000, help="Port du serveur")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        print("Arr\u00eat du client.")
