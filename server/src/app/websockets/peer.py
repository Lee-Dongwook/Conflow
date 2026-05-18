"""Shared WebRTC peer helpers for CLI signaling clients."""

import asyncio
import os
from collections.abc import Awaitable, Callable

import websockets
from aiortc import (
    RTCConfiguration,
    RTCIceCandidate,
    RTCIceServer,
    RTCPeerConnection,
    RTCSessionDescription,
)
from websockets.asyncio.client import ClientConnection

from .schemas import (
    AnswerMessage,
    IceMessage,
    OfferMessage,
    SignalingMessage,
    parse_signaling_message,
)

DEFAULT_SIGNALING_WS_URL = "ws://127.0.0.1:8000/ws/signal"
DEFAULT_ROOM_ID = "test-room"
DEFAULT_STUN_URL = "stun:stun.l.google.com:19302"
SESSION_SECONDS = 30


def signaling_ws_url() -> str:
    """Base WebSocket URL for signaling (without room suffix)."""
    return os.environ.get("SIGNALING_WS_URL", DEFAULT_SIGNALING_WS_URL).rstrip("/")


def signaling_room_id() -> str:
    """Room id shared by initiator and receiver CLI scripts."""
    return os.environ.get("SIGNALING_ROOM_ID", DEFAULT_ROOM_ID)


def create_peer_connection() -> RTCPeerConnection:
    """Build an ``RTCPeerConnection`` with a public STUN server."""
    return RTCPeerConnection(
        configuration=RTCConfiguration(iceServers=[RTCIceServer(urls=[DEFAULT_STUN_URL])]),
    )


class IceCandidateBuffer:
    """Queue ICE candidates until the remote SDP is applied."""

    def __init__(self, pc: RTCPeerConnection) -> None:
        self._pc = pc
        self._remote_ready = False
        self._pending: list[IceMessage] = []

    def mark_remote_ready(self) -> None:
        """Allow queued and future ICE candidates to be applied."""
        self._remote_ready = True

    async def add(self, message: IceMessage) -> None:
        """Apply or queue an ICE candidate from the signaling channel."""
        if self._remote_ready:
            await self._pc.addIceCandidate(_to_rtc_ice(message))
            return
        self._pending.append(message)

    async def flush(self) -> None:
        """Apply all candidates that arrived before remote SDP."""
        for message in self._pending:
            await self._pc.addIceCandidate(_to_rtc_ice(message))
        self._pending.clear()


def _to_rtc_ice(message: IceMessage) -> RTCIceCandidate:
    return RTCIceCandidate(
        candidate=message.candidate,
        sdpMid=message.sdp_mid,
        sdpMLineIndex=message.sdp_mline_index,
    )


def wire_local_ice(
    pc: RTCPeerConnection,
    send_json: Callable[[SignalingMessage], Awaitable[None]],
) -> None:
    """Emit local trickle ICE candidates onto the signaling channel."""

    @pc.on("icecandidate")
    def on_icecandidate(candidate: RTCIceCandidate | None) -> None:
        if candidate is None or candidate.candidate is None:
            return
        loop = asyncio.get_running_loop()
        loop.create_task(
            send_json(
                IceMessage(
                    candidate=candidate.candidate,
                    sdp_mid=candidate.sdpMid,
                    sdp_mline_index=candidate.sdpMLineIndex,
                ),
            ),
        )


class SignalingClient:
    """WebSocket client for a single signaling room."""

    def __init__(self, room_id: str | None = None) -> None:
        self._room_id = room_id or signaling_room_id()
        self._url = f"{signaling_ws_url()}/{self._room_id}"
        self._ws: ClientConnection | None = None

    @property
    def room_id(self) -> str:
        return self._room_id

    async def connect(self) -> None:
        """Open the signaling WebSocket."""
        self._ws = await websockets.connect(self._url)

    async def close(self) -> None:
        """Close the signaling WebSocket."""
        if self._ws is not None:
            await self._ws.close()
            self._ws = None

    async def send(self, message: SignalingMessage) -> None:
        """Send a validated signaling message."""
        if self._ws is None:
            msg = "SignalingClient is not connected"
            raise RuntimeError(msg)
        await self._ws.send(message.model_dump_json(by_alias=True))

    async def listen(
        self,
        handler: Callable[[OfferMessage | AnswerMessage | IceMessage], Awaitable[None]],
    ) -> None:
        """Dispatch signaling messages until the socket closes."""
        if self._ws is None:
            msg = "SignalingClient is not connected"
            raise RuntimeError(msg)
        async for raw in self._ws:
            if isinstance(raw, bytes):
                raw = raw.decode()
            await handler(parse_signaling_message(raw))


async def apply_answer(pc: RTCPeerConnection, ice_buffer: IceCandidateBuffer, message: AnswerMessage) -> None:
    """Set remote answer SDP and drain queued ICE."""
    await pc.setRemoteDescription(RTCSessionDescription(sdp=message.sdp, type="answer"))
    ice_buffer.mark_remote_ready()
    await ice_buffer.flush()


async def apply_offer(
    pc: RTCPeerConnection,
    ice_buffer: IceCandidateBuffer,
    client: SignalingClient,
    message: OfferMessage,
) -> None:
    """Set remote offer SDP, create an answer, and publish it."""
    await pc.setRemoteDescription(RTCSessionDescription(sdp=message.sdp, type="offer"))
    ice_buffer.mark_remote_ready()
    await ice_buffer.flush()
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    local = pc.localDescription
    if local is None:
        msg = "Local description missing after createAnswer"
        raise RuntimeError(msg)
    await client.send(AnswerMessage(sdp=local.sdp))
