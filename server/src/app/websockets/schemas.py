"""Pydantic schemas for WebRTC signaling over WebSocket."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class SignalingMessageBase(BaseModel):
    """Shared config for signaling payloads."""

    model_config = ConfigDict(populate_by_name=True)


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
    candidate: str
    sdp_mid: str | None = Field(default=None, validation_alias="sdpMid", serialization_alias="sdpMid")
    sdp_mline_index: int | None = Field(
        default=None,
        validation_alias="sdpMLineIndex",
        serialization_alias="sdpMLineIndex",
    )


SignalingMessage = Annotated[
    OfferMessage | AnswerMessage | IceMessage,
    Field(discriminator="type"),
]


def parse_signaling_message(raw: str) -> OfferMessage | AnswerMessage | IceMessage:
    """Parse a JSON signaling frame from the wire."""
    from pydantic import TypeAdapter

    adapter: TypeAdapter[SignalingMessage] = TypeAdapter(SignalingMessage)
    return adapter.validate_json(raw)
