from __future__ import annotations

import html

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, ChatMemberUpdated, Message

from bot.controller import GameController
from bot.keyboards import lobby_kb
from config import Settings
from game.models import GameMode, Phase, Player
from game.store import bind_user, create_game, end_game, get_game, unbind_user
from i18n import get_chat_lang, get_user_lang, t
from services.chat_control import ensure_bot_admin

router = Router(name="group")


def _player_from_user(user, is_host: bool = False) -> Player:
    return Player(
        user_id=user.id,
        full_name=user.full_name,
        username=user.username,
        is_host=is_host,
    )


def _user_mention(user) -> str:
    return f'<a href="tg://user?id={user.id}">{html.escape(user.full_name)}</a>'


def _lobby_text(game, lang) -> str:
    names = "\n".join(f"• {p.mention()}" for p in game.players.values()) or t("lobby.empty", lang)
    mode = t(f"mode.{game.mode.value}", lang)
    mode_hint = t(f"mode.{game.mode.value}.hint", lang)
    return (
        f"{t('lobby.title', lang)}\n\n"
        f"{t('lobby.mode', lang, mode=mode)}\n"
        f"<i>{mode_hint}</i>\n\n"
        f"{t('lobby.players', lang, n=len(game.players))}\n{names}\n\n"
        f"{t('lobby.hint', lang)}"
    )


def _lobby_markup(game, lang, settings: Settings):
    return (
        _lobby_text(game, lang)
        + "\n\n"
        + t("lobby.need", lang, min=settings.min_players, max=settings.max_players),
        lobby_kb(lang, game.mode.value),
    )


