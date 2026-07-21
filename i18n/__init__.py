from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Lang(str, Enum):
    RU = "ru"
    UK = "uk"


DEFAULT_LANG = Lang.RU
USER_LANG: dict[int, Lang] = {}
CHAT_LANG: dict[int, Lang] = {}


@dataclass
class LocMsg:
    """Отложенный перевод: ключ + аргументы."""

    key: str
    kwargs: dict[str, Any] = field(default_factory=dict)

    def render(self, lang: Lang | str) -> str:
        return t(self.key, lang, **self.kwargs)


def parse_lang(value: str | Lang | None) -> Lang:
    if isinstance(value, Lang):
        return value
    if value and value.lower().strip() in {"uk", "ua", "ukrainian", "українська", "украинский"}:
        return Lang.UK
    return Lang.RU


def get_user_lang(user_id: int) -> Lang:
    return USER_LANG.get(user_id, DEFAULT_LANG)


def set_user_lang(user_id: int, lang: Lang | str) -> Lang:
    USER_LANG[user_id] = parse_lang(lang)
    return USER_LANG[user_id]


def get_chat_lang(chat_id: int) -> Lang:
    return CHAT_LANG.get(chat_id, DEFAULT_LANG)


def set_chat_lang(chat_id: int, lang: Lang | str) -> Lang:
    CHAT_LANG[chat_id] = parse_lang(lang)
    return CHAT_LANG[chat_id]


def t(key: str, lang: Lang | str | None = None, **kwargs: Any) -> str:
    from i18n.texts import TEXTS

    lang = parse_lang(lang)
    pack = TEXTS.get(lang.value, TEXTS[Lang.RU.value])
    template = pack.get(key) or TEXTS[Lang.RU.value].get(key) or key
    if not kwargs:
        return template

    class _Safe(dict):
        def __missing__(self, name: str) -> str:
            return "{" + name + "}"

    try:
        return template.format_map(_Safe(kwargs))
    except ValueError:
        # битые скобки в шаблоне / значении — подставляем вручную
        out = template
        for name, value in kwargs.items():
            out = out.replace("{" + name + "}", str(value))
        return out
