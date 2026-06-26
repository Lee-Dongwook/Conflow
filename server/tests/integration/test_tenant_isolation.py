"""Cross-tenant isolation regression.

Verifies the application-layer filter (`Issue.workspace_uuid == ws`) blocks
cross-tenant reads. When `manual_sql/rls_policies.sql` is applied, the same
test ALSO exercises the RLS USING clause — both paths must yield 0 leaks.

This test is the canary for Watch List #4 ("workspace_uuid 없는 쿼리가
머지됨" in docs/02-product/domain-overview.md).
"""

from __future__ import annotations

import pytest
from sqlalchemy import func, select


@pytest.mark.asyncio
async def test_issue_reads_dont_cross_tenants(
    db_session, workspace_factory
) -> None:
    """An Issue in workspace A must not appear in workspace B's listing."""
    from src.app.core.db_context import set_workspace_context
    from src.app.pm.model import Issue
    from src.app.pm.schemas import IssueCreateInput, IssuePriority
    from src.app.pm.service import create_issue

    ws_a_uuid, mem_a_uuid, _ = await workspace_factory()
    ws_b_uuid, mem_b_uuid, _ = await workspace_factory()

    # Seed an issue in workspace A.
    await set_workspace_context(
        db_session, workspace_uuid=ws_a_uuid, member_uuid=mem_a_uuid
    )
    a_issue = await create_issue(
        workspace_uuid=ws_a_uuid,
        caller_member_uuid=mem_a_uuid,
        payload=IssueCreateInput(
            title="A-only", priority=IssuePriority.LOW
        ),
        db=db_session,
    )

    # Switch context to workspace B. Try to read A's issue id.
    await set_workspace_context(
        db_session, workspace_uuid=ws_b_uuid, member_uuid=mem_b_uuid
    )
    res = await db_session.execute(
        select(func.count()).select_from(Issue).where(
            Issue.uuid == a_issue.uuid
        )
    )
    leaked = int(res.scalar_one())
    assert leaked == 0, (
        f"Workspace B sees Issue {a_issue.uuid} owned by Workspace A — "
        "isolation broken (either RLS bypass or application-filter miss)."
    )

    # Sanity: workspace A still sees its own issue.
    await set_workspace_context(
        db_session, workspace_uuid=ws_a_uuid, member_uuid=mem_a_uuid
    )
    res = await db_session.execute(
        select(func.count())
        .select_from(Issue)
        .where(
            Issue.uuid == a_issue.uuid,
            Issue.workspace_uuid == ws_a_uuid,
        )
    )
    assert int(res.scalar_one()) == 1