@router.message(Command("game"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_game(message: Message, settings: Settings) -> None:
    assert message.from_user
    lang = get_chat_lang(message.chat.id)
    ok, err_key = await ensure_bot_admin(message.bot, message.chat.id)
    if not ok:
        await message.answer(t(err_key, lang))
        return

    existing = get_game(message.chat.id)
    if existing and existing.phase != Phase.ENDED:
        await message.answer(t("game.already", lang))
        return

    game = create_game(message.chat.id, message.from_user.id)
    player = _player_from_user(message.from_user, is_host=True)
    game.players[player.user_id] = player
    bind_user(player.user_id, game.chat_id)

    text, markup = _lobby_markup(game, lang, settings)
    await message.answer(text, parse_mode="HTML", reply_markup=markup)


@router.message(Command("stop"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_stop(message: Message, controller: GameController) -> None:
    assert message.from_user
    lang = get_chat_lang(message.chat.id)
    game = get_game(message.chat.id)
    if not game:
        await message.answer(t("game.none", lang))
        return

    member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    is_admin = member.status in ("administrator", "creator")
    if message.from_user.id != game.host_id and not is_admin:
        await message.answer(t("game.stop_denied", lang))
        return

    controller.cancel_timer(game)
    from services import chat_control as chat

    await chat.unmute_many(message.bot, game.chat_id, list(game.players.keys()))
    end_game(game.chat_id)
    await message.answer(t("game.stopped", lang))


@router.message(Command("players"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_players(message: Message) -> None:
    lang = get_chat_lang(message.chat.id)
    game = get_game(message.chat.id)
    if not game:
        await message.answer(t("game.no_game", lang))
        return
    if game.phase == Phase.LOBBY:
        await message.answer(_lobby_text(game, lang), parse_mode="HTML")
        return
    alive = ", ".join(p.mention() for p in game.alive()) or "—"
    dead = ", ".join(p.mention() for p in game.dead()) or "—"
    await message.answer(
        t(
            "players.status",
            lang,
            phase=t(f"phase.{game.phase.value}", lang),
            day=game.day_number,
            alive=alive,
            dead=dead,
        ),
        parse_mode="HTML",
    )


@router.message(Command("skip"), F.chat.type.in_({"group", "supergroup"}))
async def cmd_skip(message: Message, controller: GameController) -> None:
    assert message.from_user
    lang = get_chat_lang(message.chat.id)
    game = get_game(message.chat.id)
    if not game or game.phase == Phase.LOBBY:
        await message.answer(t("game.skip_nothing", lang))
        return
    if message.from_user.id != game.host_id:
        await message.answer(t("game.skip_host", lang))
        return

    controller.cancel_timer(game)
    if game.phase == Phase.NIGHT:
        await controller.finish_night(game)
    elif game.phase == Phase.DAY:
        await controller.begin_vote(game)
    elif game.phase == Phase.VOTE:
        await controller.finish_vote(game)
    elif game.phase == Phase.CONFIRM:
        await controller.finish_confirm(game)
    else:
        await message.answer(t("game.skip_denied_phase", lang))


@router.callback_query(F.data == "lobby:join")
async def lobby_join(callback: CallbackQuery, settings: Settings) -> None:
    assert callback.from_user and callback.message
    clang = get_chat_lang(callback.message.chat.id)
    ulang = get_user_lang(callback.from_user.id)
    game = get_game(callback.message.chat.id)
    if not game or game.phase != Phase.LOBBY:
        await callback.answer(t("lobby.no_recruit", ulang), show_alert=True)
        return
    if callback.from_user.id in game.players:
        await callback.answer(t("lobby.already_in", ulang))
        return
    if len(game.players) >= settings.max_players:
        await callback.answer(t("lobby.no_slots", ulang), show_alert=True)
        return

    game.players[callback.from_user.id] = _player_from_user(callback.from_user)
    bind_user(callback.from_user.id, game.chat_id)
    await callback.answer(t("lobby.joined", ulang))
    text, markup = _lobby_markup(game, clang, settings)
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)
    try:
        await callback.bot.send_message(
            callback.from_user.id,
            t(
                "lobby.dm_joined",
                ulang,
                title=callback.message.chat.title or "",
            ),
        )
    except Exception:
        await callback.message.answer(
            t("lobby.open_dm", clang, name=_user_mention(callback.from_user))
        )


@router.callback_query(F.data == "lobby:leave")
async def lobby_leave(callback: CallbackQuery, settings: Settings) -> None:
    assert callback.from_user and callback.message
    clang = get_chat_lang(callback.message.chat.id)
    ulang = get_user_lang(callback.from_user.id)
    game = get_game(callback.message.chat.id)
    if not game or game.phase != Phase.LOBBY:
        await callback.answer(t("lobby.no_recruit", ulang), show_alert=True)
        return
    if callback.from_user.id not in game.players:
        await callback.answer(t("lobby.not_in", ulang))
        return
    if callback.from_user.id == game.host_id:
        await callback.answer(t("lobby.host_cant_leave", ulang), show_alert=True)
        return

    del game.players[callback.from_user.id]
    unbind_user(callback.from_user.id)
    await callback.answer(t("lobby.left", ulang))
    text, markup = _lobby_markup(game, clang, settings)
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)


@router.callback_query(F.data.startswith("lobby:mode:"))
async def lobby_mode(callback: CallbackQuery, settings: Settings) -> None:
    assert callback.from_user and callback.message and callback.data
    clang = get_chat_lang(callback.message.chat.id)
    ulang = get_user_lang(callback.from_user.id)
    game = get_game(callback.message.chat.id)
    if not game or game.phase != Phase.LOBBY:
        await callback.answer(t("lobby.no_recruit", ulang), show_alert=True)
        return
    if callback.from_user.id != game.host_id:
        await callback.answer(t("lobby.host_only_mode", ulang), show_alert=True)
        return

    raw = callback.data.split(":")[-1]
    try:
        game.mode = GameMode(raw)
    except ValueError:
        await callback.answer()
        return

    await callback.answer(t("lobby.mode_set", ulang, mode=t(f"mode.{game.mode.value}", ulang)))
    text, markup = _lobby_markup(game, clang, settings)
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=markup)


@router.callback_query(F.data == "lobby:cancel")
async def lobby_cancel(callback: CallbackQuery) -> None:
    assert callback.from_user and callback.message
    clang = get_chat_lang(callback.message.chat.id)
    ulang = get_user_lang(callback.from_user.id)
    game = get_game(callback.message.chat.id)
    if not game or game.phase != Phase.LOBBY:
        await callback.answer(t("lobby.nothing_cancel", ulang))
        return
    member = await callback.bot.get_chat_member(callback.message.chat.id, callback.from_user.id)
    is_admin = member.status in ("administrator", "creator")
    if callback.from_user.id != game.host_id and not is_admin:
        await callback.answer(t("lobby.host_admin_only", ulang), show_alert=True)
        return
    end_game(game.chat_id)
    await callback.message.edit_text(t("lobby.cancelled", clang))
    await callback.answer()


@router.callback_query(F.data == "lobby:start")
async def lobby_start(callback: CallbackQuery, controller: GameController, settings: Settings) -> None:
    assert callback.from_user and callback.message
    ulang = get_user_lang(callback.from_user.id)
    game = get_game(callback.message.chat.id)
    if not game or game.phase != Phase.LOBBY:
        await callback.answer(t("lobby.no_recruit", ulang), show_alert=True)
        return
    if callback.from_user.id != game.host_id:
        await callback.answer(t("lobby.host_start_only", ulang), show_alert=True)
        return
    if len(game.players) < settings.min_players:
        await callback.answer(
            t("lobby.need_min", ulang, n=settings.min_players),
            show_alert=True,
        )
        return

    await callback.answer(t("lobby.starting", ulang))
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await controller.start_game(game)


@router.my_chat_member()
async def on_my_chat_member(event: ChatMemberUpdated) -> None:
    """Один раз при входе — «сделайте админом»; один раз при выдаче прав — «готово»."""
    from game.store import BOT_STATUS_NOTICE

    me = await event.bot.get_me()
    if event.new_chat_member.user.id != me.id:
        return

    old_status = event.old_chat_member.status
    new_status = event.new_chat_member.status
    chat_id = event.chat.id
    lang = get_chat_lang(chat_id)
    username = me.username or "bot"

    # Удалили / кикнули — сброс, чтобы при повторном добавлении снова поприветствовать
    if new_status in ("left", "kicked"):
        BOT_STATUS_NOTICE.pop(chat_id, None)
        return

    async def _notice(kind: str, key: str, **kwargs) -> None:
        if BOT_STATUS_NOTICE.get(chat_id) == kind:
            return
        BOT_STATUS_NOTICE[chat_id] = kind
        await event.bot.send_message(
            chat_id,
            t(key, lang, **kwargs),
            parse_mode="HTML",
        )

    # Первый заход обычным участником
    if new_status == "member":
        if old_status in ("left", "kicked") or old_status not in ("member", "administrator", "creator"):
            await _notice("need_admin", "bot.need_make_admin", username=username)
        return

    # Стал админом (или обновили права админа)
    if new_status == "administrator":
        can_delete = bool(getattr(event.new_chat_member, "can_delete_messages", False))
        can_restrict = bool(getattr(event.new_chat_member, "can_restrict_members", False))
        if can_delete and can_restrict:
            await _notice("ready", "bot.ready")
        else:
            await _notice("need_rights", "bot.need_rights")
        return
