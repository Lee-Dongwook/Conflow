import base64
import os
from pathlib import Path
from typing import Literal

import magic
from langchain_core.messages import ChatMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END
from langgraph.types import Command
from src.app.agent.graphs.image.model import ImageSubgraphState
from src.app.agent.graphs.image.utils import download_image_url, extract_text_from_image
from src.app.core.base import get_model


def candidate_base64_image(image_data: str) -> bool:
    if image_data.startswith("data:image"):
        return True
    candidate = image_data.split(",", 1)[1] if image_data.startswith("data:") and "," in image_data else image_data
    if len(candidate) < 64:
        return False
    try:
        base64.b64decode(candidate, validate=True)
        return True   
    except Exception:
        return False

async def process_image_node(
    state: ImageSubgraphState,
    config: RunnableConfig,
) -> Command[Literal[END, "quality_check", "analysis_image"]]:
    image_task = state.image_task

    # TODO: Have to handle image bucket storage
    image_url_data = state.image_data
    extracted_text = None
    last_element = None

    image_source_type = state.image_source_type
    file_extension = None

    if image_source_type == "auto":
        if image_url_data.startswith(("http://", "https://")):
            image_source_type = "url"
        elif candidate_base64_image(image_url_data):
            image_source_type = "base64"
        else:
            image_source_type = "internal"
    
    if image_source_type == "internal":
        image_source_type = "url"
    
    if image_source_type == "url" and not image_url_data.startswith("http"):
        file_url = image_url_data
        file_extension = Path(file_url).suffix.lower()

        if file_extension in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
            image_url_data = f"https://storage.googleapis.com/image_bucket/{file_url}" 
            # TODO: Have to switch an example to real bucket url
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")
        
    
    if image_task == "ocr" or image_task == "ocr_accurate":
        image_bytes = None
        try:
            if image_task == "ocr":
                if image_source_type == "base64":
                    image_data = state.image_data
                    if "," in image_data:
                        image_data_split = image_data.split(",", 1)[1]
                    image_bytes = base64.b64decode(image_data_split)
                elif image_url_data.startswith("http"):
                    image_bytes = await download_image_url(image_url_data)
                
                if not image_bytes:
                    raise ValueError("Failed to download or decode image")
            
            elif image_task == "ocr_accurate":
                image_url_for_llm = image_url_data
                if image_source_type == "url" and image_url_data.startswith("http"):
                    image_bytes = await download_image_url(image_url_data)
                    if not image_bytes:
                        raise ValueError("Failed to download image")
                    decoded_v = base64.b64encode(image_bytes).decode("utf-8")
                    mimetype = magic.from_buffer(image_bytes, mime=True)
                    image_url_for_llm = f"data:{mimetype};base64,{decoded_v}"
                
                ocr_prompt="""
                You are a helpful assistant that extracts text from images.
                You are given an image and a question.
                You need to extract the text from the image and answer the question.
                The image is: {image_url_for_llm}
                The question is: {user_question}
                Return the answer in the same language as the question.
                """
                messages = [
                    HumanMessage(
                        content=[
                            {"type": "text", "text": ocr_prompt},
                            {"type": "image_url", "image_url": {"url": image_url_for_llm}}
                        ]
                    )
                ]

                model = get_model(
                    config,
                    "gpt-4o-mini",
                    "image_ocr_model"
                )

                response = await model.ainvoke(
                    messages,
                    config={
                        **config,
                        "configurable": {
                            **config.get("configurable", {}),
                            "ocr_disable_streaming": True,
                        }
                    }
                )

                if not isinstance(response.content, str):
                    raise RuntimeError("Invalid response content")
                
                extracted_text = response.content.strip()

                if not extracted_text or extracted_text.strip().upper() == "FAIL":
                    raise ValueError("Failed to extract text from image")
        
        except Exception as e:
            last_element = e
    
    elif image_task == "direct_analysis":
        image_url_for_llm = None

        try:
            if image_url_data.startswith(("http://", "https://")):
                image_bytes = await download_image_url(image_url_data)
                if not image_bytes:
                    raise ValueError("Failed to download image")
                decoded_v = base64.b64encode(image_bytes).decode("utf-8")
                mimetype = magic.from_buffer(image_bytes, mime=True)
                image_url_for_llm = f"data:{mimetype};base64,{decoded_v}"
            
            if not image_url_for_llm:
                raise ValueError("Failed to prepare image for LLM")
            
            return Command(
                goto="analysis_image",
                update={
                    "extracted_text": None,
                    "image_url": image_url_for_llm,
                }
            )
        
        except Exception as e:
            last_element = e
    
    if last_element is None and extracted_text:
        return Command(
            goto="quality_check",
            update={
                "extracted_text": extracted_text,
                "messages": [
                    ChatMessage(
                        content="Extracted text: " + extracted_text,
                        name="image_subgraph",
                        role="assistant" 
                    )
                ]
            }
        )
    
    return Command(
        goto=END,
         update={
            "extracted_text": "FAIL",
            "messages": [
                ChatMessage(
                    content="Failed to process image.",
                    name="image_subgraph",
                    role="assistant",
                    additional_kwargs={"error": str(last_element) if last_element else "OCR returned no text."},
                ),
            ],
        },
    )





