"""Optional standalone signaling server (port 8765) for local testing without FastAPI."""

import asyncio
import os

import websockets
from websockets.asyncio.server import ServerConnection

from .hub import signaling_hub, send_websockets

STANDALONE_HOST = os.environ.get("SIGNALING_HOST", "127.0.0.1")
STANDALONE_PORT = int(os.environ.get("SIGNALING_PORT", "8765"))


async def signaling_handler(websocket: ServerConnection) -> None:
    """Relay JSON signaling frames for a room encoded in the request path."""
    room_id = websocket.request.path.strip("/") or "default"
    signaling_hub.join(room_id, websocket)
    try:
        async for message in websocket:
            await signaling_hub.relay(room_id, websocket, message, send_websockets)
    finally:
        signaling_hub.leave(room_id, websocket)


async def main() -> None:
    """Run the standalone signaling server until interrupted."""
    async with websockets.serve(signaling_handler, STANDALONE_HOST, STANDALONE_PORT):
        print(f"Standalone signaling on ws://{STANDALONE_HOST}:{STANDALONE_PORT}/<room_id>")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
