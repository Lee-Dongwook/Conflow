#!/usr/bin/env python3
"""End-to-end smoke: workspace → issue → transition → outbox/audit verify.

Walks the full Phase 0-1 alpha flow against a real PostgreSQL DB:
    1. ensure a test User exists (raw insert; bypass Supabase signup)
    2. create_workspace  → Workspace + 5 Role + creator Member + OWNER + AuditLog
    3. create_issue      → Issue + AuditLog + EventOutbox(pm.issue.created)
    4. transition BLOCKED → AuditLog + EventOutbox(pm.issue.blocked)
    5. count AuditLog + EventOutbox rows in this workspace and print a verdict

Usage:
    cd server
    uv run python scripts/smoke_e2e.py                  # use a fresh test user
    uv run python scripts/smoke_e2e.py --user-uuid <u>  # reuse an existing user
    uv run python scripts/smoke_e2e.py --cleanup        # delete the test rows on success

Requires the schema (alembic upgrade head) to already be applied.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import uuid as _uuid
from pathlib import Path

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))


def _ok(label: str, detail: str = "") -> None:
    print(f"  [ok]   {label}{(': ' + detail) if detail else ''}")


def _fail(label: str, detail: str) -> None:
    print(f"  [FAIL] {label}: {detail}")


async def _run(*, user_uuid_arg: str | None, cleanup: bool) -> int:
    from sqlalchemy import delete, func, select
    from src.app.comms.model import Channel, ChannelMember, Message
    from src.app.core import database as core_db
    from src.app.core.shared import (
        AuditLog,
        EventOutbox,
        Member,
        MemberInviteInput,
        MemberStatus,
        Role,
        RoleAssignment,
        RoleName,
        Workspace,
        WorkspaceCreateInput,
        accept_invitation,
        create_workspace,
        invite_member,
    )
    from src.app.core.shared_init import load_dotenv
    from src.app.pm.model import Issue
    from src.app.pm.schemas import (
        IssueCreateInput,
        IssuePriority,
        IssueStatus,
        IssueTransitionInput,
    )
    from src.app.pm.service import create_issue, transition_issue_status
    from src.app.user.model import User

    load_dotenv(os.environ.get("ENV", "local"))
    await core_db.initialize_postgres_db()
    if core_db.async_session is None:
        print("Error: async_session not initialized; check DB_* env vars.")
        return 2

    test_slug = f"smoke-{_uuid.uuid4().hex[:8]}"
    failures = 0

    async with core_db.async_session() as db:
        # ---------- 1. test User ----------
        print("[1] ensure test User")
        if user_uuid_arg:
            user = await db.get(User, user_uuid_arg)
            if user is None:
                print(f"  user_uuid {user_uuid_arg} not found")
                return 2
            _ok("existing user reused", user.uuid)
        else:
            user = User(
                name="smoke-e2e",
                email=f"smoke-{_uuid.uuid4().hex[:8]}@example.local",
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            _ok("fresh User created", user.uuid)

        # ---------- 2. create_workspace ----------
        print("[2] create_workspace + role/member seed")
        ws_out = await create_workspace(
            creator_user_uuid=user.uuid,
            payload=WorkspaceCreateInput(name="Smoke WS", slug=test_slug),
            db=db,
        )
        workspace_uuid = ws_out.uuid
        _ok("workspace created", f"{workspace_uuid} slug={test_slug}")

        role_count = await db.scalar(
            select(func.count()).select_from(Role).where(Role.workspace_uuid == workspace_uuid)
        )
        if role_count == 5:
            _ok("5 roles seeded")
        else:
            _fail("role seed", f"expected 5, got {role_count}")
            failures += 1

        member_res = await db.execute(
            select(Member).where(
                Member.workspace_uuid == workspace_uuid,
                Member.user_uuid == user.uuid,
            )
        )
        member = member_res.scalar_one_or_none()
        if member is None:
            _fail("creator Member", "row missing")
            failures += 1
            return failures or 1
        _ok("creator Member exists", member.uuid)

        assignment_res = await db.execute(
            select(RoleAssignment).where(
                RoleAssignment.workspace_uuid == workspace_uuid,
                RoleAssignment.member_uuid == member.uuid,
            )
        )
        assignments = list(assignment_res.scalars().all())
        if len(assignments) == 1:
            _ok("1 OWNER RoleAssignment")
        else:
            _fail("OWNER assignment", f"expected 1, got {len(assignments)}")
            failures += 1

        # ---------- 3. create_issue ----------
        print("[3] create_issue")
        issue_out = await create_issue(
            workspace_uuid=workspace_uuid,
            caller_member_uuid=member.uuid,
            payload=IssueCreateInput(
                title="smoke test issue",
                description="created by smoke_e2e",
                priority=IssuePriority.HIGH,
                assignee_member_uuid=member.uuid,
            ),
            db=db,
        )
        issue_uuid = issue_out.uuid
        _ok("issue created", issue_uuid)

        # ---------- 4. transition to BLOCKED ----------
        print("[4] transition BACKLOG → BLOCKED (via TODO)")
        # need to walk the state machine: backlog → todo → blocked
        await transition_issue_status(
            workspace_uuid=workspace_uuid,
            caller_member_uuid=member.uuid,
            issue_uuid=issue_uuid,
            payload=IssueTransitionInput(new_status=IssueStatus.TODO),
            db=db,
        )
        blocked_out = await transition_issue_status(
            workspace_uuid=workspace_uuid,
            caller_member_uuid=member.uuid,
            issue_uuid=issue_uuid,
            payload=IssueTransitionInput(
                new_status=IssueStatus.BLOCKED,
                blocked_reason="awaiting design review",
            ),
            db=db,
        )
        if blocked_out.status == IssueStatus.BLOCKED and blocked_out.blocked_reason:
            _ok(
                "issue is BLOCKED with reason",
                f"reason='{blocked_out.blocked_reason}'",
            )
        else:
            _fail("transition", f"status={blocked_out.status} reason={blocked_out.blocked_reason}")
            failures += 1

        # ---------- 5. verify AuditLog + EventOutbox ----------
        print("[5] AuditLog + EventOutbox counts")
        audit_total = await db.scalar(
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.workspace_uuid == workspace_uuid)
        )
        # expected actions: workspace.created, pm.issue.created,
        # pm.issue.transitioned (backlog→todo), pm.issue.blocked = 4
        if audit_total is not None and audit_total >= 4:
            _ok("AuditLog rows", f"{audit_total} (expected ≥4)")
        else:
            _fail("AuditLog rows", f"got {audit_total}, expected ≥4")
            failures += 1

        outbox_res = await db.execute(
            select(EventOutbox.event_name, EventOutbox.published_at)
            .where(EventOutbox.workspace_uuid == workspace_uuid)
            .order_by(EventOutbox.occurred_at)
        )
        outbox_rows = list(outbox_res.all())
        names = [r.event_name for r in outbox_rows]
        if "pm.issue.created" in names and "pm.issue.blocked" in names:
            _ok("outbox events emitted", str(names))
        else:
            _fail("outbox events", f"expected pm.issue.created + pm.issue.blocked, got {names}")
            failures += 1

        unpublished = [r for r in outbox_rows if r.published_at is None]
        if len(unpublished) == len(outbox_rows):
            _ok(
                "all outbox rows unpublished",
                f"{len(unpublished)}/{len(outbox_rows)} (worker will pick up)",
            )
        else:
            _ok(
                "some outbox rows already published",
                f"{len(outbox_rows) - len(unpublished)}/{len(outbox_rows)} "
                "(worker is running — fine)",
            )

        # ---------- 5c. cross-tenant isolation probe ----------
        # Creates a second workspace + new user/member, then tries to read
        # rows from the first workspace using the second workspace's RLS
        # context. When RLS is enabled, all such reads MUST return 0 rows.
        # (Without RLS this still passes because the application filter is
        # equally tight — the test just becomes a sanity check.)
        print("[5c] cross-tenant isolation probe")
        from src.app.core.db_context import set_workspace_context as _set_ctx

        probe_email = f"probe-{_uuid.uuid4().hex[:8]}@example.local"
        probe_user = User(name="smoke-probe", email=probe_email)
        db.add(probe_user)
        await db.commit()
        await db.refresh(probe_user)
        probe_ws = await create_workspace(
            creator_user_uuid=probe_user.uuid,
            payload=WorkspaceCreateInput(
                name="Probe WS",
                slug=f"probe-{_uuid.uuid4().hex[:8]}",
            ),
            db=db,
        )

        # Now set RLS context to probe workspace and try to count rows
        # belonging to the first workspace. Expectation: 0 (RLS) OR
        # the application filter still works (no RLS, no leak).
        await _set_ctx(db, workspace_uuid=probe_ws.uuid)
        leaked_issues = await db.scalar(
            select(func.count())
            .select_from(Issue)
            .where(Issue.workspace_uuid == workspace_uuid)
        )
        if leaked_issues == 0:
            _ok("cross-tenant Issue probe", "0 leaked rows")
        else:
            _fail(
                "cross-tenant leak",
                f"{leaked_issues} Issue rows visible from probe workspace "
                "— RLS not enforced (apply manual_sql/rls_policies.sql)",
            )
            failures += 1
        # Restore original workspace context for the rest of the script.
        await _set_ctx(
            db, workspace_uuid=workspace_uuid, member_uuid=member.uuid
        )

        # ---------- 5b. invite + accept ----------
        print("[5b] invite_member + accept_invitation")
        invitee_email = f"invitee-{_uuid.uuid4().hex[:8]}@example.local"
        invite_out = await invite_member(
            workspace_uuid=workspace_uuid,
            caller_member_uuid=member.uuid,
            payload=MemberInviteInput(
                email=invitee_email,
                role_name=RoleName.MEMBER,
            ),
            db=db,
        )
        invited_uuid = invite_out.member_uuid
        _ok("invited", f"{invitee_email} → member_uuid={invited_uuid}")

        invitee_user = User(name="smoke-invitee", email=invitee_email)
        db.add(invitee_user)
        await db.commit()
        await db.refresh(invitee_user)
        _ok("invitee User created", invitee_user.uuid)

        joined = await accept_invitation(
            workspace_uuid=workspace_uuid,
            invited_member_uuid=invited_uuid,
            caller_user_uuid=invitee_user.uuid,
            db=db,
        )
        if joined.status == MemberStatus.ACTIVE and joined.user_uuid == invitee_user.uuid:
            _ok("accepted (status=ACTIVE, user_uuid bound)")
        else:
            _fail(
                "accept_invitation",
                f"status={joined.status} user_uuid={joined.user_uuid}",
            )
            failures += 1

        # Extra event check: two new outbox events (invited, joined)
        invite_event_res = await db.execute(
            select(EventOutbox.event_name)
            .where(
                EventOutbox.workspace_uuid == workspace_uuid,
                EventOutbox.event_name.in_(
                    ("workspace.member.invited", "workspace.member.joined")
                ),
            )
            .order_by(EventOutbox.occurred_at)
        )
        invite_events = [r[0] for r in invite_event_res.all()]
        if (
            "workspace.member.invited" in invite_events
            and "workspace.member.joined" in invite_events
        ):
            _ok("invite/joined outbox events emitted", str(invite_events))
        else:
            _fail("invite events", f"got {invite_events}")
            failures += 1

        # ---------- 5d. A2UI Tool invoke ----------
        # Side-effect import: Tool registry must be populated before invoke.
        # (lifespan does this; the standalone smoke script needs it too.)
        print("[5d] A2UI invoke")
        import src.app.core.a2ui.tools  # noqa: F401
        from src.app.core.a2ui import ToolInvocationError, invoke_tool

        search_result = await invoke_tool(
            workspace_uuid=workspace_uuid,
            caller_member_uuid=member.uuid,
            tool_id="pm.search_issues",
            raw_input={"limit": 50},
            db=db,
        )
        issue_uuids = [i.uuid for i in search_result.issues]
        if issue_uuid in issue_uuids:
            _ok("pm.search_issues returned our issue", f"total={search_result.total}")
        else:
            _fail(
                "pm.search_issues",
                f"our issue {issue_uuid} missing from {issue_uuids}",
            )
            failures += 1

        # Tier gate: workspace is FREE, pm.create_issue requires TEAM → 402.
        try:
            await invoke_tool(
                workspace_uuid=workspace_uuid,
                caller_member_uuid=member.uuid,
                tool_id="pm.create_issue",
                raw_input={"title": "should be blocked"},
                db=db,
            )
            _fail("tier gate", "expected 402, request succeeded")
            failures += 1
        except ToolInvocationError as exc:
            if exc.status_code == 402:
                _ok("tier gate blocked Free→Team Tool", "402 Payment Required")
            else:
                _fail("tier gate", f"expected 402, got {exc.status_code}: {exc.detail}")
                failures += 1

        # AuditLog: one success + one failure → both `a2ui.tool.*` actions.
        a2ui_audit_res = await db.execute(
            select(AuditLog.action)
            .where(
                AuditLog.workspace_uuid == workspace_uuid,
                AuditLog.resource_type == "a2ui.tool",
            )
            .order_by(AuditLog.occurred_at)
        )
        a2ui_actions = [r[0] for r in a2ui_audit_res.all()]
        if (
            "a2ui.tool.invoked" in a2ui_actions
            and "a2ui.tool.failed" in a2ui_actions
        ):
            _ok("A2UI audit rows", str(a2ui_actions))
        else:
            _fail(
                "A2UI audit",
                f"expected both invoked + failed, got {a2ui_actions}",
            )
            failures += 1

        # ---------- 6. cleanup ----------
        if cleanup and failures == 0:
            print("[6] cleanup")
            await db.execute(
                delete(Message).where(Message.workspace_uuid == workspace_uuid)
            )
            await db.execute(
                delete(ChannelMember).where(ChannelMember.workspace_uuid == workspace_uuid)
            )
            await db.execute(
                delete(Channel).where(Channel.workspace_uuid == workspace_uuid)
            )
            await db.execute(delete(Issue).where(Issue.workspace_uuid == workspace_uuid))
            await db.execute(
                delete(EventOutbox).where(EventOutbox.workspace_uuid == workspace_uuid)
            )
            await db.execute(
                delete(AuditLog).where(AuditLog.workspace_uuid == workspace_uuid)
            )
            await db.execute(
                delete(RoleAssignment).where(
                    RoleAssignment.workspace_uuid == workspace_uuid
                )
            )
            await db.execute(delete(Role).where(Role.workspace_uuid == workspace_uuid))
            await db.execute(delete(Member).where(Member.workspace_uuid == workspace_uuid))
            await db.execute(delete(Workspace).where(Workspace.uuid == workspace_uuid))
            if not user_uuid_arg:
                await db.execute(delete(User).where(User.uuid == user.uuid))
            # Invitee + probe Users are always cleaned up (created by this run).
            await db.execute(delete(User).where(User.uuid == invitee_user.uuid))
            # Probe workspace and its members/roles/audit must be cleaned too.
            await db.execute(
                delete(RoleAssignment).where(
                    RoleAssignment.workspace_uuid == probe_ws.uuid
                )
            )
            await db.execute(delete(Role).where(Role.workspace_uuid == probe_ws.uuid))
            await db.execute(
                delete(AuditLog).where(AuditLog.workspace_uuid == probe_ws.uuid)
            )
            await db.execute(
                delete(EventOutbox).where(EventOutbox.workspace_uuid == probe_ws.uuid)
            )
            await db.execute(
                delete(Member).where(Member.workspace_uuid == probe_ws.uuid)
            )
            await db.execute(delete(Workspace).where(Workspace.uuid == probe_ws.uuid))
            await db.execute(delete(User).where(User.uuid == probe_user.uuid))
            await db.commit()
            _ok("cleanup complete")
        elif cleanup and failures > 0:
            print("[6] cleanup skipped (failures present — rows kept for debugging)")
        else:
            print(
                f"[6] cleanup skipped (default). workspace_uuid={workspace_uuid} "
                "kept for inspection."
            )

    print()
    if failures == 0:
        print("RESULT: PASS")
        return 0
    print(f"RESULT: FAIL ({failures} check(s) failed)")
    return 1


def main() -> None:
    parser = argparse.ArgumentParser(description="End-to-end smoke for workspace+pm+outbox.")
    parser.add_argument(
        "--user-uuid",
        default=None,
        help="Reuse an existing users.uuid (else a fresh User row is inserted)",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Delete all rows created by this run on success (User kept if reused)",
    )
    args = parser.parse_args()

    code = asyncio.run(
        _run(user_uuid_arg=args.user_uuid, cleanup=args.cleanup)
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
