from typing import Any, Protocol

from langchain_core.runnables import RunnableConfig


class McpAuthProtocol(Protocol):
    async def get_headers(
        self,
        mcp_config: dict[str, Any],
        state: dict[str, Any],
        config: RunnableConfig,
        resolve_template_function: Any,
        agent_model: Any | None = None
    ) -> dict[str, str]: ...

    async def referesh_if_needed(
        self,
        error: Exception,
        mcp_config: dict[str, Any],
        state: dict[str, Any],
        agent_model: Any,
        config: RunnableConfig,
        resolve_template_function: Any,
        endpoint_url: str | None = None,
    ) -> bool: ...
