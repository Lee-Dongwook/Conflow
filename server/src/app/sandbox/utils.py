import logging
import os
import re
from collections.abc import Callable
from pathlib import Path, PurePosixPath
from typing import Any, overload

logger = logging.getLogger(__name__)

# Constants List
MAX_LINE_LENGTH = 1000
LINE_NUMBER_WIDTH = 6
TOOL_RESULT_TOKEN_LIMIT = 20000
TRUNCATION_GUIDANCE = "... [results truncated, try being more specific with your parameters]"
MAX_READ_LINES = 5000
MAX_RAW_READ_SIZE = 512 * 1024 # 512KB

# URI Schemes Policy
DEFUALT_ALLOWED_SCHEMES = ["skills", "sandbox"]

def count_lines(file_path: str | Path) -> int:
    count = 0
    with open(file_path, "rb") as f:
        buf_size = 1024 * 1024
        read_f = f.read
        buf = read_f(buf_size)
        while buf:
            count += buf.count(b"\n")
            buf = read_f(buf_size)
    return count

def read_last_lines(file_path: str | Path, n: int) -> str:
    if n <= 0:
        return ""
    
    with open(file_path, "rb") as f:
        f.seek(0, os.SEEK_END)
        file_size = f.tell()

        buffer_size = 64 * 1024 # 64KB
        lines_found = 0
        pos = file_size
        blocks: list[bytes] = []

        while pos > 0 and lines_found < n:
            pos = max(0, pos - buffer_size)
            f.seek(pos, os.SEEK_SET)
            chunk = f.read(min(buffer_size, file_size - pos))
            
            lines_found += chunk.count(b"\n")
            blocks.insert(0, chunk)

            if pos == 0:
                break

        full_content = b"".join(blocks)
        lines = full_content.splitlines(keepends=True)
        result_lines = lines[-n:]
        return b"".join(result_lines).decode("utf-8", errors="ignore")

def validate_path(path: str, user_root: str | Path) -> Path:
    user_root_path = Path(user_root).resolve()

    parts = PurePosixPath(path.replace("\\", "/")).parts
    if ".." in parts or path.startswith("~"):
        raise ValueError(f"Path traversal is not allowed: {path}")

    if re.match(r"^[a-zA-Z]:\\", path):
        return ValueError(f"Windows drive paths are not allowed: {path}")
    
    normalized_virtual_path = os.path.normpath(path).lstrip("/")
    final_path = (user_root_path / normalized_virtual_path).resolve()

    try:
        final_path.relative_to(user_root_path)
    except ValueError as e:
        raise ValueError(f"Invalid path: {e}") from e

    return final_path
