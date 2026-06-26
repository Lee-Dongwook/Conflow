"""Tool Registry — single source of truth for A2UI Tool metadata.

Tools register themselves at module import (see `core/a2ui/tools/`).
Tier gating + permission policy live HERE; never inlined into service
functions (Watch List #2 in docs/02-product/domain-overview.md).
"""

from __future__ import annotations

import enum
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..shared import WorkspaceTier


class PermissionLevel(enum.Enum):
    """Coarse permission required to invoke a Tool.

    Maps to `core.permissions.require_workspace_*`. Resource-scoped
    (external-collaborator / project-private) checks land alongside their
    domains; the dispatcher only handles workspace-scoped gating here.
    """

    MEMBER = "member"   # any workspace Member (incl. Guest)
    WRITER = "writer"   # Member / Admin / Owner (not Guest, not External)
    ADMIN = "admin"     # Admin / Owner only


# A Tool handler must accept these keyword-only args and return a Pydantic
# model. The dispatcher constructs `payload` from raw input, runs gating,
# and stamps audit.
ToolHandler = Callable[..., Awaitable[BaseModel]]


_TIER_ORDER: dict[WorkspaceTier, int] = {
    WorkspaceTier.FREE: 0,
    WorkspaceTier.TEAM: 1,
    WorkspaceTier.BUSINESS: 2,
    WorkspaceTier.ENTERPRISE: 3,
}


def tier_at_least(actual: WorkspaceTier, minimum: WorkspaceTier) -> bool:
    return _TIER_ORDER[actual] >= _TIER_ORDER[minimum]


@dataclass(frozen=True)
class ToolSpec:
    """Wire-level Tool definition. Immutable once registered."""

    id: str  # e.g. "pm.search_issues"
    domain: str  # "pm" / "comms" / "hr" / "documents" / "a2ui"
    description: str
    handler: ToolHandler
    input_schema: type[BaseModel]
    output_schema: type[BaseModel]
    min_tier: WorkspaceTier = WorkspaceTier.FREE
    permission_required: PermissionLevel = PermissionLevel.MEMBER
    cross_domain: bool = False
    phase: int = 1
    # Free-form tags (e.g. "a2ui-recommended", "kr-only"). Search-friendly.
    tags: tuple[str, ...] = field(default_factory=tuple)


_REGISTRY: dict[str, ToolSpec] = {}


def register_tool(spec: ToolSpec) -> ToolSpec:
    """Register a Tool. Raises if `spec.id` already exists — duplicates
    must be deliberate (call `clear_tools` first in tests)."""
    if spec.id in _REGISTRY:
        raise ValueError(f"Tool {spec.id!r} already registered")
    _REGISTRY[spec.id] = spec
    return spec


def get_tool(tool_id: str) -> ToolSpec:
    spec = _REGISTRY.get(tool_id)
    if spec is None:
        raise KeyError(f"Tool {tool_id!r} not registered")
    return spec


def list_tools(
    *,
    domain: str | None = None,
    max_tier: WorkspaceTier | None = None,
    max_phase: int | None = None,
    cross_domain_only: bool = False,
) -> list[ToolSpec]:
    """Filtered Tool catalog. `max_tier` returns Tools whose `min_tier`
    is at most `max_tier` (i.e. Tools the given Tier may call)."""
    out = list(_REGISTRY.values())
    if domain is not None:
        out = [t for t in out if t.domain == domain]
    if max_tier is not None:
        out = [t for t in out if tier_at_least(max_tier, t.min_tier)]
    if max_phase is not None:
        out = [t for t in out if t.phase <= max_phase]
    if cross_domain_only:
        out = [t for t in out if t.cross_domain]
    return sorted(out, key=lambda t: t.id)


def clear_tools() -> None:
    """For tests. Drops all registered Tools."""
    _REGISTRY.clear()


# Convenience for downstream type hints.
ToolInvokeKwargs = dict[str, Any]
__all_runtime__ = (AsyncSession,)  # keep import alive for type hints elsewhere
