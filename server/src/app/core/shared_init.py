import os

import dotenv

from . import logger


def initialize() -> None:
    logger.info("Initializing shared variables...")

    env_path = os.environ.get("ENV_PATH", "")
    if env_path:
        # Validate each directory exists and is an absolute path
        current_path = os.environ.get("PATH", "")
        new_dirs = [
            d for d in env_path.split(os.pathsep)
            if d and d != "$PATH" and os.path.isabs(d) and os.path.isdir(d)
        ]
        if new_dirs:
            os.environ["PATH"] = os.pathsep.join(new_dirs) + os.pathsep + current_path
        del os.environ["ENV_PATH"]
        logger.info(f"Updated PATH with validated directories: {new_dirs}")

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
