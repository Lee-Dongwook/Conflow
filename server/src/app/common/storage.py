import asyncio
import logging
import random
from collections.abc import AsyncGenerator
from io import BufferedReader, FileIO
from pathlib import Path
from tempfile import SpooledTemporaryFile

import httpx
from httpx import AsyncByteStream
from supabase import Client

logger = logging.getLogger(__name__)

class AsyncFileStream(AsyncByteStream):
    def __init__(self, file: BufferedReader | FileIO | SpooledTemporaryFile, chunk_size: int = 5_242_880) -> None:  # noqa: E501
        self.file = file
        self.chunk_size = chunk_size
    
    async def __aiter__(self) -> AsyncGenerator[bytes]:
        loop = asyncio.get_running_loop()
        while True:
            chunk = await loop.run_in_executor(None, self.file.read, self.chunk_size)
            if not chunk:
                break
            yield chunk
    
class AsyncBytesStream(AsyncByteStream):
    def __init__(self, data:bytes) -> None:
        self.data = data
    
    async def __aiter__(self) -> AsyncGenerator[bytes]:
        yield self.data
        

class AsyncGeneratorStream(AsyncByteStream):
    def __init__(self, agen: AsyncGenerator[bytes]) -> None:
        self.agen = agen
    
    async def __aiter__(self) -> AsyncGenerator[bytes]:
        async for chunk in self.agen:
            yield chunk
        

async def get_secure_signed_upload_url(supabase_client: Client, bucket_name: str, file_path: str) -> str:
    try:
        response = await supabase_client.storage.from_(bucket_name).create_signed_upload_url(file_path)  # noqa: E501
        return response.get("signedUrl")
    except Exception as e:
        logger.error(f"Failed to get secure signed upload url: {e}")
        raise

async def stream_upload_to_signed_url(
    signed_url: str,
    file_content: BufferedReader | bytes | FileIO | str | Path | SpooledTemporaryFile | AsyncGenerator[bytes],  # noqa: E501
    content_type: str = "application/octet-stream",
    max_retries: int = 3,
    timeout: float = 60.0,
) -> httpx.Response:

    headers = {"Content-Type": content_type}

    upload_stream: AsyncByteStream
    file_to_close = None

    try:
        if isinstance(file_content, bytes):
            upload_stream = AsyncBytesStream(file_content)
        elif isinstance(file_content, AsyncGenerator):
            upload_stream = AsyncGeneratorStream(file_content)
        elif isinstance(file_content, (BufferedReader, FileIO, SpooledTemporaryFile)):
            upload_stream = AsyncFileStream(file_content)
        elif isinstance(file_content, (str, Path)):
            try:
                file_to_close = open(file_content, "rb")
                upload_stream = AsyncFileStream(file_to_close)            
            except FileNotFoundError as e:
                raise ValueError(f"File not found: {e}") from e
        else:
            raise ValueError(f"Unsupported file content type: {type(file_content)}")

        async with httpx.AsyncClient(timeout=timeout) as client:
            for attempt in range(1, max_retries + 1):
                try:
                    logger.debug(f"[{attempt}/{max_retries}] Uploading to signed url: {signed_url}")

                    response = await client.put(
                        signed_url,
                        content=upload_stream,
                        headers=headers,
                    )
                    response.raise_for_status()
                    logger.info(f"Sucessfully uploaded file. Status: {response.status_code}")
                    return response
                
                except (httpx.TimeoutException, httpx.RequestError, httpx.HTTPStatusError) as e:
                    if isinstance(e, httpx.HTTPStatusError) and 400 <= e.response.status_code < 500:
                        logger.error(f"Client error {e.response.status_code} - not retrying: {e.response.text}")  # noqa: E501
                        raise

                    logger.warning(f"{type(e).__name__} - retrying in {2 ** attempt} seconds")
                
                if attempt == max_retries:
                    logger.error(f"Max retries reached. Failed to upload file. Status: {response.status_code}")  # noqa: E501
                    raise httpx.HTTPError(f"Max retries reached. Failed to upload file. Status: {response.status_code}")  # noqa: E501
                
                delay = min((2 ** (attempt -1)) + random.uniform(0, 1), 10)
                logger.warning(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
    finally:
        if file_to_close:
            file_to_close.close()
