"""WebRTC answerer CLI — waits for an offer on the signaling server."""

import asyncio
import contextlib

from .peer import (
    SESSION_SECONDS,
    IceCandidateBuffer,
    SignalingClient,
    apply_offer,
    create_peer_connection,
    wire_local_ice,
)
from .schemas import AnswerMessage, IceMessage, OfferMessage


async def run_answer() -> None:
    """Wait for an offer and reply with an answer via WebSocket signaling."""
    client = SignalingClient()
    await client.connect()
    print(f"Signaling connected (room={client.room_id}), waiting for offer…")

    pc = create_peer_connection()
    ice_buffer = IceCandidateBuffer(pc)
    wire_local_ice(pc, client.send)
    handshake_done = asyncio.Event()

    @pc.on("datachannel")
    def on_datachannel(channel) -> None:
        @channel.on("message")
        def on_message(message: str) -> None:
            print("Data channel message:", message)
            channel.send("Hello from answerer")

    async def on_signaling(message: OfferMessage | AnswerMessage | IceMessage) -> None:
        if isinstance(message, OfferMessage):
            await apply_offer(pc, ice_buffer, client, message)
            print("Offer applied, answer sent")
            handshake_done.set()
            return
        if isinstance(message, IceMessage):
            await ice_buffer.add(message)

    listen_task = asyncio.create_task(client.listen(on_signaling))

    try:
        await asyncio.wait_for(handshake_done.wait(), timeout=SESSION_SECONDS)
        await asyncio.sleep(SESSION_SECONDS)
    finally:
        listen_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await listen_task
        await client.close()
        await pc.close()


if __name__ == "__main__":
    asyncio.run(run_answer())
