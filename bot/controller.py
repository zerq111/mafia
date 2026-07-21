from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError

from bot import keyboards as kb
from config import Settings
from game.engine import (
    apply_lynch,
    assign_roles,
    check_winners,
    confirm_counts,
    confirm_passed,
    death_text,
    format_alive_list,
    night_actors_done,
    player_left_home,
    promote_roles,
    render_lines,
    resolve_night,
    role_card,
    role_composition,
    sleep_left,
    tally_votes,
    winners_text,
)
from game.models import Game, Phase
from game.roles import Role, is_mafia, role_title
from game.store import end_game
from i18n import get_chat_lang, get_user_lang, t
from services import chat_control as chat
from services.media import send_animation

logger = logging.getLogger(__name__)

# Мут «до конца фазы» vs «до конца игры» (hard)
SOFT_EXTRA = 60

ROLE_WAKE_KEYS: dict[Role, str] = {
    Role.MANIAC: "night.wake.maniac",
    Role.LAWYER: "night.wake.lawyer",
    Role.DOCTOR: "night.wake.doctor",
    Role.COMMISSIONER: "night.wake.commissioner",
    Role.MISTRESS: "night.wake.mistress",
    Role.HOMELESS: "night.wake.homeless",
}


class GameController:
    def __init__(self, bot: Bot, settings: Settings):
        self.bot = bot
        self.settings = settings
        self._username: str | None = None

    async def username(self) -> str:
        if self._username is None:
            me = await self.bot.get_me()
            self._username = me.username or "bot"
        return self._username

    def lang(self, game: Game):
        return get_chat_lang(game.chat_id)

    def cancel_timer(self, game: Game) -> None:
        task = game.phase_task
        game.phase_task = None
        if task and not task.done():
            task.cancel()

    def schedule(self, game: Game, seconds: int, phase: Phase, callback) -> None:
        self.cancel_timer(game)

        async def _run() -> None:
            try:
                await asyncio.sleep(seconds)
                if game.phase == phase:
                    await callback(game)
            except asyncio.CancelledError:
                return

        game.phase_task = asyncio.create_task(_run())

    async def group(self, game: Game, text: str, reply_markup=None) -> None:
        await self.bot.send_message(
            game.chat_id,
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )

    async def dm(self, user_id: int, text: str, reply_markup=None) -> bool:
        try:
            await self.bot.send_message(
                user_id,
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
            )
            return True
        except TelegramForbiddenError:
            return False

    async def mute_eliminated(self, game: Game, *user_ids: int) -> None:
        """В hard — мут до конца игры; в standard — короткий мут фазы."""
        ids = [uid for uid in user_ids if uid]
        if not ids:
            return
        if game.is_hard:
            await chat.mute_many(
                self.bot, game.chat_id, ids, 60, until_game_end=True
            )
        else:
            await chat.mute_many(self.bot, game.chat_id, ids, 120)

    # --- lifecycle ---

    async def start_game(self, game: Game) -> None:
        assign_roles(game)
        game.day_number = 0
        lang = self.lang(game)
        failed: list[str] = []

        for p in game.players.values():
            ul = get_user_lang(p.user_id)
            if not await self.dm(p.user_id, role_card(p, ul)):
                failed.append(p.mention())
            if p.role and is_mafia(p.role):
                mates = [
                    m.mention()
                    for m in game.players.values()
                    if m.user_id != p.user_id and m.role and is_mafia(m.role)
                ]
                if mates:
                    await self.dm(
                        p.user_id,
                        t("game.family", ul, list="\n".join(f"• {n}" for n in mates)),
                    )

        hint = t("game.roles_hint", lang)
        if failed:
            hint += t("game.dm_failed", lang, names=", ".join(failed))
        mode_name = t(f"mode.{game.mode.value}", lang)
        await self.group(
            game,
            t("game.started", lang, n=len(game.players), mode=mode_name, hint=hint),
        )
        await self.begin_night(game)

    async def begin_night(self, game: Game) -> None:
        self.cancel_timer(game)
        game.phase = Phase.NIGHT
        game.day_number += 1
        game.reset_night()
        game.reset_vote()
        game.clear_mistress_blocks()

        seconds = self.settings.night_seconds
        lang = self.lang(game)
        uname = await self.username()

        # Живых — на ночь; мёртвых в hard уже держим до конца игры
        await chat.mute_many(
            self.bot,
            game.chat_id,
            game.alive_ids(),
            seconds + SOFT_EXTRA,
        )
        if game.dead():
            await self.mute_eliminated(game, *[p.user_id for p in game.dead()])

        await send_animation(
            self.bot,
            game.chat_id,
            "sunset",
            t("night.city_sleeps", lang),
            reply_markup=kb.go_bot_kb(uname, lang),
        )

        await self.group(
            game,
            f"{t('night.alive_header', lang)}\n{format_alive_list(game.alive())}\n\n"
            f"{sleep_left(seconds, lang)}",
            reply_markup=kb.go_bot_kb(uname, lang),
        )
        await self._prompt_night(game)
        self.schedule(game, seconds, Phase.NIGHT, self.finish_night)

    async def announce_role_wake(self, game: Game, role: Role | None) -> None:
        """В чат — только после хода роли (не в начале ночи)."""
        if game.phase != Phase.NIGHT or not role:
            return
        key = ROLE_WAKE_KEYS.get(role)
        if not key or role.value in game.wake_announced:
            return
        if not game.by_role(role):
            return
        game.wake_announced.add(role.value)
        await self.group(game, t(key, self.lang(game)))

    async def update_homeless_visit(self, game: Game, *, night_over: bool = False) -> None:
        """Бомж: дома / не дома. Ждём ход цели или рассвет."""
        actions = game.night_actions
        if actions.homeless_informed or not actions.homeless_target:
            return
        homeless = game.by_role(Role.HOMELESS)
        if not homeless or homeless.blocked_until_day_end:
            return
        target = game.get(actions.homeless_target)
        if not target:
            return

        status = player_left_home(game, target, night_over=night_over)
        if status is None:
            return

        actions.homeless_informed = True
        ul = get_user_lang(homeless.user_id)
        key = "priv.homeless_away" if status else "priv.homeless_home"
        await self.dm(homeless.user_id, t(key, ul, name=target.mention()))

    async def announce_mafia_done(self, game: Game) -> None:
        if game.phase != Phase.NIGHT or "mafia" in game.wake_announced:
            return
        mafia = game.mafia()
        if not mafia or not game.night_actions.mafia_votes:
            return
        if not all(p.user_id in game.night_actions.done for p in mafia):
            return
        game.wake_announced.add("mafia")
        await self.group(game, t("night.wake.mafia", self.lang(game)))

    async def maybe_finish_night_early(self, game: Game) -> None:
        if game.phase != Phase.NIGHT:
            return
        await self.update_homeless_visit(game)
        await self.announce_mafia_done(game)
        if night_actors_done(game):
            self.cancel_timer(game)
            await self.finish_night(game)

    async def _prompt_night(self, game: Game) -> None:
        alive = game.alive()
        for p in alive:
            ul = get_user_lang(p.user_id)
            if p.blocked_until_day_end:
                await self.dm(p.user_id, t("night.blocked", ul))
                continue
            if not p.role:
                continue

            others = [x for x in alive if x.user_id != p.user_id]
            if p.role in (Role.DON, Role.MAFIA):
                await self.dm(
                    p.user_id,
                    t("night.mafia_pick", ul),
                    kb.players_targets_kb(others, "night:mafia"),
                )
            elif p.role == Role.COMMISSIONER:
                await self.dm(p.user_id, t("night.comm_mode", ul), kb.commissioner_mode_kb(ul))
            elif p.role == Role.DOCTOR:
                extra = t(
                    "night.doctor_self_ok" if not p.doctor_self_used else "night.doctor_self_no",
                    ul,
                )
                exclude = {p.user_id} if p.doctor_self_used else set()
                await self.dm(
                    p.user_id,
                    t("night.doctor_pick", ul, extra=extra),
                    kb.players_targets_kb(alive, "night:doctor", exclude_ids=exclude),
                )
            elif p.role == Role.MANIAC:
                await self.dm(
                    p.user_id,
                    t("night.maniac_pick", ul),
                    kb.players_targets_kb(others, "night:maniac"),
                )
            elif p.role == Role.MISTRESS:
                await self.dm(
                    p.user_id,
                    t("night.mistress_pick", ul),
                    kb.players_targets_kb(others, "night:mistress"),
                )
            elif p.role == Role.LAWYER:
                await self.dm(
                    p.user_id,
                    t("night.lawyer_pick", ul),
                    kb.players_targets_kb(others, "night:lawyer"),
                )
            elif p.role == Role.HOMELESS:
                await self.dm(
                    p.user_id,
                    t("night.homeless_pick", ul),
                    kb.players_targets_kb(others, "night:homeless"),
                )
            elif p.role == Role.SERGEANT:
                await self.dm(p.user_id, t("night.sergeant", ul))

    async def finish_night(self, game: Game) -> None:
        if game.phase != Phase.NIGHT:
            return
        await self.update_homeless_visit(game, night_over=True)
        report = resolve_night(game)
        game.last_night = report

        for uid, messages in report.dms.items():
            ul = get_user_lang(uid)
            for msg in messages:
                await self.dm(uid, msg.render(ul))

        winners = check_winners(game)
        await self.begin_day(game, finish_with=winners or None)

    async def begin_day(self, game: Game, finish_with: list[str] | None = None) -> None:
        self.cancel_timer(game)
        game.phase = Phase.DAY
        lang = self.lang(game)
        seconds = self.settings.day_seconds
        report = game.last_night

        unmute = [p.user_id for p in game.players.values() if p.alive and not p.blocked_until_day_end]
        soft_mute = [p.user_id for p in game.players.values() if p.alive and p.blocked_until_day_end]
        dead_ids = [p.user_id for p in game.dead()]

        await chat.unmute_many(self.bot, game.chat_id, unmute)
        soft_seconds = seconds + self.settings.vote_seconds + SOFT_EXTRA
        if soft_mute:
            await chat.mute_many(self.bot, game.chat_id, soft_mute, soft_seconds)
        if dead_ids:
            if game.is_hard:
                await chat.mute_many(
                    self.bot, game.chat_id, dead_ids, 60, until_game_end=True
                )
            else:
                await chat.mute_many(self.bot, game.chat_id, dead_ids, soft_seconds)

        await send_animation(
            self.bot,
            game.chat_id,
            "sunrise",
            t("day.sunrise", lang, n=game.day_number),
        )

        if report:
            for event in report.deaths:
                victim = game.get(event.victim_id)
                name = victim.mention() if victim else str(event.victim_id)
                await self.group(game, death_text(event, name, lang))
            for name in report.saved:
                await self.group(game, t("pub.saved", lang, name=name))
            for name in report.lucky:
                await self.group(game, t("pub.lucky", lang, name=name))
            if report.quiet:
                await self.group(game, t("pub.quiet", lang))
            for msg in report.promotes:
                await self.group(game, msg.render(lang))

        if finish_with:
            await self.finish_game(game, finish_with)
            return

        blocked = [p for p in game.alive() if p.blocked_until_day_end]
        blocked_note = (
            t("day.blocked", lang, names=", ".join(p.mention() for p in blocked)) if blocked else ""
        )
        alive = game.alive()
        await self.group(
            game,
            t(
                "day.discuss",
                lang,
                alive_block=f"{t('day.alive_header', lang)}\n{format_alive_list(alive)}",
                composition=role_composition(alive, lang),
                total=len(alive),
                blocked=blocked_note,
            ),
        )
        self.schedule(game, seconds, Phase.DAY, self.begin_vote)

    async def begin_vote(self, game: Game) -> None:
        self.cancel_timer(game)
        game.phase = Phase.VOTE
        game.votes.clear()
        seconds = self.settings.vote_seconds
        lang = self.lang(game)

        await self.group(
            game,
            t("vote.start", lang, seconds=seconds),
            reply_markup=kb.go_bot_kb(await self.username(), lang, vote=True),
        )
        for p in game.alive():
            ul = get_user_lang(p.user_id)
            if p.blocked_until_day_end:
                await self.dm(p.user_id, t("vote.cant", ul))
                continue
            await self.dm(
                p.user_id,
                t("vote.dm", ul),
                kb.vote_kb(game.alive(), p.user_id, ul),
            )
        self.schedule(game, seconds, Phase.VOTE, self.finish_vote)

    async def announce_vote(self, game: Game, voter_id: int, target_id: int) -> None:
        voter = game.get(voter_id)
        if not voter:
            return
        lang = self.lang(game)
        if target_id < 0:
            await self.group(game, t("vote.cast_skip", lang, voter=voter.mention()))
            return
        target = game.get(target_id)
        if target:
            await self.group(
                game,
                t("vote.cast", lang, voter=voter.mention(), target=target.mention()),
            )

    async def maybe_finish_vote_early(self, game: Game) -> None:
        if game.phase != Phase.VOTE:
            return
        voters = game.voters()
        if voters and all(p.user_id in game.votes for p in voters):
            self.cancel_timer(game)
            await self.finish_vote(game)

    async def finish_vote(self, game: Game) -> None:
        if game.phase != Phase.VOTE:
            return
        lang = self.lang(game)
        candidate = tally_votes(game)
        if candidate is None:
            await self.group(game, t("vote.tie", lang))
            await self.begin_night(game)
            return

        victim = game.get(candidate)
        if not victim:
            await self.begin_night(game)
            return

        game.lynch_candidate = candidate
        game.confirm_votes.clear()
        game.phase = Phase.CONFIRM
        seconds = self.settings.confirm_seconds

        await self.group(
            game,
            t("confirm.start", lang, name=victim.mention()),
            reply_markup=kb.confirm_kb(lang),
        )
        for p in game.voters():
            ul = get_user_lang(p.user_id)
            await self.dm(
                p.user_id,
                t("confirm.dm", ul, name=victim.mention()),
                kb.confirm_kb(ul),
            )
        self.schedule(game, seconds, Phase.CONFIRM, self.finish_confirm)

    async def maybe_finish_confirm_early(self, game: Game) -> None:
        if game.phase != Phase.CONFIRM:
            return
        voters = game.voters()
        if voters and all(p.user_id in game.confirm_votes for p in voters):
            self.cancel_timer(game)
            await self.finish_confirm(game)

    async def finish_confirm(self, game: Game) -> None:
        if game.phase != Phase.CONFIRM:
            return
        lang = self.lang(game)
        candidate = game.lynch_candidate
        yes, no = confirm_counts(game)
        victim = game.get(candidate) if candidate else None

        if not victim or not confirm_passed(game):
            await self.group(
                game,
                t("confirm.failed", lang, yes=yes, no=no, name=victim.mention() if victim else "?"),
            )
            await self.begin_night(game)
            return

        await self.group(
            game,
            t("confirm.results", lang, yes=yes, no=no, name=victim.mention()),
        )

        if victim.role == Role.KAMIKAZE:
            game.phase = Phase.KAMIKAZE
            game.kamikaze_id = victim.user_id
            _, lines = apply_lynch(game, candidate)  # type: ignore[arg-type]
            await self.mute_eliminated(game, victim.user_id)
            await self.group(game, render_lines(lines, lang))
            if game.winners:
                await self.finish_game(game, game.winners)
                return
            await self.group(game, t("kamikaze.announce", lang, name=victim.mention()))
            ul = get_user_lang(victim.user_id)
            await self.dm(
                victim.user_id,
                t("kamikaze.dm", ul),
                kb.kamikaze_kb(game.alive(), victim.user_id),
            )
            self.schedule(game, 30, Phase.KAMIKAZE, self._kamikaze_timeout)
            return

        _, lines = apply_lynch(game, candidate)  # type: ignore[arg-type]
        await self.mute_eliminated(game, victim.user_id)
        await self.group(game, render_lines(lines, lang))
        if game.winners:
            await self.finish_game(game, game.winners)
            return
        winners = check_winners(game)
        if winners:
            await self.finish_game(game, winners)
            return
        await self.begin_night(game)

    async def _kamikaze_timeout(self, game: Game) -> None:
        await self.group(game, t("kamikaze.none", self.lang(game)))
        winners = check_winners(game)
        if winners:
            await self.finish_game(game, winners)
        else:
            await self.begin_night(game)

    async def resolve_kamikaze(self, game: Game, target_id: int) -> None:
        if game.phase != Phase.KAMIKAZE:
            return
        self.cancel_timer(game)
        lang = self.lang(game)
        target = game.get(target_id)
        if not target or not target.alive:
            await self.begin_night(game)
            return

        target.alive = False
        await self.mute_eliminated(game, target.user_id)
        notes = promote_roles(game)
        role = role_title(target.role, lang) if target.role else "?"
        text = t("kamikaze.took", lang, name=target.mention(), role=role)
        if notes:
            text += "\n" + "\n".join(n.render(lang) for n in notes)
        await self.group(game, text)

        winners = check_winners(game)
        if winners:
            await self.finish_game(game, winners)
        else:
            await self.begin_night(game)

    async def finish_game(self, game: Game, winners: list[str]) -> None:
        self.cancel_timer(game)
        game.phase = Phase.ENDED
        game.winners = winners
        lang = self.lang(game)

        await chat.unmute_many(self.bot, game.chat_id, list(game.players.keys()))

        lines = [t("game.over", lang, winners=winners_text(winners, lang))]
        for p in game.players.values():
            status = "💀" if not p.alive else "✅"
            role = role_title(p.role, lang) if p.role else "?"
            lines.append(
                t("game.over.role_line", lang, status=status, name=p.mention(), role=role)
            )
        await self.group(game, "\n".join(lines))
        end_game(game.chat_id)
