"""In-memory room registry for WebRTC signaling relay."""

from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import TypeVar

from starlette.websockets import WebSocket
from websockets.asyncio.server import ServerConnection

TConnection = TypeVar("TConnection", WebSocket, ServerConnection)


class SignalingHub:
    """Relay signaling messages to every other peer in the same room."""

    def __init__(self) -> None:
        self._rooms: dict[str, set[object]] = defaultdict(set)

    def join(self, room_id: str, connection: object) -> None:
        """Register a connection in a room."""
        self._rooms[room_id].add(connection)

    def leave(self, room_id: str, connection: object) -> None:
        """Remove a connection and drop empty rooms."""
        peers = self._rooms.get(room_id)
        if peers is None:
            return
        peers.discard(connection)
        if not peers:
            self._rooms.pop(room_id, None)

    async def relay(
        self,
        room_id: str,
        sender: object,
        message: str,
        send: Callable[[object, str], Awaitable[None]],
    ) -> None:
        """Send a message to all peers in the room except the sender."""
        peers = list(self._rooms.get(room_id, ()))
        targets = [peer for peer in peers if peer is not sender]
        if not targets:
            return
        await _broadcast(send, targets, message)


async def _broadcast(
    send: Callable[[object, str], Awaitable[None]],
    targets: list[object],
    message: str,
) -> None:
    import asyncio

    await asyncio.gather(
        *[send(peer, message) for peer in targets],
        return_exceptions=True,
    )


async def send_starlette(peer: object, message: str) -> None:
    """Send text to a FastAPI/Starlette WebSocket peer."""
    assert isinstance(peer, WebSocket)
    await peer.send_text(message)


async def send_websockets(peer: object, message: str) -> None:
    """Send text to a ``websockets`` server connection peer."""
    assert isinstance(peer, ServerConnection)
    await peer.send(message)


signaling_hub = SignalingHub()
