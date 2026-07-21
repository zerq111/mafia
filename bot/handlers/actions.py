from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.controller import GameController
from bot.keyboards import players_targets_kb
from game.models import Game, Phase, Player
from game.roles import Role
from game.store import get_game, get_user_game
from i18n import get_user_lang, t

router = Router(name="actions")


def _ctx(callback: CallbackQuery) -> tuple[Game | None, Player | None]:
    assert callback.from_user
    game = get_user_game(callback.from_user.id)
    if not game and callback.message and callback.message.chat.type in {"group", "supergroup"}:
        game = get_game(callback.message.chat.id)
    player = game.get(callback.from_user.id) if game else None
    return game, player


async def _deny(callback: CallbackQuery, key: str) -> None:
    assert callback.from_user
    await callback.answer(t(key, get_user_lang(callback.from_user.id)), show_alert=True)


async def _night_pick(
    callback: CallbackQuery,
    controller: GameController,
    *,
    roles: set[Role],
    attr: str,
    done_text_key: str,
    allow_self: bool = False,
) -> None:
    assert callback.from_user and callback.data
    lang = get_user_lang(callback.from_user.id)
    game, player = _ctx(callback)

    if not game or not player or game.phase != Phase.NIGHT or not player.alive:
        await _deny(callback, "cb.not_now")
        return
    if player.role not in roles:
        await _deny(callback, "cb.not_yours")
        return
    if player.blocked_until_day_end:
        await _deny(callback, "cb.mistress")
        return

    target_id = int(callback.data.rsplit(":", 1)[-1])
    target = game.get(target_id)
    if not target or not target.alive:
        await _deny(callback, "cb.bad_target")
        return
    if not allow_self and target_id == player.user_id:
        await _deny(callback, "cb.bad_target")
        return
    if attr == "doctor_target" and target_id == player.user_id and player.doctor_self_used:
        await _deny(callback, "cb.self_heal_used")
        return

    if attr == "mafia":
        game.night_actions.mafia_votes[player.user_id] = target_id
    else:
        setattr(game.night_actions, attr, target_id)

    game.night_actions.done.add(player.user_id)
    ack = "cb.mafia_vote" if attr == "mafia" else "cb.accepted"
    await callback.answer(t(ack, lang))
    if callback.message:
        await callback.message.edit_text(t(done_text_key, lang, name=target.mention()))

    if attr == "mafia":
        await controller.announce_mafia_done(game)
    else:
        await controller.announce_role_wake(game, player.role)
    await controller.maybe_finish_night_early(game)


@router.callback_query(F.data.startswith("night:mafia:"))
async def night_mafia(callback: CallbackQuery, controller: GameController) -> None:
    await _night_pick(
        callback,
        controller,
        roles={Role.DON, Role.MAFIA},
        attr="mafia",
        done_text_key="cb.mafia_voted",
    )


@router.callback_query(F.data.in_({"night:comm:check", "night:comm:shoot"}))
async def night_comm_mode(callback: CallbackQuery) -> None:
    assert callback.from_user and callback.data
    lang = get_user_lang(callback.from_user.id)
    game, player = _ctx(callback)
    if not game or not player or game.phase != Phase.NIGHT or player.role != Role.COMMISSIONER:
        await _deny(callback, "cb.not_now")
        return

    mode = "check" if callback.data.endswith("check") else "shoot"
    game.night_actions.commissioner_mode = mode
    others = [p for p in game.alive() if p.user_id != player.user_id]
    title = t("cb.comm_whom_check" if mode == "check" else "cb.comm_whom_shoot", lang)
    await callback.answer()
    if callback.message:
        await callback.message.edit_text(title, reply_markup=players_targets_kb(others, "night:commtarget"))


@router.callback_query(F.data.startswith("night:commtarget:"))
async def night_comm_target(callback: CallbackQuery, controller: GameController) -> None:
    assert callback.from_user and callback.data
    lang = get_user_lang(callback.from_user.id)
    game, player = _ctx(callback)
    if not game or not player or game.phase != Phase.NIGHT or player.role != Role.COMMISSIONER:
        await _deny(callback, "cb.not_now")
        return
    if not game.night_actions.commissioner_mode:
        await _deny(callback, "cb.pick_action")
        return

    target_id = int(callback.data.rsplit(":", 1)[-1])
    target = game.get(target_id)
    if not target or not target.alive:
        await _deny(callback, "cb.bad_target")
        return

    game.night_actions.commissioner_target = target_id
    game.night_actions.done.add(player.user_id)
    mode = game.night_actions.commissioner_mode
    action = t("cb.comm_check_act" if mode == "check" else "cb.comm_shoot_act", lang)
    await callback.answer(t("cb.accepted", lang))
    if callback.message:
        await callback.message.edit_text(t("cb.comm_done", lang, action=action, name=target.mention()))
    await controller.announce_role_wake(game, Role.COMMISSIONER)
    await controller.maybe_finish_night_early(game)


