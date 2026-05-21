"""Huddle Session and WebRTC Peer Connection Manager for Backend Infrastructure."""

from __future__ import annotations

import logging

from aiortc import RTCPeerConnection
from fastapi import WebSocket

from src.app.websockets.media_processor import HuddleMediaProcessor
from src.app.websockets.schemas import SignalingPayload

logger = logging.getLogger(__name__)

class HuddleParticipant:
    def __init__(self, peer_id: str, websocket: WebSocket):
        self.peer_id = peer_id
        self.websocket = websocket
        self.pc = RTCPeerConnection()
        self.audio_processor: HuddleMediaProcessor | None = None

class HuddleSessionManager:
    def __init__(self):
        self.rooms: dict[str, dict[str, HuddleParticipant]] = {}

    async def register_peer(self, room_id: str, peer_id: str, websocket: WebSocket) -> HuddleParticipant:  # noqa: E501
        """Register a new peer in the session."""
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
            logger.info(f"Created new room: {room_id}")
        
        participant = HuddleParticipant(peer_id, websocket)
        self.rooms[room_id][peer_id] = participant


        @participant.pc.on("track")
        def on_track(track):
            if track.kind == "audio":
                logger.info(f"Received audio track from peer {peer_id} in room {room_id}")
                participant.audio_processor = HuddleMediaProcessor(track, room_id)
        
        logger.info(f"Registered new peer {peer_id} in room {room_id}")
        return participant


    async def handle_signaling(self, room_id: str, payload: SignalingPayload):
        """Handle the signaling payload."""
        room_peers = self.rooms.get(room_id, {})
        sender = room_peers.get(payload.sender_id)

        if not sender:
            logger.error(f"Sender {payload.sender_id} not found in room {room_id}")
            return
        
        if payload.target_id:
            target = room_peers.get(payload.target_id)
            if target:
                await target.websocket.send_text(payload.model_dump_json(by_alias=True))
            return
        
        for peer_id, participant in room_peers.items():
            if peer_id != payload.sender_id:
                await participant.websocket.send_text(payload.model_dump_json(by_alias=True))
        
    
    async def remove_peer(self, room_id: str, peer_id: str):
        """Remove a peer from the session."""
        if room_id in self.rooms and peer_id in self.rooms[room_id]:
            participant = self.rooms[room_id].pop(peer_id)

            if participant.audio_processor:
                participant.audio_processor.stop()
            
            await participant.pc.close()
            logger.info(f"Removed peer {peer_id} from room {room_id}")

            if not self.rooms[room_id]:
                self.rooms.pop(room_id)
                logger.info(f"Removed room {room_id} as it is empty")


huddle_session_manager = HuddleSessionManager()
