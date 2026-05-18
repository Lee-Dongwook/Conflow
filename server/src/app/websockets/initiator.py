"""WebRTC offerer CLI — connects to the signaling server and starts the call."""

import asyncio
import contextlib

from .peer import (
    SESSION_SECONDS,
    IceCandidateBuffer,
    SignalingClient,
    apply_answer,
    create_peer_connection,
    wire_local_ice,
)
from .schemas import AnswerMessage, IceMessage, OfferMessage


async def run_offer() -> None:
    """Create an offer and complete the handshake via WebSocket signaling."""
    client = SignalingClient()
    await client.connect()
    print(f"Signaling connected (room={client.room_id})")

    pc = create_peer_connection()
    ice_buffer = IceCandidateBuffer(pc)
    wire_local_ice(pc, client.send)

    channel = pc.createDataChannel("chat")
    answer_received = asyncio.Event()

    @channel.on("open")
    def on_open() -> None:
        print("Data channel open")
        channel.send("Hello from offerer")

    @channel.on("message")
    def on_message(message: str) -> None:
        print("Data channel message:", message)

    async def on_signaling(message: OfferMessage | AnswerMessage | IceMessage) -> None:
        if isinstance(message, AnswerMessage):
            await apply_answer(pc, ice_buffer, message)
            print("Answer applied")
            answer_received.set()
            return
        if isinstance(message, IceMessage):
            await ice_buffer.add(message)

    listen_task = asyncio.create_task(client.listen(on_signaling))

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    local = pc.localDescription
    if local is None:
        msg = "Local description missing after createOffer"
        raise RuntimeError(msg)
    await client.send(OfferMessage(sdp=local.sdp))
    print("Offer sent — waiting for answer…")

    try:
        await asyncio.wait_for(answer_received.wait(), timeout=SESSION_SECONDS)
        await asyncio.sleep(SESSION_SECONDS)
    finally:
        listen_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await listen_task
        await client.close()
        await pc.close()


if __name__ == "__main__":
    asyncio.run(run_offer())
