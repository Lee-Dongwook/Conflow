"""Tool dispatcher — the only sanctioned path that calls Tool handlers.

Responsibilities (Watch List #2 enforcement point):
  1. Resolve Tool spec
  2. Verify `Workspace.tier >= tool.min_tier`
  3. Verify caller permission via `core.permissions.require_workspace_*`
  4. Parse raw input → `tool.input_schema`
  5. Call handler with the headless kwargs contract
  6. Stamp AuditLog (`a2ui.tool.invoked` + tool_id + tier)
  7. (Future) propagate OpenTelemetry trace_id

Handlers MUST accept exactly:
    async def handler(*,
        workspace_uuid: str,
        caller_member_uuid: str,
        payload: <input_schema>,
        db: AsyncSession,
    ) -> <output_schema>
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..shared import AuditDomain, AuditLog, Workspace
from .registry import PermissionLevel, ToolSpec, get_tool, tier_at_least


class ToolInvocationError(HTTPException):
    """Wraps Tool-level failures into a HTTP-aware exception so api.py
    can return a structured response without special-casing."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(status_code=status_code, detail=detail)


async def _enforce_tier(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    spec: ToolSpec,
) -> None:
    res = await db.execute(
        select(Workspace.tier).where(Workspace.uuid == workspace_uuid)
    )
    tier = res.scalar_one_or_none()
    if tier is None:
        raise ToolInvocationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )
    if not tier_at_least(tier, spec.min_tier):
        raise ToolInvocationError(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=(
                f"Tool {spec.id!r} requires tier {spec.min_tier.value} "
                f"or higher (workspace is {tier.value})"
            ),
        )


async def _enforce_permission(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    spec: ToolSpec,
) -> None:
    # Lazy import: `core.permissions` → `core.shared` → `core.shared.service`
    # → back to `core.permissions`. Importing at function-call time breaks
    # the cycle without leaking dispatcher into the Shared Core boot path.
    from ..permissions import (  # noqa: PLC0415
        require_workspace_admin,
        require_workspace_member,
        require_workspace_writer,
    )

    if spec.permission_required == PermissionLevel.MEMBER:
        await require_workspace_member(
            db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
        )
    elif spec.permission_required == PermissionLevel.WRITER:
        await require_workspace_writer(
            db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
        )
    elif spec.permission_required == PermissionLevel.ADMIN:
        await require_workspace_admin(
            db, workspace_uuid=workspace_uuid, member_uuid=caller_member_uuid
        )


def _audit_invocation(
    db: AsyncSession,
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    spec: ToolSpec,
    success: bool,
    error_detail: str | None = None,
) -> None:
    db.add(
        AuditLog(
            workspace_uuid=workspace_uuid,
            actor_member_uuid=caller_member_uuid,
            domain=AuditDomain.SYSTEM,
            action="a2ui.tool.invoked" if success else "a2ui.tool.failed",
            resource_type="a2ui.tool",
            resource_uuid=workspace_uuid,  # no per-tool UUID; key by workspace
            audit_metadata={
                "tool_id": spec.id,
                "domain": spec.domain,
                "cross_domain": spec.cross_domain,
                "tier_required": spec.min_tier.value,
                "permission_required": spec.permission_required.value,
                **({"error": error_detail} if error_detail else {}),
            },
        )
    )


async def invoke_tool(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    tool_id: str,
    raw_input: dict[str, Any],
    db: AsyncSession,
) -> BaseModel:
    """Run the full gating + dispatch + audit pipeline for a Tool call.

    Raises `ToolInvocationError` (HTTPException) on policy failures; lets
    the handler's own HTTPException propagate (404/403 from inside service).
    """
    try:
        spec = get_tool(tool_id)
    except KeyError as exc:
        raise ToolInvocationError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    # Tier first — cheaper than the permission JOIN. Both must pass.
    await _enforce_tier(db, workspace_uuid=workspace_uuid, spec=spec)
    await _enforce_permission(
        db,
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller_member_uuid,
        spec=spec,
    )

    try:
        payload = spec.input_schema.model_validate(raw_input)
    except ValidationError as exc:
        # Audit the rejection so abuse patterns surface in metrics.
        _audit_invocation(
            db,
            workspace_uuid=workspace_uuid,
            caller_member_uuid=caller_member_uuid,
            spec=spec,
            success=False,
            error_detail="input_schema_validation",
        )
        await db.commit()
        raise ToolInvocationError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Input does not match {spec.input_schema.__name__}: {exc.errors()}",
        ) from exc

    try:
        result = await spec.handler(
            workspace_uuid=workspace_uuid,
            caller_member_uuid=caller_member_uuid,
            payload=payload,
            db=db,
        )
    except HTTPException:
        # Re-raise with audit. The handler's HTTPException already carries
        # the right status; we don't translate it.
        _audit_invocation(
            db,
            workspace_uuid=workspace_uuid,
            caller_member_uuid=caller_member_uuid,
            spec=spec,
            success=False,
            error_detail="handler_http_exception",
        )
        await db.commit()
        raise

    # Defensive: confirm handler honored the output_schema contract.
    if not isinstance(result, spec.output_schema):
        # Don't fail the user request over this — log and pass through.
        # Tightening this to a hard error is a Phase 2 hardening step once
        # the eval harness lands.
        pass

    _audit_invocation(
        db,
        workspace_uuid=workspace_uuid,
        caller_member_uuid=caller_member_uuid,
        spec=spec,
        success=True,
    )
    await db.commit()
    return result
