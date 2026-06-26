"""A2UI (AI-to-UI) Tool Registry — differentiation axis 2.

Per docs/04-architecture/a2ui-strategy.md: every domain's headless service
function can be lifted into a Tool with `register_tool(...)`. The Tool
Registry is the single place Tier gating and permission policy is enforced
(Watch List #2 — inlining a tier check in service code breaks the promise).

Public surface:
    register_tool / get_tool / list_tools     — registry.py
    invoke_tool                                — dispatcher.py
"""

from .dispatcher import ToolInvocationError, invoke_tool
from .registry import (
    PermissionLevel,
    ToolSpec,
    clear_tools,
    get_tool,
    list_tools,
    register_tool,
)

__all__ = [
    "PermissionLevel",
    "ToolInvocationError",
    "ToolSpec",
    "clear_tools",
    "get_tool",
    "invoke_tool",
    "list_tools",
    "register_tool",
]
