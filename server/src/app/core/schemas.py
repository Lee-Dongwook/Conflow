from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, field_validator

T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):  # noqa: UP046
    code : int
    message: str
    data: T | None = None

class Paging(BaseModel):
    total: int
    last_offset: int

class PagingResponse(ResponseModel[T]):
    paging: Paging

class PagingQuery(BaseModel):
    query: str | None = None
    page: int | None = None
    size: int | None = None

    @field_validator("query", mode="before")
    @classmethod
    def empty_str_to_none(cls, value: str | None) -> str | None:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @field_validator("page", mode="before")
    @classmethod
    def page_to_be_positive(cls, value: int | None) -> int | None:
        if value is None:
            value = 1
        elif value < 1:
            raise ValueError("Page must be greater than 0")
        return value

    @field_validator("size", mode="before")
    @classmethod
    def size_to_be_positive(cls, value: int | None) -> int | None:
        if value is None:
            value = 10
        elif value < 1:
            raise ValueError("Size must be greater than 0")
        elif value > 200:
            raise ValueError("Size must be less than 200")
        return value
    
    model_config = ConfigDict(populate_by_name=True)
