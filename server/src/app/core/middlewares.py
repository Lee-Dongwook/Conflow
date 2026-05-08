import json
import os
import re
from collections.abc import Callable
from typing import Any

import humps
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .logger import LoggingMiddleware
from .shared import logger

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)  # noqa: E501


def _camelize_key(value: str) -> str:
    """Convert a key to camelCase with safe fallback behavior."""
    camelize_fn = getattr(humps, "camelize", None)
    if callable(camelize_fn):
        return str(camelize_fn(value))

    camel_module = getattr(humps, "camel", None)
    camel_case_fn = getattr(camel_module, "case", None)
    if callable(camel_case_fn):
        return str(camel_case_fn(value))

    normalized_value = re.sub(r"[^0-9A-Za-z]+", "_", value).strip("_")
    if not normalized_value:
        return value

    parts = [part for part in normalized_value.split("_") if part]
    if not parts:
        return value

    first_part = parts[0].lower()
    rest_part = "".join(part[:1].upper() + part[1:] for part in parts[1:])
    return f"{first_part}{rest_part}"


def _decamelize_key(value: str) -> str:
    """Convert a key to snake_case with safe fallback behavior."""
    decamelize_fn = getattr(humps, "decamelize", None)
    if callable(decamelize_fn):
        return str(decamelize_fn(value))

    normalized_value = value.replace("-", "_")
    snake_case = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized_value)
    return snake_case.lower()


def camelize_dict(d: dict | list ) -> dict | list:
    if isinstance(d, dict):
        return {
            (k if _UUID_RE.match(k) else _camelize_key(k)): camelize_dict(v)
            for k, v in d.items()
        }
    elif isinstance(d, list):
        return [camelize_dict(i) for i in d]
    else:
        return d

def decamelize_dict(d: dict | list) -> dict | list:
    if isinstance(d, dict):
        return {
            (k if _UUID_RE.match(k) else _decamelize_key(k)): decamelize_dict(v)
            for k, v in d.items()
        }
    elif isinstance(d, list):
        return [decamelize_dict(i) for i in d]
    else:
        return d

async def handle_request(request: Request) -> Request:
    body_bytes = await request.body()

    if body_bytes:
        try:
          body = json.loads(body_bytes)

          # Check MCP and return
          if isinstance(body, dict) and "jsonrpc" in body:
            return request
          
          snake_case_body = decamelize_dict(body)
          new_body_bytes = json.dumps(snake_case_body).encode("utf-8")

          request._body = new_body_bytes
          request.scope["headers"] = [
            ((k, v) if k.lower() != b"content-length" else (k, str(len(new_body_bytes)).encode()))
            for k, v in request.scope["headers"]
          ]

        except Exception as e:
            logger.error(f"Error decoding JSON: {e}")
    
    return request


def is_swagger_path(path: str) -> bool:
    return path.startswith("/docs") or path.startswith("/openapi.json") or path.startswith("/redoc")


def camelize_properties(schema: dict) -> dict: # noqa: C901
    if not isinstance(schema, dict):
        return schema
    
    if "properties" in schema:
        new_props = {}
        for key, value in schema["properties"].items():
            new_key = _camelize_key(key)
            new_props[new_key] = camelize_properties(value)
        schema["properties"] = new_props

    if "required" in schema and isinstance(schema["required"], list):
        schema["required"] = [_camelize_key(item) for item in schema["required"]]

    if "items" in schema:
        schema["items"] = camelize_properties(schema["items"])
    
    for field in ["allOf", "anyOf", "oneOf"]:
        if field in schema and isinstance(schema[field], list):
            schema[field] = [camelize_properties(item) for item in schema[field]]

    for key, value in list(schema.items()):
        if isinstance(value, dict):
            schema[key] = camelize_properties(value)
        elif isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, dict):
                    new_list.append(camelize_properties(item))
                else:
                    new_list.append(item)
            schema[key] = new_list
    return schema

class CamelCaseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if is_swagger_path(request.url.path):
            return await call_next(request)

        # MCP session ID
        if request.headers.get("mcp-session-id", None):
            return await call_next(request)

        if request.headers.get("content-type", "").startswith("application/json"):
            return await handle_request(request)

        response = await call_next(request)

        if response.headers.get("x-skip-camelize") == "1":
            return response

        if response.headers.get("content-type", "").startswith("application/json"):
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            if not body or body.strip() == b"null":
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                )
            try:
                data = json.loads(body)

                if data is None:
                    return Response(
                        content=body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                    )
                
                camelized_data = camelize_dict(data)
                headers = dict(response.headers.items())

                if "content-length" in headers:
                    del headers["content-length"]

                return JSONResponse(
                    content=camelized_data,
                    status_code=response.status_code,
                    headers=headers
                )
            
            except Exception as e:
                logger.error(f"Error decoding JSON: {e}")
                return response
            
        return response


class ContextRefreshMiddleware:
    def __init__(self, app:ASGIApp) -> None:
        self.app = app
    
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: Message) -> None:
            await send(message)

        await self.app(scope, receive, send_wrapper)

def setup_openapi(app: FastAPI) -> Callable:
    def override_openapi() -> dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
            for schema_name, schema_body in openapi_schema["components"]["schemas"].items():
                openapi_schema["components"]["schemas"][schema_name] = camelize_properties(schema_body)  # noqa: E501

        
        if "paths" in openapi_schema:
            for path in openapi_schema["paths"].values():
                for operation in path.values():
                    if "parameters" in operation:
                        for param in operation["parameters"]:
                            if "schema" in param:
                                param["schema"] = camelize_properties(param["schema"])

                    if "requestBody" in operation and "content" in operation["requestBody"]:
                        for content in operation["requestBody"]["content"].values():
                            if "schema" in content:
                                content["schema"] = camelize_properties(content["schema"])

                    if "responses" in operation:
                        for response in operation["responses"].values():
                            if "content" in response:
                                for content in response["content"].values():
                                    if "schema" in content:
                                        content["schema"] = camelize_properties(content["schema"])

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return override_openapi



def setup_middleware(app: FastAPI) -> None:
    cors_options = dict(
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    default_origins = [
        "http://localhost:5173"
    ]

    env_origins_str = os.environ.get("CORS_ALLOWED_ORIGINS", "")
    env_origins = [origin.strip() for origin in env_origins_str.split(",") if origin.strip()]


    combined_origins = list(dict.fromkeys(default_origins + env_origins))
    os.environ["CORS_ALLOWED_ORIGINS"] = ",".join(combined_origins)

    cors_origins_regex = os.environ.get("CORS_ALLOWED_ORIGINS_REGEX")
    if cors_origins_regex:
        cors_options["allow_origin_regex"] = cors_origins_regex

    app.add_middleware(
        CORSMiddleware,
        allow_origins=combined_origins,
        **cors_options,
    )

    app.add_middleware(ContextRefreshMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(CamelCaseMiddleware)
    app.openapi = setup_openapi(app)
