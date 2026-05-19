from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from src.app.core.logger import logger


def normalize_model_name(model_name: str) -> tuple[str, str]:
    gemini_models = ["gemini-2.5-pro", "gemini-2.5-flash"]
    if "gemini-" in model_name and any(n in model_name for n in gemini_models):
        if "/" in model_name and model_name.startswith("models/"):
            model_name = model_name[7:]
        return "gemini", model_name

    openai_models = [
        "gpt-4o-mini", "gpt-4o", "gpt-4.1", "gpt-4.1-nano", "gpt-4.1-mini",
        "gpt-5",
        "gpt-5-mini",
        "gpt-5-nano",
    ]

    if model_name in openai_models:
        return "openai", model_name
    
    anthropic_models = [
     "claude-opus-4-0",
     "claude-opus-4-0-sonnet",
     "claude-opus-4-0-sonnet-20250514",
     "claude-opus-4-0-sonnet-20250514",
     "claude-sonnet-4-5",
     "claude-sonnet-4-5-sonnet",
     "claude-sonnet-4-5-sonnet-20250514",
     "claude-sonnet-4-5-sonnet-20250514",
    ]

    if model_name in anthropic_models:
        return "anthropic", model_name
    return "openai", "gpt-4o-mini"


def get_llm_model(model_type: str, model_name: str,
    temperature: float = 0.0, max_tokens: int = 8000, config_prefix: str = ""
    ) -> BaseChatModel:
    from langchain.chat_models import init_chat_model

    model_key = f"{model_type}:{model_name}" if model_type != "" else model_name

    llm_model = None

    try:
        configurable_state_field = ("temperature", "disable_streaming", "model", "model_provider")
        if model_type in ["gemini", "google_genai", "openai", "anthropic"]:
            if model_type == "gemini":
                model_type = "google_genai"
            
            llm_model = init_chat_model(
                model=model_name,
                model_provider=model_type,
                configurable_fields=configurable_state_field,
                config_prefix=config_prefix,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            llm_model = init_chat_model(
                model=model_name,
                configurable_fields=configurable_state_field,
                config_prefix=config_prefix,
                temperature=temperature,
                max_tokens=max_tokens,
            )
    except Exception as e:
        logger.warning(f"Error initializing {model_key} model: {e}")
    
    if llm_model is None:
        llm_model = ChatOpenAI(model="gpt-4o-mini", temperature=temperature, max_output_tokens=max_tokens)
    
    return llm_model


def get_model(config: RunnableConfig, default: str, key: str) -> BaseChatModel:
    config_prefix = key[:-6] if key.endswith("_model") else key
    configurable_state = config.get("configurable", {})
    model_name = configurable_state.get(key) or config.get(key, default)

    temperature = 0.0

    temperature = float(configurable_state.get(f"{key}_temperature", 
     configurable_state.get(f"{config_prefix}_temperature", 0.0))
    )

    if temperature:
        logger.info(f"Setting temperature for {key} to {temperature}")

    max_tokens = 8000
    max_tokens = int(configurable_state.get(f"{key}_max_tokens", 
    configurable_state.get(f"{config_prefix}_max_tokens", 8000)
    ))
    if max_tokens != 8000:
        logger.info(f"Setting max tokens for {key} to {max_tokens}")

    model_map = {
        "openai": "gpt-5-mini",
        "gemini": "gemini-2.5-flash",
        "anthropic": "claude-4-sonnet-20250514",
    }
    model_name = model_map.get(model_name, model_name)

    if ":" in model_name:
        parts = model_name.split(":", 1)
        model_type = parts[0]
        model_name = parts[1]
    else:
        model_type, model_name = normalize_model_name(model_name)
    
    logger.info(f"Using model: {model_name} ({model_type})")

    llm_model = get_llm_model(
        model_type=model_type,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        config_prefix=config_prefix,
    )

    if llm_model:
        return llm_model
    
    logger.warning(f"No model found for {key}, using default: {default}")
    return get_llm_model("openai", model_name="gpt-4o-mini", temperature=temperature, config_prefix=config_prefix)
