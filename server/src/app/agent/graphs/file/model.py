from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator


class FileInfo(BaseModel):
    uuid: str
    original_file_name: str
    file_url: str
    file_size: int
    file_extension: str
    user_question: str | None = None
    file_task: str | None = None

class FileSubgraphOutputState(BaseModel):
    uuid: str
    original_file_name: str
    file_url: str
    file_size: int
    file_extension: str
    success: bool
    content: str

def file_results_reducer(existing: list[FileSubgraphOutputState], new: list[FileSubgraphOutputState]) -> list[FileSubgraphOutputState]:  # noqa: E501
    if new == []:
        return []

    if not existing:
        return new

    result = existing.copy()
    for item in new:
        item_name = item.original_file_name if hasattr(item, 'original_file_name') else item.get('original_file_name')  # noqa: E501

        already_exists = False
        for existing_item in result:
            existing_name = existing_item.original_file_name if hasattr(existing_item, 'original_file_name') else existing_item.get('original_file_name')  # noqa: E501
            if existing_name == item_name:
                already_exists = True
                break

        if not already_exists:
            result.append(item)

    return result


class FileSubgraphInputState(BaseModel):
    user_uuid: str | None = None
    file_path: str | list[str] = Field(..., description="The path to the file to process")
    user_question: str = Field(..., description="The question to ask the file")
    file_task: str = Field(..., description="The task to perform on the file")
    file_info_list: list[FileInfo]| None = None
    file_process_results: Annotated[list[FileSubgraphOutputState] | None, file_results_reducer] = None  # noqa: E501

class FileSubgraphState(BaseModel):
    user_uuid: str | None
    file_path: str | None
    user_question: str | None
    file_task: str | None
    file_info_list: list[FileInfo] | None
    file_process_results: Annotated[list[FileSubgraphOutputState] | None, file_results_reducer] = None  # noqa: E501
    structured_response: dict | None = None

class FileContentAnalysisState(BaseModel):
    file_path: str = Field(..., description="The path to the file to analyze")
    user_uuid: str | None = None
    user_question: str = Field(..., description="The question to ask the file")
    file_task: Literal["extract", "extract_and_process"] = Field(
        ...,
        description="The task to perform on the file"
    )
    start_page: int | None = Field(None, description="The start page of the file to analyze")
    end_page: int | None = Field(None, description="The end page of the file to analyze")

    extracted_content: str | None = None
    processed_content: str | None = None

    @field_validator("file_task", mode="before")
    @classmethod
    def validate_file(cls, v: str) -> str:
        if isinstance(v, str):
            lower_v = v.lower()
            if "analyze" in lower_v or "process" in lower_v:
                return "extract_and_process"
            elif "extract" in lower_v or "save" in lower_v:
                return "extract"
            
        return v if v in ["extract", "extract_and_process"] else "extract"
