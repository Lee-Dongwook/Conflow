from starlette.types import ASGIApp, Receive, Scope, Send

from .utils import parse_accept_language, set_locale


class I18nMiddleware:
    """ASGI middleware that sets the request locale from Accept-Language header."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        # extract Accept-Language from raw headers
        accept_language = ""
        for key, value in scope.get("headers", []):
            if key == b"accept-language":
                accept_language = value.decode("latin-1")
                break

        locale = parse_accept_language(accept_language)
        set_locale(locale)

        await self.app(scope, receive, send)
