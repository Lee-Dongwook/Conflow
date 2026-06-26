"""A2UI cross-domain query Tool — first composition pattern.

The differentiation axis 2 (docs/00-vision/positioning.md) lives or dies
here: combining PM + Comms + HR + Documents reads behind a single
permission-safe Tool call.

Alpha policy:
  - Sub-tool selection is DETERMINISTIC (keyword-mapped intent → ordered
    sub-tool list). LLM-based planning lands once the Phase 2 eval
    harness is in place — until then, deterministic plans keep the
    behavior reproducible.
  - Sub-tools are invoked via the normal `invoke_tool` pipeline, so they
    inherit Tier + permission + audit. No backdoor.
  - Composition is JSON-shaped: each sub-tool's structured output is
    preserved verbatim + a short human-readable summary is rendered.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared import WorkspaceTier
from ..dispatcher import ToolInvocationError, invoke_tool
from ..registry import PermissionLevel, ToolSpec, register_tool

# Deterministic intent → (sub_tool_id, param_extractor_key) plan.
# Each step pulls its raw input from `params[<key>]`; missing keys fall
# back to {} (Tool's input_schema defaults).
_PLAN_BY_INTENT: dict[str, list[tuple[str, str]]] = {
    "blockers": [
        ("pm.identify_blockers", "blockers"),
    ],
    "blockers_with_one_on_one": [
        ("pm.identify_blockers", "blockers"),
        ("hr.list_one_on_ones", "one_on_ones"),
    ],
    "sprint_health": [
        ("pm.get_sprint_summary", "sprint_summary"),
        ("pm.identify_blockers", "blockers"),
    ],
    "pending_reviews": [
        ("documents.list_pending_review", "pending_reviews"),
    ],
    "team_pulse": [
        ("pm.identify_blockers", "blockers"),
        ("hr.list_one_on_ones", "one_on_ones"),
        ("documents.list_pending_review", "pending_reviews"),
    ],
}


class CrossDomainQueryInput(BaseModel):
    intent: str = Field(
        description=(
            "Known intent key — selects a deterministic sub-tool plan. "
            "Supported: blockers, blockers_with_one_on_one, sprint_health, "
            "pending_reviews, team_pulse."
        ),
    )
    params: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description=(
            "Per-sub-tool raw input keyed by the plan step name. "
            "E.g. {'sprint_summary': {'sprint_uuid': '...'}}."
        ),
    )


class CrossDomainTraceEntry(BaseModel):
    tool_id: str
    ok: bool
    status_code: int | None = None
    error: str | None = None
    snippet: dict[str, Any] | None = None


class CrossDomainQueryOutput(BaseModel):
    model_config = ConfigDict(from_attributes=False)

    intent: str
    summary: str
    tool_trace: list[CrossDomainTraceEntry]
    results: dict[str, dict[str, Any]]


def _render_summary(
    intent: str, results: dict[str, dict[str, Any]]
) -> str:
    """Plain-text summary for human readers. LLM-based summarization
    replaces this once the eval harness lands (Phase 2)."""
    parts = [f"intent={intent}"]
    if "blockers" in results:
        n = results["blockers"].get("total") or len(
            results["blockers"].get("issues") or []
        )
        parts.append(f"blockers: {n}")
    if "one_on_ones" in results:
        n = results["one_on_ones"].get("total") or len(
            results["one_on_ones"].get("one_on_ones") or []
        )
        parts.append(f"1:1 sessions (yours): {n}")
    if "sprint_summary" in results:
        s = results["sprint_summary"]
        parts.append(
            f"sprint '{s.get('name')}' phase={s.get('phase')} "
            f"blockers={s.get('blocker_count')}"
        )
    if "pending_reviews" in results:
        n = results["pending_reviews"].get("total") or len(
            results["pending_reviews"].get("instances") or []
        )
        parts.append(f"pending document reviews: {n}")
    return " | ".join(parts)


async def _a2ui_cross_domain_query(
    *,
    workspace_uuid: str,
    caller_member_uuid: str,
    payload: CrossDomainQueryInput,
    db: AsyncSession,
) -> CrossDomainQueryOutput:
    plan = _PLAN_BY_INTENT.get(payload.intent)
    if plan is None:
        from fastapi import HTTPException, status  # noqa: PLC0415

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unknown intent {payload.intent!r}. "
                f"Supported: {sorted(_PLAN_BY_INTENT.keys())}"
            ),
        )

    trace: list[CrossDomainTraceEntry] = []
    results: dict[str, dict[str, Any]] = {}

    for tool_id, plan_key in plan:
        raw_input = payload.params.get(plan_key, {})
        try:
            # Recursive invoke — sub-tool's tier + permission are checked
            # against the SAME caller, so escalation across domains is
            # impossible. Each sub-tool also stamps its own audit row.
            sub_result = await invoke_tool(
                workspace_uuid=workspace_uuid,
                caller_member_uuid=caller_member_uuid,
                tool_id=tool_id,
                raw_input=raw_input,
                db=db,
            )
            dumped = sub_result.model_dump(mode="json")
            results[plan_key] = dumped
            # snippet keeps top-level summary keys only — full dump is in
            # `results` so the trace stays light for chat surfaces.
            snippet = {
                k: v for k, v in dumped.items() if not isinstance(v, list)
            }
            trace.append(
                CrossDomainTraceEntry(
                    tool_id=tool_id,
                    ok=True,
                    snippet=snippet,
                )
            )
        except ToolInvocationError as exc:
            trace.append(
                CrossDomainTraceEntry(
                    tool_id=tool_id,
                    ok=False,
                    status_code=exc.status_code,
                    error=str(exc.detail),
                )
            )
            # Partial composition is OK — degrade gracefully instead of
            # failing the whole query.

    summary = _render_summary(payload.intent, results)
    return CrossDomainQueryOutput(
        intent=payload.intent,
        summary=summary,
        tool_trace=trace,
        results=results,
    )


register_tool(
    ToolSpec(
        id="a2ui.cross_domain_query",
        domain="a2ui",
        description=(
            "Deterministic cross-domain composition. Picks a known intent "
            "(blockers / blockers_with_one_on_one / sprint_health / "
            "pending_reviews / team_pulse), runs the planned sub-Tools in "
            "order under the caller's own permissions, and returns the "
            "composed result + a human-readable summary + per-step trace. "
            "LLM-based intent planning lands once the Phase 2 eval harness ships."
        ),
        handler=_a2ui_cross_domain_query,
        input_schema=CrossDomainQueryInput,
        output_schema=CrossDomainQueryOutput,
        min_tier=WorkspaceTier.BUSINESS,
        permission_required=PermissionLevel.MEMBER,
        cross_domain=True,
        phase=2,
        tags=("composition", "differentiation-axis-2"),
    )
)
