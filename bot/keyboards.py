from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from game.models import Player
from i18n import Lang, t


def add_to_group_kb(bot_username: str, lang: Lang) -> InlineKeyboardMarkup:
    url = f"https://t.me/{bot_username}?startgroup=true"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn.add_to_chat", lang), url=url)],
            [
                InlineKeyboardButton(text=t("btn.rules", lang), callback_data="rules"),
                InlineKeyboardButton(text=t("btn.lang", lang), callback_data="lang:private"),
            ],
        ]
    )


def lang_pick_kb(scope: str) -> InlineKeyboardMarkup:
    """scope: private | chat"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("btn.lang_ru", Lang.RU), callback_data=f"setlang:{scope}:ru"),
                InlineKeyboardButton(text=t("btn.lang_uk", Lang.UK), callback_data=f"setlang:{scope}:uk"),
            ]
        ]
    )


def lobby_kb(lang: Lang) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn.join", lang), callback_data="lobby:join")],
            [InlineKeyboardButton(text=t("btn.leave", lang), callback_data="lobby:leave")],
            [InlineKeyboardButton(text=t("btn.start_game", lang), callback_data="lobby:start")],
            [InlineKeyboardButton(text=t("btn.cancel", lang), callback_data="lobby:cancel")],
        ]
    )


def players_targets_kb(
    players: list[Player],
    prefix: str,
    exclude_ids: set[int] | None = None,
    extra_rows: list[list[InlineKeyboardButton]] | None = None,
) -> InlineKeyboardMarkup:
    exclude_ids = exclude_ids or set()
    builder = InlineKeyboardBuilder()
    for p in players:
        if p.user_id in exclude_ids or not p.alive:
            continue
        builder.button(
            text=p.display(),
            callback_data=f"{prefix}:{p.user_id}",
        )
    builder.adjust(1)
    if extra_rows:
        for row in extra_rows:
            builder.row(*row)
    return builder.as_markup()


def commissioner_mode_kb(lang: Lang) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t("btn.check", lang), callback_data="night:comm:check")],
            [InlineKeyboardButton(text=t("btn.shoot", lang), callback_data="night:comm:shoot")],
        ]
    )


def vote_kb(players: list[Player], voter_id: int, lang: Lang) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in players:
        if not p.alive or p.user_id == voter_id:
            continue
        builder.button(text=p.display(), callback_data=f"vote:{p.user_id}")
    builder.button(text=t("btn.abstain", lang), callback_data="vote:skip")
    builder.adjust(1)
    return builder.as_markup()


def go_bot_kb(bot_username: str, lang: Lang, vote: bool = False) -> InlineKeyboardMarkup:
    url = f"https://t.me/{bot_username}"
    text = t("btn.vote" if vote else "btn.go_bot", lang)
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=text, url=url)]]
    )


def confirm_kb(lang: Lang) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("btn.yes", lang), callback_data="confirm:yes"),
                InlineKeyboardButton(text=t("btn.no", lang), callback_data="confirm:no"),
            ]
        ]
    )


def kamikaze_kb(players: list[Player], kamikaze_id: int) -> InlineKeyboardMarkup:
    return players_targets_kb(players, "kami", exclude_ids={kamikaze_id})
