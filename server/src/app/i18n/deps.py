import gettext

from fastapi import Request

from .utils import get_translator, parse_accept_language


def get_translations(request: Request) -> gettext.GNUTranslations | gettext.NullTranslations:
    """FastAPI dependency that returns a translator for the current request.

    Usage:
        @router.get("/example")
        def example(t: gettext.GNUTranslations = Depends(get_translations)):
            return {"message": t.gettext("Hello")}
    """
    accept_language = request.headers.get("accept-language", "")
    locale = parse_accept_language(accept_language)
    return get_translator(locale)
