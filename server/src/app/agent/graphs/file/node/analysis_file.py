import textwrap

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from src.app.agent.graphs.file.model import FileContentAnalysisState
from src.app.core.logger import logger
from src.app.core.base import get_model

async def analysis_file(state: FileContentAnalysisState, config: RunnableConfig) -> dict:
    logger.info(f"Analyzing file: {state.file_path}")
    extracted_content = state.extracted_content

    result_content = ""

    if not extracted_content or extracted_content.startswith("Error:"):
        logger.warning("No extracted content found")
        result_content = extracted_content or "Error: No extracted content found"
        return {
            "processed_content": result_content,
            "messages": [AIMessage(content=result_content, name="file_content_subgraph")]
        }
    
    if state.file_task == "extract":
        logger.info("Extracting content from file")
        result_content = extracted_content
        return {
            "processed_content": result_content,
            "messages": [AIMessage(content=result_content, name="file_content_subgraph")]
        }

    try:
        user_question = state.user_question
        if not user_question:
            raise ValueError("User question is required")
        
        prompt = textwrap.dedent(f"""
        You are a helpful assistant that analyzes files.
        You are given a file and a question.
        You need to analyze the file and answer the question.
        The file is: {extracted_content}
        The question is: {user_question}
        Return the answer in the same language as the question.
        """)

        messages = [HumanMessage(content=prompt)]

        model = get_model(config, "gpt-4o-mini", "file_analysis_model")
        response = await model.ainvoke(messages, config=config)
        result_content = (response.content or "").strip()
        logger.info(f"Processed content: {result_content}")
    except Exception as e:
        logger.error(f"Error analyzing file: {e}")
        result_content = f"Error: {e}"
    
    return {
        "processed_content": result_content,
        "messages": [AIMessage(content=result_content, name="file_content_subgraph")]
    }
