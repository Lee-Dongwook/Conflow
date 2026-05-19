from typing import Literal

from langchain_core.messages import AnyMessage
from pydantic import BaseModel, Field, field_validator


class ImageSubgraphState(BaseModel):
    image_task: Literal["ocr", "ocr_accurate", "direct_analysis"] = Field(
        ...,
        description="The task to perform on the image"
    )

    image_source_type: Literal["url", "internal", "base64", "auto"] = Field(
        ...,
        description="The type of the image source"
    )

    image_data: str = Field(
        ...,
        description="The data of the image"
    )

    user_question: str = Field(
        ...,
        description="The question to ask the image"
    )

    user_uuid: str | None = None
    retry_count: int = 0

    extracted_text: str | None = None
    image_url: str | None = None
    ocr_quality: Literal["low", "medium", "high"] | None = None
    processed_content: str | None = None
    messages: list[AnyMessage] = Field(default_factory=list)

    @field_validator("image_source_type", mode="before")
    @classmethod
    def normalize_source_type(cls, v: str) -> str:
        
        normalized_v = v.strip().lower().replace("-", "_")
        compact_v = normalized_v.replace("_", "")

        if normalized_v in {"url", "internal", "base64", "auto"}:
            return normalized_v
        if normalized_v == "internal_url" or "internal" in normalized_v:
            return "internal"
        if compact_v in {"httpurl", "httpsurl", "remoteurl"}:
            return "url"
        if compact_v in {"base64url", "dataurl"}:
            return "base64"
        return "auto"