@router.callback_query(F.data.startswith("night:doctor:"))
async def night_doctor(callback: CallbackQuery, controller: GameController) -> None:
    await _night_pick(
        callback,
        controller,
        roles={Role.DOCTOR},
        attr="doctor_target",
        done_text_key="cb.doctor_done",
        allow_self=True,
    )


@router.callback_query(F.data.startswith("night:maniac:"))
async def night_maniac(callback: CallbackQuery, controller: GameController) -> None:
    await _night_pick(
        callback,
        controller,
        roles={Role.MANIAC},
        attr="maniac_target",
        done_text_key="cb.maniac_done",
    )


@router.callback_query(F.data.startswith("night:mistress:"))
async def night_mistress(callback: CallbackQuery, controller: GameController) -> None:
    await _night_pick(
        callback,
        controller,
        roles={Role.MISTRESS},
        attr="mistress_target",
        done_text_key="cb.mistress_done",
    )


@router.callback_query(F.data.startswith("night:lawyer:"))
async def night_lawyer(callback: CallbackQuery, controller: GameController) -> None:
    await _night_pick(
        callback,
        controller,
        roles={Role.LAWYER},
        attr="lawyer_target",
        done_text_key="cb.lawyer_done",
    )


@router.callback_query(F.data.startswith("night:homeless:"))
async def night_homeless(callback: CallbackQuery, controller: GameController) -> None:
    await _night_pick(
        callback,
        controller,
        roles={Role.HOMELESS},
        attr="homeless_target",
        done_text_key="cb.homeless_done",
    )


@router.callback_query(F.data.startswith("vote:"))
async def vote_action(callback: CallbackQuery, controller: GameController) -> None:
    assert callback.from_user and callback.data
    lang = get_user_lang(callback.from_user.id)
    game, player = _ctx(callback)
    if not game or not player or not player.alive:
        await _deny(callback, "cb.not_in_game")
        return
    if game.phase != Phase.VOTE:
        await _deny(callback, "cb.cant_vote")
        return
    if player.blocked_until_day_end:
        await _deny(callback, "cb.mistress")
        return

    raw = callback.data.rsplit(":", 1)[-1]
    if raw == "skip":
        game.votes[player.user_id] = -1
        await callback.answer(t("cb.abstained", lang))
        if callback.message and callback.message.chat.type == "private":
            await callback.message.edit_text(t("cb.you_abstained", lang))
        await controller.announce_vote(game, player.user_id, -1)
        await controller.maybe_finish_vote_early(game)
        return

    target_id = int(raw)
    target = game.get(target_id)
    if not target or not target.alive or target_id == player.user_id:
        await _deny(callback, "cb.bad_vote")
        return

    game.votes[player.user_id] = target_id
    await callback.answer(t("cb.voted_for", lang, name=target.display()))
    if callback.message and callback.message.chat.type == "private":
        await callback.message.edit_text(t("cb.your_vote", lang, name=target.mention()))
    await controller.announce_vote(game, player.user_id, target_id)
    await controller.maybe_finish_vote_early(game)


@router.callback_query(F.data.in_({"confirm:yes", "confirm:no"}))
async def confirm_action(callback: CallbackQuery, controller: GameController) -> None:
    assert callback.from_user and callback.data
    lang = get_user_lang(callback.from_user.id)
    game, player = _ctx(callback)
    if not game or not player or not player.alive:
        await _deny(callback, "cb.not_in_game")
        return
    if game.phase != Phase.CONFIRM:
        await _deny(callback, "cb.not_now")
        return
    if player.blocked_until_day_end:
        await _deny(callback, "cb.cant_confirm")
        return

    yes = callback.data.endswith("yes")
    game.confirm_votes[player.user_id] = yes
    await callback.answer(t("cb.yes" if yes else "cb.no", lang))
    if callback.message and callback.message.chat.type == "private":
        await callback.message.edit_text(t("btn.yes" if yes else "btn.no", lang))
    await controller.maybe_finish_confirm_early(game)


@router.callback_query(F.data.startswith("kami:"))
async def kamikaze_pick(callback: CallbackQuery, controller: GameController) -> None:
    assert callback.from_user and callback.data
    lang = get_user_lang(callback.from_user.id)
    game, player = _ctx(callback)
    if not game or not player or game.phase != Phase.KAMIKAZE:
        await _deny(callback, "cb.not_now")
        return
    if player.user_id != game.kamikaze_id:
        await _deny(callback, "cb.kami_only")
        return

    target_id = int(callback.data.rsplit(":", 1)[-1])
    target = game.get(target_id)
    await callback.answer(t("cb.picked", lang))
    if callback.message:
        await callback.message.edit_text(
            t("cb.kami_take", lang, name=target.mention() if target else str(target_id))
        )
    await controller.resolve_kamikaze(game, target_id)
