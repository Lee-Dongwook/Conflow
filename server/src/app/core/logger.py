import json
import logging
import os
import sys
import time
from typing import Any
from urllib.parse import parse_qs

from starlette.datastructures import Headers
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from . import shared

logger = shared.logger


def parse_body_content(body_bytes: bytes, content_type: str) -> Any:
    if content_type.startswith("application/json"):
        try:
            return json.loads(body_bytes)
        except Exception:
            return body_bytes.decode("utf-8", errors="ignore")[:1000]
    
    elif content_type.startswith("application/x-www-form-urlencoded"):
        try:
            parsed = parse_qs(body_bytes.decode("utf-8"))
            return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
        except Exception:
            return body_bytes.decode("utf-8", errors="ignore")[:1000]
    
    elif content_type.startswith("multipart/form-data"):
        try:
            boundary = content_type.split("boundary=")[-1].strip()
            if boundary:
                parts = body_bytes.split(f"--{boundary}".encode())
                form_data = {}

                for part in parts[1:-1]:
                    if b"\r\n\r\n" in part:
                        header, content = part.split(b"\r\n\r\n", 1)
                        if b'Content-Disposition' in header:
                            name_match = header.decode("utf-8", errors="ignore")
                            if 'name="' in name_match:
                                name = name_match.split('name="')[1].split('"')[0]

                                if b'filename=' in header:
                                    filename = header.decode("utf-8", errors="ignore").split('filename="')[1].split('"')[0]  # noqa: E501
                                    form_data[name] = f"<file: {filename}>"
                                else:
                                    value = content.rstrip(b"\r\n").decode("utf-8", errors="ignore")
                                    form_data[name] = value

                return form_data if form_data else body_bytes.decode("utf-8", errors="ignore")[:1000]
        except Exception:
            pass
    
        return body_bytes.decode("utf-8", errors="ignore")[:1000]
    
    else:
        return f"<{content_type or 'unknown'} data: {len(body_bytes)} bytes>"

class LoggingMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        logger = shared.logger

        start_time = time.time()

        body_chunks = []

        async def receive_wrapper() -> Message:
            message = await receive()
            if message["type"] == "http.request":
                body = message.get("body", b"")
                if body:
                    body_chunks.append(body)
            return message
        
        status_code: int | None = None

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive_wrapper, send_wrapper)
        
        except Exception as e:
            process_time = round((time.time() - start_time) * 1000)
            log_data: dict[str, Any] = {
                "method": scope["method"],
                "path": scope["path"],
                "error": str(e),
                "process_time_ms": process_time,
            }

            if body_chunks and scope["method"] in ["POST", "PUT", "PATCH"]:
                body_bytes = b"".join(body_chunks)
                headers = Headers(scope=scope)
                content_type = headers.get("content-type", "")
                log_data["body"] = parse_body_content(body_bytes, content_type)
            
            logger.error("Unhandled exception in request", extra=log_data)
            raise
        
        process_time = round((time.time() - start_time) * 1000, 2)

        log_data = {
            "method": scope["method"],
            "path": scope["path"],
            "status_code": status_code,
            "process_time_ms": process_time,
        }


        if body_chunks and scope["method"] in ["POST", "PUT", "PATCH"]:
            body_bytes = b"".join(body_chunks)
            headers = Headers(scope=scope)
            content_type = headers.get("content-type", "")
            log_data["body"] = parse_body_content(body_bytes, content_type)

        if status_code is not None:
            if status_code >= 400:
                logger.error("HTTP request failed", extra=log_data)
            else:
                logger.info("HTTP request", extra=log_data)
        else:
            logger.warning("HTTP request without status code", extra=log_data)


