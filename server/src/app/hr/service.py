"""Headless HR service functions.

Every public function takes `workspace_uuid` and `caller_member_uuid` as
keyword-only arguments (docs/04-architecture/a2ui-strategy.md). Response
serialization must consult the column-level `info={"privacy": ...}`
metadata declared in `hr.model` before returning fields to the caller.
"""

from __future__ import annotations

# Service functions land here as the HR surface grows.
