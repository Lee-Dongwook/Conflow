import gettext
from contextvars import ContextVar
from functools import lru_cache
from pathlib import Path

LOCALE_DIR = Path(__file__).parent / "locales"
DEFAULT_LOCALE = "ko"
SUPPORTED_LOCALES = ("ko", "en")

# per-request locale (set by middleware)
_current_locale: ContextVar[str] = ContextVar("current_locale", default=DEFAULT_LOCALE)


def get_locale() -> str:
    return _current_locale.get()


def set_locale(locale: str) -> None:
    _current_locale.set(locale)


@lru_cache(maxsize=32)
def get_translator(
    language: str, domain: str = "conflow",
) -> gettext.GNUTranslations | gettext.NullTranslations:
    return gettext.translation(
        domain,
        localedir=LOCALE_DIR,
        languages=[language],
        fallback=True,
    )


def _(message: str) -> str:
    """Translate a message using the current request locale."""
    return get_translator(get_locale()).gettext(message)


def ngettext(singular: str, plural: str, n: int) -> str:
    """Translate singular/plural forms using the current request locale."""
    return get_translator(get_locale()).ngettext(singular, plural, n)


def pgettext(context: str, message: str) -> str:
    """Context-aware translation (msgctxt)."""
    return get_translator(get_locale()).pgettext(context, message)


def parse_accept_language(header: str) -> str:
    """Parse Accept-Language header and return the best matching locale.

    Example: 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7' -> 'ko'
    """
    if not header:
        return DEFAULT_LOCALE

    langs: list[tuple[float, str]] = []
    for part in header.split(","):
        part = part.strip()
        if not part:
            continue
        if ";q=" in part:
            lang, q = part.split(";q=", 1)
            try:
                quality = float(q.strip())
            except ValueError:
                quality = 0.0
        else:
            lang = part
            quality = 1.0
        langs.append((quality, lang.strip()))

    # sort by quality descending
    langs.sort(key=lambda x: x[0], reverse=True)

    for _, lang in langs:
        code = lang.split("-")[0].lower()
        if code in SUPPORTED_LOCALES:
            return code

    return DEFAULT_LOCALE
