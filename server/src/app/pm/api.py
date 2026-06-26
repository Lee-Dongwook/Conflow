"""PM HTTP routes. Thin layer over service.* — no business logic here."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/pm", tags=["pm"])

# Routes land here as the PM surface grows.
