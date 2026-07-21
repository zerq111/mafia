from __future__ import annotations

from aiogram import F, Router
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from bot.keyboards import add_to_group_kb, lang_pick_kb
from i18n import Lang, get_chat_lang, get_user_lang, set_chat_lang, set_user_lang, t

router = Router(name="private")


@router.message(CommandStart(), F.chat.type == "private")
async def cmd_start(message: Message) -> None:
    assert message.from_user
    lang = get_user_lang(message.from_user.id)
    me = await message.bot.get_me()
    await message.answer(
        t("start.welcome", lang),
        parse_mode="HTML",
        reply_markup=add_to_group_kb(me.username or "MafiaBot", lang),
    )


@router.message(Command("help"), F.chat.type == "private")
@router.message(Command("rules"), F.chat.type == "private")
async def cmd_rules_private(message: Message) -> None:
    assert message.from_user
    lang = get_user_lang(message.from_user.id)
    await message.answer(t("rules.text", lang), parse_mode="HTML")


@router.message(Command("lang"), F.chat.type == "private")
async def cmd_lang_private(message: Message) -> None:
    assert message.from_user
    lang = get_user_lang(message.from_user.id)
    await message.answer(
        t("lang.current_private", lang, lang_name=t(f"lang.name.{lang.value}", lang))
        + "\n\n"
        + t("lang.choose_private", lang),
        parse_mode="HTML",
        reply_markup=lang_pick_kb("private"),
    )


@router.message(Command("lang"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_lang_chat(message: Message) -> None:
    assert message.from_user
    clang = get_chat_lang(message.chat.id)
    member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status != ChatMemberStatus.CREATOR:
        # ответ владельцу — на языке чата; отказ — тоже
        ulang = get_user_lang(message.from_user.id)
        await message.answer(t("lang.only_owner", ulang))
        return
    await message.answer(
        t("lang.current_chat", clang, lang_name=t(f"lang.name.{clang.value}", clang))
        + "\n\n"
        + t("lang.choose_chat", clang),
        parse_mode="HTML",
        reply_markup=lang_pick_kb("chat"),
    )


@router.callback_query(F.data == "rules")
async def cb_rules(callback: CallbackQuery) -> None:
    assert callback.from_user
    lang = get_user_lang(callback.from_user.id)
    await callback.answer()
    if callback.message:
        await callback.message.answer(t("rules.text", lang), parse_mode="HTML")


@router.callback_query(F.data == "lang:private")
async def cb_lang_private_menu(callback: CallbackQuery) -> None:
    assert callback.from_user
    lang = get_user_lang(callback.from_user.id)
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            t("lang.choose_private", lang),
            reply_markup=lang_pick_kb("private"),
        )


@router.callback_query(F.data.startswith("setlang:"))
async def cb_set_lang(callback: CallbackQuery) -> None:
    assert callback.from_user and callback.message and callback.data
    # setlang:private:ru | setlang:chat:uk
    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer()
        return
    _, scope, code = parts
    new_lang = Lang.UK if code == "uk" else Lang.RU

    if scope == "private":
        set_user_lang(callback.from_user.id, new_lang)
        await callback.answer()
        await callback.message.answer(
            t(
                "lang.set_private",
                new_lang,
                lang_name=t(f"lang.name.{new_lang.value}", new_lang),
            )
        )
        if callback.message.chat.type == ChatType.PRIVATE:
            me = await callback.bot.get_me()
            try:
                await callback.message.edit_reply_markup(
                    reply_markup=add_to_group_kb(me.username or "MafiaBot", new_lang)
                )
            except Exception:
                pass
        return

    if scope == "chat":
        if callback.message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
            await callback.answer(t("lang.only_owner", get_user_lang(callback.from_user.id)), show_alert=True)
            return
        member = await callback.bot.get_chat_member(
            callback.message.chat.id, callback.from_user.id
        )
        if member.status != ChatMemberStatus.CREATOR:
            await callback.answer(
                t("lang.only_owner", get_user_lang(callback.from_user.id)),
                show_alert=True,
            )
            return
        set_chat_lang(callback.message.chat.id, new_lang)
        await callback.answer()
        await callback.message.answer(
            t(
                "lang.set_chat",
                new_lang,
                lang_name=t(f"lang.name.{new_lang.value}", new_lang),
            )
        )
        return

    await callback.answer()
