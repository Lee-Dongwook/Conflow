"""Huddle Agent Orchestrator for driving LangGraph asynchronously without blocking WebRTC."""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from langgraph.checkpoint.memory import MemorySaver

from src.app.agent.graphs.supervisor_graph import supervisor_agent_graph

logger = logging.getLogger(__name__)

class HuddleAgentOrchestrator:
    """Orchestrate Huddle agent workflows asynchronously."""

    def __init__(self, room_id: str):
        self.room_id = room_id
        self.graph = supervisor_agent_graph
        self.current_task: asyncio.Task | None = None

    async def trigger_agent(self, transcribed_text: str, current_state_context: dict[str, Any] | None = None):  # noqa: E501
        """Trigger the agent workflow with the transcribed text."""
        if self.current_task and not self.current_task.done():
            logger.warning("Agent workflow already running. Skipping new trigger.")
            self.current_task.cancel()
            try:
                await self.current_task
            except asyncio.CancelledError:
                pass
    
        self.current_task = asyncio.create_task(
            self._execute_graph_stream(transcribed_text, current_state_context)
        )
    
    async def _execute_graph_stream(self, text: str, context: dict[str, Any] | None = None):
        """Execute the graph stream with the transcribed text and current state context."""
        logger.info("Initializing LangGraph async runtime for Huddle Room: %s", self.room_id)
        initial_state = {
            "current_task": text,
            "team_context": f"Huddle Room: {self.room_id}",
            "chat_history": [],
        }

        if context:
            initial_state.update(context)
        
        config = {"configurable": {"thread_id": f"huddle_room_{self.room_id}"}}

        try:
            async for event in self.graph.astream(initial_state, config=config, stream_mode="updates"):  # noqa: E501
                for node_name, node_output in event.items():
                    logger.info("Node %s emitted event: %s", node_name, node_output)

                    await self._handle_node_update(node_name, node_output)
            
            final_state = await self.graph.aget_state(config)
            await self._process_final_agent_output(final_state.values)
        
        except asyncio.CancelledError:
            logger.warning("Agent workflow cancelled for Huddle Room: %s", self.room_id)

        except Exception as e:
            logger.error("Unhandled error in Agent workflow for Huddle Room: %s", e, exc_info=True)  # noqa: E501
    
    async def _handle_node_update(self, node_name: str, node_output: dict[str, Any]):
        """Handle the node update event."""
        logger.debug("Node %s emitted event: %s", node_name, node_output)

        if node_name == "finalize_meeting_summary":
            logger.info("Received final meeting summary from agent for Huddle Room: %s", self.room_id)  # noqa: E501
    
    async def _process_final_agent_output(self, final_values: dict[str, Any]):
        """Process the final agent output."""
        logger.info("Received final agent output for Huddle Room: %s", self.room_id)

        detected_blockers = final_values.get("detected_blockers")
        detected_insights = final_values.get("detected_insights")

        if detected_blockers:
            logger.info("Detected blockers: %s", detected_blockers)
        
        if detected_insights:
            logger.info("Detected insights: %s", detected_insights)

            
