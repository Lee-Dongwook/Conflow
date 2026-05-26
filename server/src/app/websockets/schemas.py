"""Pydantic schemas for WebRTC signaling over WebSocket."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class SignalingMessageBase(BaseModel):
    """Shared config for signaling payloads."""
    model_config = ConfigDict(populate_by_name=True)
    sender_id: str = Field(description="The ID of the sender")
    target_id: str | None = Field(default=None, description="The ID of the target")


class OfferMessage(SignalingMessageBase):
    """SDP offer from the initiating peer."""
    type: Literal["offer"] = "offer"
    sdp: str


class AnswerMessage(SignalingMessageBase):
    """SDP answer from the receiving peer."""
    type: Literal["answer"] = "answer"
    sdp: str


class IceMessage(SignalingMessageBase):
    """Trickle ICE candidate."""
    type: Literal["ice"] = "ice"
    candidate: str | dict = Field(description="The ICE candidate")
    sdp_mid: str | None = Field(default=None, validation_alias="sdpMid", serialization_alias="sdpMid")  # noqa: E501
    sdp_mline_index: int | None = Field(
        default=None,
        validation_alias="sdpMLineIndex",
        serialization_alias="sdpMLineIndex",
    )

class JoinMessage(SignalingMessageBase):
    """Join a signaling room."""
    type: Literal["join"] = "join"
    room_id: str = Field(description="The ID of the room")

class LeaveMessage(SignalingMessageBase):
    """Leave a signaling room."""
    type: Literal["leave"] = "leave"
    room_id: str = Field(description="The ID of the room")

class SystemControlMessage(SignalingMessageBase):
    """System control message."""
    type: Literal["control"] = "control"
    action: Literal["mute", "unmute", "start_stt", "stop_stt", "agent_interrupt"]
    payload: dict | None = Field(default=None, description="The payload of the message")



SignalingPayload = Annotated[
    OfferMessage | AnswerMessage | IceMessage | JoinMessage | LeaveMessage | SystemControlMessage,
    Field(discriminator="type"),
]

SignalingMessage = SignalingPayload

_SIGNALING_ADAPTER: TypeAdapter[SignalingPayload] = TypeAdapter(SignalingPayload)


def parse_signaling_message(raw: str) -> SignalingPayload:
    """Parse a JSON signaling frame from the wire."""
    return _SIGNALING_ADAPTER.validate_json(raw)
