"""Comms HTTP routes. Thin layer over service.* — no business logic here."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/comms", tags=["comms"])

# Routes land here as the Comms surface grows.
