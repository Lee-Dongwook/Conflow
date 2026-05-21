"""Tests for Huddle idempotency helpers."""

from __future__ import annotations

import asyncio
from typing import Any

from src.app.common import idempotency


class FakeRedis:
    """Minimal async Redis fake for idempotency behavior."""

    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        """Return a stored value."""
        return self.values.get(key)

    async def set(self, key: str, value: str, **kwargs: Any) -> bool:
        """Store a value, honoring nx."""
        if kwargs.get("nx") and key in self.values:
            return False
        self.values[key] = value
        return True

    async def delete(self, key: str) -> None:
        """Delete a stored value."""
        self.values.pop(key, None)


def test_execute_huddle_task_caches_completed_result(
    monkeypatch: Any,
) -> None:
    """The same idempotency key should return the cached first result."""
    fake_redis = FakeRedis()
    call_count = 0

    monkeypatch.setattr(idempotency, "_get_redis_client", lambda: fake_redis)

    async def task() -> dict[str, str]:
        nonlocal call_count
        call_count += 1
        return {"answer": "done"}

    async def run() -> tuple[dict[str, Any], dict[str, Any]]:
        first = await idempotency.execute_huddle_task_with_idempotency(
            idempotency_key="request-1",
            room_id="room-1",
            task_factory=task,
        )
        second = await idempotency.execute_huddle_task_with_idempotency(
            idempotency_key="request-1",
            room_id="room-1",
            task_factory=task,
        )
        return first, second

    first, second = asyncio.run(run())

    assert first == {"status": "success", "data": {"answer": "done"}, "cached": False}
    assert second == {"status": "success", "data": {"answer": "done"}, "cached": True}
    assert call_count == 1


def test_execute_huddle_task_returns_locked_when_room_lock_exists(
    monkeypatch: Any,
) -> None:
    """Concurrent room work should not start another task."""
    fake_redis = FakeRedis()
    fake_redis.values["lock:huddle:room:room-1"] = "other-request"
    monkeypatch.setattr(idempotency, "_get_redis_client", lambda: fake_redis)

    async def task() -> dict[str, str]:
        return {"answer": "done"}

    result = asyncio.run(
        idempotency.execute_huddle_task_with_idempotency(
            idempotency_key="request-2",
            room_id="room-1",
            task_factory=task,
        ),
    )

    assert result == {
        "status": "locked",
        "message": "This room is already processing a request.",
    }
