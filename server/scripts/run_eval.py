#!/usr/bin/env python3
"""A2UI Tool regression runner — deterministic shape assertions.

Reads `tests/eval/cases.json`, seeds a throwaway Free-tier workspace, runs
every case through `invoke_tool`, and asserts on the response shape (or
error status). No LLM calls; runs entirely in mock mode.

Usage:
    cd server
    uv run python scripts/run_eval.py                # run all cases
    uv run python scripts/run_eval.py --case pm.*    # filter by glob
    uv run python scripts/run_eval.py --keep         # don't drop the workspace

Exit codes:
    0  all pass
    1  one or more fail
    2  setup error (DB not reachable, schema missing, etc.)
"""

from __future__ import annotations

import argparse
import asyncio
import fnmatch
import json
import os
import sys
import uuid as _uuid
from pathlib import Path
from typing import Any

SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

CASES_PATH = SERVER_ROOT / "tests" / "eval" / "cases.json"


def _load_cases(filter_glob: str | None) -> list[dict[str, Any]]:
    if not CASES_PATH.is_file():
        print(f"Error: {CASES_PATH} not found.")
        sys.exit(2)
    raw = json.loads(CASES_PATH.read_text())
    cases = raw.get("cases", [])
    if filter_glob:
        cases = [c for c in cases if fnmatch.fnmatch(c["id"], filter_glob)]
    return cases


def _check_expectation(
    result: Any | None,
    error_status_code: int | None,
    error_detail: str | None,
    expect: dict[str, Any],
) -> tuple[bool, str]:
    expected_status = expect.get("status", "ok")
    if expected_status == "error":
        if error_status_code is None:
            return False, "expected error, got success"
        wanted_code = expect.get("status_code")
        if wanted_code is not None and error_status_code != wanted_code:
            return False, f"status_code {error_status_code} != expected {wanted_code}"
        detail_contains = expect.get("detail_contains")
        if detail_contains and (
            error_detail is None
            or detail_contains.lower() not in error_detail.lower()
        ):
            return False, f"detail {error_detail!r} missing {detail_contains!r}"
        return True, "error matched"

    if error_status_code is not None:
        return False, f"expected success, got error {error_status_code}: {error_detail}"

    if not isinstance(result, dict):
        return False, f"result is not a dict (got {type(result).__name__})"

    for key in expect.get("keys", []):
        if key not in result:
            return False, f"missing key {key!r}"
    for key, value in (expect.get("equals") or {}).items():
        if result.get(key) != value:
            return False, f"{key}={result.get(key)!r} != expected {value!r}"
    for key in expect.get("truthy", []):
        if not result.get(key):
            return False, f"{key} not truthy"
    return True, "ok"


async def _run(*, filter_glob: str | None, keep: bool) -> int:
    import src.app.core.a2ui.tools  # noqa: F401  side-effect Tool registration
    from sqlalchemy import delete
    from src.app.core import database as core_db
    from src.app.core.a2ui import ToolInvocationError, invoke_tool
    from src.app.core.shared import (
        AuditLog,
        EventOutbox,
        Member,
        Role,
        RoleAssignment,
        Workspace,
        WorkspaceCreateInput,
        create_workspace,
    )
    from src.app.core.shared_init import load_dotenv
    from src.app.user.model import User

    load_dotenv(os.environ.get("ENV", "local"))
    await core_db.initialize_postgres_db()
    if core_db.async_session is None:
        print("Error: async_session not initialized.")
        return 2

    cases = _load_cases(filter_glob)
    if not cases:
        print("No cases matched filter.")
        return 0

    workspace_uuid: str | None = None
    user_uuid: str | None = None
    failures = 0

    async with core_db.async_session() as db:
        try:
            user = User(
                name="eval-runner",
                email=f"eval-{_uuid.uuid4().hex[:8]}@example.local",
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            user_uuid = user.uuid

            ws = await create_workspace(
                creator_user_uuid=user.uuid,
                payload=WorkspaceCreateInput(
                    name="Eval WS",
                    slug=f"eval-{_uuid.uuid4().hex[:8]}",
                ),
                db=db,
            )
            workspace_uuid = ws.uuid

            mem_res = await db.execute(
                Member.__table__.select().where(
                    (Member.workspace_uuid == workspace_uuid)
                    & (Member.user_uuid == user.uuid)
                )
            )
            mem_row = mem_res.fetchone()
            if mem_row is None:
                print("Error: creator member not seeded.")
                return 2
            caller_member_uuid = mem_row.uuid

            print(f"setup: workspace={workspace_uuid} member={caller_member_uuid}")
            print(f"running {len(cases)} case(s)\n")

            for case in cases:
                case_id = case["id"]
                tool_id = case["tool_id"]
                raw_input = case.get("raw_input", {})
                expect = case["expect"]

                error_status_code: int | None = None
                error_detail: str | None = None
                dumped: dict[str, Any] | None = None
                try:
                    result = await invoke_tool(
                        workspace_uuid=workspace_uuid,
                        caller_member_uuid=caller_member_uuid,
                        tool_id=tool_id,
                        raw_input=raw_input,
                        db=db,
                    )
                    dumped = result.model_dump(mode="json")
                except ToolInvocationError as exc:
                    error_status_code = exc.status_code
                    error_detail = str(exc.detail)

                ok, detail = _check_expectation(
                    dumped, error_status_code, error_detail, expect
                )
                marker = "[ok]  " if ok else "[FAIL]"
                print(f"  {marker} {case_id:50s} {detail}")
                if not ok:
                    failures += 1

        finally:
            if not keep and workspace_uuid is not None:
                # Drop the eval workspace + its rows. RLS context still
                # set, so cleanup is workspace-scoped.
                await db.execute(
                    delete(EventOutbox).where(
                        EventOutbox.workspace_uuid == workspace_uuid
                    )
                )
                await db.execute(
                    delete(AuditLog).where(AuditLog.workspace_uuid == workspace_uuid)
                )
                await db.execute(
                    delete(RoleAssignment).where(
                        RoleAssignment.workspace_uuid == workspace_uuid
                    )
                )
                await db.execute(
                    delete(Role).where(Role.workspace_uuid == workspace_uuid)
                )
                await db.execute(
                    delete(Member).where(Member.workspace_uuid == workspace_uuid)
                )
                await db.execute(
                    delete(Workspace).where(Workspace.uuid == workspace_uuid)
                )
                if user_uuid is not None:
                    await db.execute(delete(User).where(User.uuid == user_uuid))
                await db.commit()
                print("\ncleanup complete")
            elif keep:
                print(
                    f"\n--keep: workspace={workspace_uuid} retained for inspection"
                )

    print()
    if failures:
        print(f"RESULT: FAIL ({failures}/{len(cases)})")
        return 1
    print(f"RESULT: PASS ({len(cases)}/{len(cases)})")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="A2UI Tool eval runner")
    parser.add_argument(
        "--case", default=None, help="Glob filter on case id (e.g. 'pm.*')"
    )
    parser.add_argument(
        "--keep", action="store_true", help="Don't drop the workspace on exit"
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(_run(filter_glob=args.case, keep=args.keep)))


if __name__ == "__main__":
    main()
