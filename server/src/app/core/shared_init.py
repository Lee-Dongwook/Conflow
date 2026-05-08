import os

import dotenv

from . import logger


def initialize() -> None:
    logger.info("Initializing shared variables...")

    if os.environ.get("ENV_PATH", ""):
        path = os.environ.get("ENV_PATH")
        if "$PATH" in path:
            path = path.replace("$PATH", os.environ.get("PATH"))
        else:
            path = f"{path}{os.path.sep}{os.environ.get('PATH')}"
        os.environ["PATH"] = path
        del os.environ["ENV_PATH"]
        logger.info(f"set PATH={path}")

def load_dotenv(env_type: str) -> None:
    logger.info(f"Loading environment variables from .env.{env_type} file...")

    if os.getenv("DB_HOST"):
        logger.info("Database environment variables are set")
        return
    
    env_files = {
        "local": ".env.local",
        "development": ".env",
        "production": ".env",
        "test": ".env.pytest"
    }
    env_file = env_files.get(env_type, ".env")
    env_file = dotenv.find_dotenv(env_file)
    if os.path.exists(env_file):
        dotenv.load_dotenv(env_file)
        logger.info(f"Loaded environment variables from {env_file}")
    else:
      dotenv_file = dotenv.find_dotenv()
      if dotenv_file:
        logger.info(f"Loaded environment variables from {dotenv_file}")
        dotenv.load_dotenv(dotenv_file)
      else:
        logger.warning("No environment file found")
