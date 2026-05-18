"""FastAPI WebSocket routes for WebRTC signaling."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .hub import signaling_hub, send_starlette

router = APIRouter(prefix="/ws", tags=["signaling"])


@router.websocket("/signal/{room_id}")
async def signal_room(websocket: WebSocket, room_id: str) -> None:
    """Relay JSON signaling frames between peers in the same room."""
    await websocket.accept()
    signaling_hub.join(room_id, websocket)
    try:
        while True:
            message = await websocket.receive_text()
            await signaling_hub.relay(room_id, websocket, message, send_starlette)
    except WebSocketDisconnect:
        pass
    finally:
        signaling_hub.leave(room_id, websocket)
