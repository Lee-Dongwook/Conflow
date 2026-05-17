"""Optional cache layer (e.g. Redis) for embeddings and retrieve results."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class CacheBackend(Protocol):
    """Async key-value cache used before hitting the vector store."""

    async def get(self, key: str) -> str | None:
        """Return cached value or None."""
        ...

    async def set(
        self,
        key: str,
        value: str,
        ttl_seconds: int | None = None,
    ) -> None:
        """Store value with optional TTL."""
        ...

    async def delete(self, key: str) -> None:
        """Remove a key."""
        ...
