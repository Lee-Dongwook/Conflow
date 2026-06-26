"""Pydantic Input / Output schemas for HR service functions.

Per docs/04-architecture/a2ui-strategy.md "Schema-first": every service
function exposes Pydantic schemas so it can be lifted into the A2UI Tool
Registry without rework. Response schemas must respect the four-layer
privacy classification declared on each model column.
"""

from __future__ import annotations

# Schemas land here as the HR service surface grows.
