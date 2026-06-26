"""HR HTTP routes. Thin layer over service.* — no business logic here."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/workspaces/{workspace_uuid}/hr", tags=["hr"])

# Routes land here as the HR surface grows.
