from typing import Annotated
from pydantic import BaseModel, Field

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

def file_results_reducer(existing: list[FileSubgraphOutputState], new: list[FileSubgraphOutputState]) -> list[FileSubgraphOutputState]:
    if new == []:
        return []

    if not existing:
        return new

    result = existing.copy()
    for item in new:
        item_name = item.original_file_name if hasattr(item, 'original_file_name') else item.get('original_file_name')

        already_exists = False
        for existing_item in result:
            existing_name = existing_item.original_file_name if hasattr(existing_item, 'original_file_name') else existing_item.get('original_file_name')
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
    file_process_results = Annotated[list[FileSubgraphOutputState] | None, file_results_reducer] = None

class FileSubgraphState(BaseModel):
    user_uuid: str | None
    file_path: str | None
    user_question: str | None
    file_task: str | None
    file_info_list: list[FileInfo] | None
    file_process_results: Annotated[list[FileSubgraphOutputState] | None, file_results_reducer] = None
    structured_response: dict | None = None
