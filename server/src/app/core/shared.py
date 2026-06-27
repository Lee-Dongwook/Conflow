"""Process-wide shared handles (logging, optional background workers)."""

from __future__ import annotations

import logging
from typing import Any

# init logger using uvicorn.error
logger = logging.getLogger("uvicorn.error")

# global shared variables
scheduler: Any | None = None
celery_enabled: bool = False
