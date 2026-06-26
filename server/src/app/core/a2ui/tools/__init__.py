"""A2UI Tool registrations.

Import side-effect only: each module calls `register_tool(...)` at load.
`main.py` lifespan imports this package once so the registry is populated
before the first HTTP request.
"""

from __future__ import annotations

from . import comms, documents, hr, pm  # noqa: F401  side-effect imports
