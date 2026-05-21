"""Backend WebRTC Audio Track Receiver for STT pipeline integration."""

from __future__ import annotations

import asyncio
import logging

from aiortc import MediaStreamTrack
from av.audio.frame import AudioFrame

from src.app.websockets.agent_orchestrator import HuddleAgentOrchestrator

logger = logging.getLogger(__name__)

class HuddleMediaProcessor(MediaStreamTrack):
    """Process audio frames from WebRTC media stream for Huddle STT."""

    kind = "audio"

    def __init__(self, track: MediaStreamTrack, room_id: str):
        super().__init__()
        self.track = track
        self.room_id = room_id
        self.audio_queue: asyncio.Queue[bytes] = asyncio.Queue()
        self.is_running = True
        self.processing_task = asyncio.create_task(self._stt_pipeline_loop())
        self.orchestrator = HuddleAgentOrchestrator(room_id=self.room_id)

    async def recv(self) -> AudioFrame:
        try:
            frame = await self.track.recv()

            for plane in frame.planes:
                chunk = plane.to_bytes()
                if chunk:
                    await self.audio_queue.put(chunk)
            
            return frame
        except Exception as e:
            logger.error(f"Error processing audio frame: {e}")
            self.stop()
            raise e

    async def _stt_pipeline_loop(self):
        buffer = bytearray()

        flush_size = 32000 * 2 * 3 # temporary set 16kHZ, 16bit, Mono standard based 32,000bytes per seconds with 3 seconds buffer unit  # noqa: E501

        logger.info(f"Starting STT pipeline loop with flush size: {flush_size}")

        while self.is_running:
            try:
                chunk = await self.audio_queue.get()
                buffer.extend(chunk)
                self.audio_queue.task_done()

                if len(buffer) >= flush_size:
                    audio_payload = bytes(buffer[:flush_size])
                    del buffer[:flush_size]

                    asyncio.create_task(self._execute_stt(audio_payload))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in STT pipeline loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _execute_stt(self, audio_data: bytes):
        logger.info("Captured %d bytes of audio chunk. Triggering STT inference...", len(audio_data))

        mocked_text = "스프린트 백엔드 API 명세서 작업이 계속 지연되고 있어서 프론트 개발이 막혔습니다."  # noqa: E501

        await self._forward_to_langgraph_agent(mocked_text)

    async def _forward_to_langgraph_agent(self, text: str):
        logger.info(f"Forwarding text to LangGraph agent: {text}")
        await self.orchestrator.trigger_agent(transcribed_text=text)
    
    def stop(self):
        if self.is_running:
            self.is_running = False
            self.processing_task.cancel()
            logger.info("STT pipeline loop stopped")

