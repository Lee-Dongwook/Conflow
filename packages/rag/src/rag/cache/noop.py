"""No-op cache for development and tests."""


class NoOpCache:
    """Cache backend that always misses."""

    async def get(self, key: str) -> str | None:
        """Always return None."""
        _ = key
        return None

    async def set(
        self,
        key: str,
        value: str,
        ttl_seconds: int | None = None,
    ) -> None:
        """No-op."""
        _ = key, value, ttl_seconds

    async def delete(self, key: str) -> None:
        """No-op."""
        _ = key
