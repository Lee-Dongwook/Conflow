import logging
import os
import re
import tempfile
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
MAX_RAW_WRITE_SIZE = 1 * 1024 * 1024 # 1MB

# URI Schemes Policy
DEFUALT_ALLOWED_SCHEMES = ["skills", "sandbox"]
DEFAULT_ALLOWED_EXTENSIONS = [
    ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".xml", ".csv",
    ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".scss", ".less",
]

def count_lines(file_path: str | Path) -> int:
    """
    Counts the number of lines in a given file.

    Args:
        file_path (str | Path): The path to the file.

    Returns:
        int: The total number of lines in the file.
    """
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
    """
    Reads the last 'n' lines from a specified file.

    Args:
        file_path (str | Path): The path to the file.
        n (int): The number of last lines to read.

    Returns:
        str: A string containing the last 'n' lines of the file,
             decoded as UTF-8 with errors ignored.
    """
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
    """
    Validates a given path to prevent directory traversal and ensure it's within the user_root.

    Args:
        path (str): The path string to validate.
        user_root (str | Path): The root directory against which the path should be validated.

    Returns:
        Path: A resolved and validated Path object if the path is safe.

    Raises:
        ValueError: If the path attempts directory traversal, is a Windows drive path,
                    or resolves outside the user_root.
    """
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

def is_allowed_file_type(file_path: str | Path, allowed_extensions: list[str]) -> bool:
    """
    Checks if the file's extension is in the list of allowed extensions.

    Args:
        file_path (str | Path): The path to the file.
        allowed_extensions (list[str]): A list of allowed file extensions (e.g., [".py", ".txt"]).

    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    file_extension = Path(file_path).suffix.lower()
    return file_extension in [ext.lower() for ext in allowed_extensions]

def check_write_size_limit(content_size: int, max_bytes: int = MAX_RAW_WRITE_SIZE) -> None:
    """
    Checks if the given content size exceeds the maximum allowed write size.

    Args:
        content_size (int): The size of the content to be written, in bytes.
        max_bytes (int): The maximum allowed size for writing, in bytes.
                         Defaults to MAX_RAW_WRITE_SIZE.

    Raises:
        ValueError: If the content size exceeds the maximum allowed bytes.
    """
    if content_size > max_bytes:
        raise ValueError(
            f"Content size ({content_size} bytes) exceeds the maximum allowed write size ({max_bytes} bytes)."
        )

def create_temp_file(user_root: str | Path, suffix: str = "", prefix: str = "tmp_") -> Path:
    """
    Creates a temporary file within the user's root directory.

    The file is created in a way that its path is guaranteed to be within
    the user_root and passes path validation checks.

    Args:
        user_root (str | Path): The root directory where the temporary file should be created.
        suffix (str): The suffix for the temporary file (e.g., '.txt').
        prefix (str): The prefix for the temporary file name (e.g., 'tmp_').

    Returns:
        Path: The path to the created temporary file.

    Raises:
        ValueError: If the temporary file path cannot be validated against the user_root.
    """
    user_root_path = Path(user_root).resolve()
    
    # Use tempfile to get a temporary file path, but ensure it's within user_root
    # tempfile.NamedTemporaryFile creates and opens a file, we just need a path
    # So we'll use mkstemp and immediately close it, then use the path
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=user_root_path)
    os.close(fd) # Close the file descriptor immediately

    temp_file_path = Path(path)
    
    # Validate the path to ensure it's indeed within the user_root, as a double-check
    try:
        validate_path(str(temp_file_path), user_root)
    except ValueError as e:
        # Clean up the created file if validation fails
        if temp_file_path.exists():
            os.remove(temp_file_path)
        raise ValueError(f"Failed to validate temporary file path: {e}") from e

    return temp_file_path

