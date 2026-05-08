"""Sample MCP server tools."""

from importlib import import_module
from typing import Any


def _resolve_fastmcp() -> Any:
    """Resolve FastMCP from available package paths."""
    try:
        return getattr(import_module("mcp.server.fastmcp"), "FastMCP")
    except ModuleNotFoundError:
        try:
            return getattr(import_module("fastmcp"), "FastMCP")
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "FastMCP is not installed. Install project dependencies in the "
                "Python >=3.13 environment defined by extension/mcp/pyproject.toml."
            ) from exc


FastMCP = _resolve_fastmcp()

mcp = FastMCP("Sample MCP")

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    return a - b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    return a * b
