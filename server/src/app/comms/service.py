"""Headless Comms service functions.

Every public function takes `workspace_uuid` and `caller_member_uuid` as
keyword-only arguments and returns Pydantic models — no React, no FastAPI
Depends (docs/04-architecture/a2ui-strategy.md).
"""

from __future__ import annotations

# Service functions land here as the Comms surface grows.
