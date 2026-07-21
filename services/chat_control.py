from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import ChatPermissions

logger = logging.getLogger(__name__)

MUTE = ChatPermissions(
    can_send_messages=False,
    can_send_audios=False,
    can_send_documents=False,
    can_send_photos=False,
    can_send_videos=False,
    can_send_video_notes=False,
    can_send_voice_notes=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
)

UNMUTE = ChatPermissions(
    can_send_messages=True,
    can_send_audios=True,
    can_send_documents=True,
    can_send_photos=True,
    can_send_videos=True,
    can_send_video_notes=True,
    can_send_voice_notes=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
)


async def safe_delete(bot: Bot, chat_id: int, message_id: int) -> None:
    try:
        await bot.delete_message(chat_id, message_id)
    except (TelegramBadRequest, TelegramForbiddenError):
        pass


async def mute_user(
    bot: Bot,
    chat_id: int,
    user_id: int,
    seconds: int = 60,
    *,
    until_game_end: bool = False,
) -> bool:
    # >366 дней = «навсегда» в Telegram, снимем сами в конце игры
    if until_game_end:
        until = datetime.now(timezone.utc) + timedelta(days=400)
    else:
        until = datetime.now(timezone.utc) + timedelta(seconds=max(35, seconds))
    try:
        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=MUTE,
            until_date=until,
            use_independent_chat_permissions=True,
        )
        return True
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        logger.debug("mute failed %s: %s", user_id, e)
        return False


async def unmute_user(bot: Bot, chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR):
            return True
        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=UNMUTE,
            use_independent_chat_permissions=True,
        )
        return True
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        logger.debug("unmute failed %s: %s", user_id, e)
        return False


async def mute_many(
    bot: Bot,
    chat_id: int,
    user_ids: list[int],
    seconds: int,
    *,
    until_game_end: bool = False,
) -> set[int]:
    muted: set[int] = set()
    for uid in user_ids:
        if await mute_user(bot, chat_id, uid, seconds, until_game_end=until_game_end):
            muted.add(uid)
    return muted


async def unmute_many(bot: Bot, chat_id: int, user_ids: list[int]) -> None:
    for uid in user_ids:
        await unmute_user(bot, chat_id, uid)


async def ensure_bot_admin(bot: Bot, chat_id: int) -> tuple[bool, str]:
    """Возвращает (ok, i18n_key)."""
    me = await bot.get_me()
    try:
        member = await bot.get_chat_member(chat_id, me.id)
    except TelegramBadRequest:
        return False, "bot.check_failed"
    if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR):
        return False, "bot.need_admin"
    can_delete = getattr(member, "can_delete_messages", False)
    can_restrict = getattr(member, "can_restrict_members", False)
    if not can_delete or not can_restrict:
        return False, "bot.need_admin"
    return True, "ok"
