"""Slack Push Notification Node utilizing Model Context Protocol (MCP)."""

from __future__ import annotations

import logging
import os
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from src.app.agent.graphs.base_agent_state import AgentState

logger = logging.getLogger(__name__)

async def slack_mcp_notifier(state: AgentState) -> dict[str, Any]:
    """Slack push notification node utilizing Model Context Protocol (MCP)."""

    blockers = state.get("detected_blockers") or []
    error_state = state.get("error")

    if not blockers and not error_state:
        return {}
    
    slack_token = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    target_channel = os.environ.get("SLACK_ALERT_CHANNEL", "#general").strip()

    if not slack_token:
        logger.warning("SLACK_BOT_TOKEN is not set")
        return {}
    
    logger.info("Sending Slack notification to %s", target_channel)

    async with MultiServerMCPClient.from_command(
        ["npx", "-y", "@modelcontextprotocol/server-slack"],
        env={**os.environ, "SLACK_BOT_TOKEN": slack_token}
    ) as mcp_adapter:

        mcp_tools = await mcp_adapter.get_tools()

        post_message_tool = next(
            (tool for tool in mcp_tools if "post_message" in tool.name),
            None
        )

        if not post_message_tool:
            return {"error": "Slack MCP tool resolution failed"}
        
        slack_payload = "🚨 **Conflow Alert**\n\n"

        if error_state:
            slack_payload += f"Error: {error_state}\n\n"
        
        if blockers:
            slack_payload += "Detected Blockers:\n"
            for idx, blocker in enumerate(blockers, 1):
                title = blocker.get("title", f"Blocker {idx}")
                desc = blocker.get("description", "")
                owner = blocker.get("owner", "")
                slack_payload += f"- {title}\n  - Description: {desc}\n  - Owner: {owner}\n\n"
        
        logger.info("Slack payload: %s", slack_payload)

        try:
            await post_message_tool.ainvoke({
                "channel": target_channel,
                "text": slack_payload
            })
            logger.info("Slack notification sent successfully")
        except Exception as e:
            logger.error("Failed to send Slack notification: %s", e)
            return {"error": str(e)}

    return {"error", None}
