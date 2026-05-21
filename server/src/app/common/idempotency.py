"""Redis-backed idempotency and room-level lock helpers."""

from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from fastapi import HTTPException, status

from src.app.core.config import get_settings

try:
    import redis.asyncio as aioredis
except ImportError:  # pragma: no cover - exercised when optional Redis is absent.
    aioredis = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

T = TypeVar("T")

_redis_client: Any | None = None


def build_huddle_idempotency_key(
    *,
    room_id: str,
    text: str,
    context: dict[str, Any] | None = None,
) -> str:
    """Build a stable idempotency key for the same Huddle room input."""
    payload = {
        "context": context or {},
        "room_id": room_id,
        "text": text,
    }
    serialized = json.dumps(payload, default=str, ensure_ascii=False, sort_keys=True)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"huddle:{room_id}:{digest}"


def _get_redis_client() -> Any | None:
    """Return the lazy Redis client when configured and installed."""
    global _redis_client

    settings = get_settings()
    if not settings.REDIS_URL:
        return None

    if aioredis is None:
        logger.warning("REDIS_URL is set, but the redis package is not installed.")
        return None

    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


def _encode_result(result: Any) -> str:
    """Serialize a task result for Redis storage."""
    return json.dumps(result, default=str, ensure_ascii=False)


def _decode_result(value: str) -> Any:
    """Deserialize a cached task result."""
    return json.loads(value)


async def execute_huddle_task_with_idempotency(  # noqa: UP047
    *,
    idempotency_key: str,
    room_id: str,
    task_factory: Callable[[], Awaitable[T]],
) -> dict[str, Any]:
    """Run a Huddle task with optional Redis idempotency and a room lock."""
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency key is required for this action.",
        )

    redis_client = _get_redis_client()
    if redis_client is None:
        return {"status": "success", "data": await task_factory(), "cached": False}

    settings = get_settings()
    redis_lock_key = f"lock:huddle:room:{room_id}"
    redis_status_key = f"idempotency:{idempotency_key}"
    lock_acquired = False

    current_status = await redis_client.get(redis_status_key)
    if current_status == "PROCESSING":
        logger.info("Duplicate Huddle request is already processing: %s", idempotency_key)
        return {"status": "processing", "message": "The same request is already processing."}
    if current_status and current_status.startswith("DONE:"):
        logger.info("Huddle idempotency cache hit: %s", idempotency_key)
        return {
            "status": "success",
            "data": _decode_result(current_status.removeprefix("DONE:")),
            "cached": True,
        }

    try:
        lock_acquired = bool(
            await redis_client.set(
                redis_lock_key,
                idempotency_key,
                ex=settings.HUDDLE_LOCK_TTL_SECONDS,
                nx=True,
            ),
        )
        if not lock_acquired:
            logger.info("Huddle room is already locked: %s", room_id)
            return {"status": "locked", "message": "This room is already processing a request."}

        await redis_client.set(
            redis_status_key,
            "PROCESSING",
            ex=settings.HUDDLE_PROCESSING_TTL_SECONDS,
        )

        result = await task_factory()
        await redis_client.set(
            redis_status_key,
            f"DONE:{_encode_result(result)}",
            ex=settings.HUDDLE_IDEMPOTENCY_TTL_SECONDS,
        )
        return {"status": "success", "data": result, "cached": False}
    except Exception:
        await redis_client.delete(redis_status_key)
        raise
    finally:
        if lock_acquired:
            await redis_client.delete(redis_lock_key)
