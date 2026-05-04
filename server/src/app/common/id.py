from __future__ import annotations

import random
import time
import uuid

_last_v6_timestamp: int | None = None

class UUID(uuid.UUID):
    __slots__ = ()

    def __init__(
        self,
        hex: str | None = None,
        bytes: bytes | None = None,
        bytes_le: bytes | None = None,
        fields: tuple[int, int, int, int, int, int] | None = None,
        int: int | None = None,
        version: int | None = None,
        *,
        is_safe: uuid.SafeUUID = uuid.SafeUUID.unknown,
    ) -> None:

        if int is None or [hex, bytes, bytes_le, fields].count(None) != 4:
            return super().__init__(
                hex=hex,
                bytes=bytes,
                bytes_le=bytes_le,
                fields=fields,
                int=int,
                version=version,
                is_safe=is_safe,
            )
        
        if not 0 <= int < 1 << 128:
            raise ValueError("int is out of range (need a 128-bit value)")
        
        if version is not None:
            if not 6 <= version <= 8:
                raise ValueError("illegal version number")
            int &= ~(0xC000 << 48)
            int |= 0x8000 << 48
            int &= ~(0xF000 << 64)
            int |= version << 76
        super().__init__(int=int, is_safe=is_safe)
    
    @property
    def subsec(self) -> int:
        return ((self.int >> 64) & 0x0FFF) << 8 | ((self.int >> 54) & 0xFF)
    
    @property
    def time(self) -> int:  # noqa: F811
        if self.version == 6:
            return (self.time_low << 28) | (self.time_mid << 12) | (self.time_hi_version & 0x0FFF)
        if self.version == 7:
            return self.int >> 80
        return super().time
    


def uuid6(node: int | None = None, clock_seq: int | None = None) -> UUID:
    global _last_v6_timestamp
    
    nanoseconds = time.time_ns()

    timestamp = nanoseconds // 100 + 0x01B21DD213814000
    if _last_v6_timestamp is not None and timestamp <= _last_v6_timestamp:
        timestamp = _last_v6_timestamp + 1
    _last_v6_timestamp = timestamp

    if clock_seq is None:
        clock_seq = random.getrandbits(14)
    
    if node is None:
        node = random.getrandbits(48)
    
    time_high_and_time_mid = (timestamp >> 12) & 0xFFFFFFFFFFFF
    time_low_and_version = timestamp & 0x0FFF
    uuid_int = time_high_and_time_mid << 80
    uuid_int |= time_low_and_version << 64
    uuid_int |= (clock_seq & 0x3FFF) << 48
    uuid_int |= node & 0xFFFFFFFFFFFF
    return UUID(int=uuid_int, version=6)


def uuid7(nanoseconds: int | None = None) -> UUID:
    try:
        import uuid_utils
        if nanoseconds is None:
            return UUID(int=uuid_utils.uuid7().int, version=7)
        seconds, nanos = divmod(nanoseconds, 1_000_000_000)
        return UUID(int=uuid_utils.uuid7(timestamp=seconds, nanos=nanos).int, version=7)
    except (ImportError, AttributeError):
        ns = nanoseconds if nanoseconds is not None else time.time_ns()
        timestamp_ms = ns // 10**6
        uuid_int = (timestamp_ms & 0xFFFFFFFFFFFF) << 80
        uuid_int |= random.getrandbits(74)
        return UUID(int=uuid_int, version=7)
