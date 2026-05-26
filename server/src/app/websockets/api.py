"""FastAPI WebSocket routes for WebRTC signaling."""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from .hub import send_starlette, signaling_hub

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["signaling"])


async def _authenticate_ws(websocket: WebSocket) -> bool:
    """Validate the access token passed as a query parameter."""
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return False

    try:
        from src.app.core.database import get_async_db
        from src.app.core.verfiy_token import verify_token_from_db

        async for db in get_async_db():
            await verify_token_from_db(token, db)
            return True
    except Exception:
        logger.warning("WebSocket auth failed for token")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return False

    return False


@router.websocket("/signal/{room_id}")
async def signal_room(websocket: WebSocket, room_id: str) -> None:
    """Relay JSON signaling frames between peers in the same room."""
    if not await _authenticate_ws(websocket):
        return

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
