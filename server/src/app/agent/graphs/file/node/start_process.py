from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel
from src.app.agent.graphs.file.model import FileSubgraphInputState, FileSubgraphState


async def start_process(state: FileSubgraphInputState, config: RunnableConfig) -> FileSubgraphState:
    if isinstance(state, BaseModel):
        state_dict = state.model_dump(exclude_none=True)
    
    file_path = state_dict.get("file_path")
    user_question = state_dict.get("user_question")
    file_task = state_dict.get("file_task")

    if isinstance(file_path, str):
        target_file_lists = [file_path]
    else:
        target_file_lists = file_path
    
    if not state_dict.get("file_info_list"):
        state_dict["file_path"] = None
        state_dict["user_question"] = None
        return state_dict
    
    for target_file in target_file_lists:
        is_found = False
        for file_info in state_dict["file_info_list"]:
            if file_info["file_url"] == target_file:
                file_info["user_question"] = user_question
                file_info["file_task"] = file_task
                is_found = True
                break
        
        if not is_found:
            continue
    

    state_dict["file_path"] = None
    state_dict["user_question"] = None
    return state_dict
