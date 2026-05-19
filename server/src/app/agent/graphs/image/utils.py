import asyncio
import logging
import random
import re
import unicodedata
from io import BytesIO
from pathlib import Path
from typing import overload

import cv2
import httpx
import numpy as np
from PIL import Image
from pytesseract import image_to_string

logger = logging.getLogger(__name__)

def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    return text.strip()

async def check_file_size(
    client: httpx.AsyncClient,
    url: str,
    max_bytes: int,
) -> None:
    try:
        response = await client.head(url, timeout=5.0)
        if response.is_success:
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > max_bytes:
                raise ValueError(f"File size exceeds the maximum allowed: {max_bytes} bytes") 
    except ValueError:
        raise
    except Exception as e:
        logger.debug(f"Error checking file size: {e}")

async def stream_download_image(
    client: httpx.AsyncClient,
    url: str,
    max_bytes: int,
    dest_path: str | Path | None = None,
) -> bytes | int:
    total_bytes = 0

    async with client.stream("GET", url) as response:
        response.raise_for_status()

        if dest_path:
            with open(dest_path, "wb") as f:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)
                    total_bytes += len(chunk)
                    if total_bytes > max_bytes:
                        raise ValueError(f"File size exceeds the maximum allowed: {max_bytes} bytes")
            return total_bytes
        else:
            data = bytearray()
            async for chunk in response.aiter_bytes():
                data += chunk
                if len(data) > max_bytes:
                    raise ValueError(f"File size exceeds the maximum allowed: {max_bytes} bytes")
            return bytes(data)

@overload
async def download_image_url(
    file_url: str,
    dest_path: None = None,
    *,
    max_retries: int = ...,
    timeout: float = ...,
    max_size_mega_bytes: int = ...,
) -> bytes: ...

@overload
async def download_image_url(
    file_url: str,
    dest_path: str | Path,
    *,
    max_retries: int = ...,
    timeout: float = ...,
    max_size_mega_bytes: int = ...,
) -> int: ...

async def download_image_url(
    file_url: str,
    dest_path: str | Path | None = None,
    *,
    max_retries: int = 3,
    timeout: float = 30.0,
    max_size_mega_bytes: int = 20,
) -> bytes | int:
    if not file_url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid URL: {file_url}")
    
    max_size_bytes = max_size_mega_bytes * 1024 * 1024
    
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        await check_file_size(client, file_url, max_size_bytes)

        for attempt in range(1, max_retries + 1):
            try:
                log_dest = f"downloaded_image_{attempt}" if dest_path is None else str(dest_path)
                logger.debug(f"[{attempt}/{max_retries}] Downloading image from: {file_url}to: {log_dest}")

                result = await stream_download_image(client, file_url, max_size_bytes, dest_path)
                size = result if isinstance(result, int) else len(result)
                logger.info(f"Downloaded image successfully. Size: {size} bytes")
                return result
            
            except httpx.HTTPStatusError as e:
                if 400 <= e.response.status_code < 500:
                    logger.error(f"Client error {e.response.status_code} - not retrying: {e.response.text}")
                    raise
                logger.warning(f"Server Error {type(e).__name__} - retrying in {2 ** attempt} seconds")
            except (httpx.TimeoutException, httpx.RequestError) as s_e:
                logger.warning(f"{type(s_e).__name__} - retrying in {2 ** attempt} seconds")
            except ValueError:
                raise
        

            if attempt == max_retries:
                raise httpx.HTTPError(f"Max retries reached. Failed to download image.")
            
            delay = min((2 ** (attempt - 1)) + random.uniform(0, 1), 10)
            logger.info(f"Retrying in {delay} seconds...")
            await asyncio.sleep(delay)
    
    raise httpx.HTTPError(f"Max retries reached. Failed to download image.")

async def load_image_from_url(
    file: str | bytes | Image.Image,
) -> Image.Image:
    if isinstance(file, str) and file.startswith(("http://", "https://")):
        byte_file = await download_image_url(file, max_retries=3)
        return Image.open(BytesIO(byte_file))
    
    if isinstance(file, bytes):
        return Image.open(BytesIO(file))
    
    if isinstance(file, str):
        return Image.open(file)
    
    if isinstance(file, Image.Image):
        return file
    
    raise ValueError(f"Unsupported file type: {type(file)}")

def prepare_image_for_ocr(pil_image: Image.Image) -> Image.Image:
    if pil_image.mode not in ("RGB", "L"):
        pil_image = pil_image.convert("RGB")
    
    image = np.array(pil_image)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if pil_image.mode != "L" else image

    denoise_image = cv2.fastNlMeansDenoising(gray, h=10)

    blur_image = cv2.GaussianBlur(denoise_image, (3, 3), 0)

    threshold = cv2.adaptiveThreshold(
        blur_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 15, 3
    )

    kernel = np.ones((2, 2), np.uint8)
    opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)

    return Image.fromarray(opening)


async def extract_text_from_image(
    file: str | bytes | Image.Image,
    lang: str ='eng+kor'
) -> str:
    try:
        pil_image = await load_image_from_url(file)
        processed_image = prepare_image_for_ocr(pil_image)
        text = image_to_string(processed_image, lang=lang)
        return normalize_text(text)
    except Exception as e:
        raise ValueError(f"Error extracting text from image: {e}")
