from __future__ import annotations

import re
import textwrap
from typing import Literal

from langchain_core.runnables import RunnableConfig
from langgrpah.types import Command
from pydantic import BaseModel, Field
from trustcall import create_extractor

from src.app.core.logger import logger

URL_PATTERN_LIST = re.compile(
    r'https?://'
    r'(?:[^\s/?#]+)'
    r'(?:/[^\s?#]*)?'
    r'(?:\?[^\s#]*)?'
    r'(?:#[^\s]*)?',
    re.UNICODE
)
