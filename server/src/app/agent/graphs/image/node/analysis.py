from langchain_core.messages import ChatMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from src.app.agent.graphs.image.model import ImageSubgraphState
from src.app.core.base import get_model
from src.app.core.logger import logger


async def analysis_image(state: ImageSubgraphState, config: RunnableConfig) -> dict:
    image_url = state.image_url
    user_question = state.user_question

    if not image_url or not user_question:
        return {"processed_content": "Error: Image URL and user question are required"}
    
    try:
        message_content = [
            {"type": "text", "text": user_question},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
        messages = [HumanMessage(content=message_content)]

        model = get_model(config, "gpt-4o-mini", "image_analysis_model")
        response = await model.ainvoke(
            messages,
            config={
                **config,
                "configurable": {
                    **config.get("configurable", {}),
                    "image_disable_streaming": True,
                }
            }
        )
        processed_content = (response.content or "").strip()
        logger.info(f"Processed content: {processed_content}")
        return {
            "processed_content": processed_content,
            "messages": [
                ChatMessage(
                    content=processed_content, 
                    role="assistant",
                    name="image_analysis_subgraph"
                ),
            ],
        }

    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return {"processed_content": f"Error: {e}"}
