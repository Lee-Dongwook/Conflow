"""Comms domain — Channel, Message, Thread, Mention, Reaction, Huddle.

Owns the conversation aggregate. The HR domain's 1:1 notes are NOT in here
(see docs/02-product/domain-overview.md). Decision detection and Huddle land
in Phase 2.
"""

from .model import (
    Channel,
    ChannelMember,
    ChannelType,
    Message,
)

__all__ = [
    "Channel",
    "ChannelMember",
    "ChannelType",
    "Message",
]
