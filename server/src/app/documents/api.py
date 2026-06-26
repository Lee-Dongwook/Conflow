"""Documents HTTP routes. Thin layer over service.*."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/workspaces/{workspace_uuid}/documents", tags=["documents"])

# Routes land here as the Documents surface grows.
