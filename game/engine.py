from __future__ import annotations

import random
from collections import Counter

from game.distribution import distribute_roles
from game.models import DeathEvent, Game, NightReport, Player
from game.roles import (
    ROLE_INFO,
    Role,
    check_result_label,
    has_night_action,
    is_mafia,
    role_title,
)
from i18n import Lang, LocMsg, get_user_lang, t

KILLER_ROLE = {
    "mafia": Role.DON,
    "maniac": Role.MANIAC,
    "commissioner": Role.COMMISSIONER,
}


def assign_roles(game: Game) -> None:
    roles = distribute_roles(len(game.players))
    random.shuffle(roles)
    for player, role in zip(game.players.values(), roles):
        player.role = role
        player.alive = True
        player.doctor_self_used = False
        player.blocked_until_day_end = False


def night_actors_done(game: Game) -> bool:
    actors = [
        p
        for p in game.alive()
        if p.role and has_night_action(p.role) and not p.blocked_until_day_end
    ]
    if not actors:
        return True
    done = game.night_actions.done
    for p in actors:
        if p.user_id not in done:
            return False
    return True


def resolve_mafia_target(game: Game) -> int | None:
    votes = game.night_actions.mafia_votes
    if not votes:
        return None
    counts = Counter(votes.values())
    top = counts.most_common()
    tied = len(top) > 1 and top[0][1] == top[1][1]
    don = game.by_role(Role.DON)
    if tied and don and don.user_id in votes:
        return votes[don.user_id]
    return top[0][0]


def promote_roles(game: Game) -> list[LocMsg]:
    notes: list[LocMsg] = []
    if not any(p.alive and p.role == Role.COMMISSIONER for p in game.players.values()):
        sergeant = game.by_role(Role.SERGEANT)
        if sergeant:
            sergeant.role = Role.COMMISSIONER
            notes.append(LocMsg("pub.promote_comm", {"name": sergeant.display()}))
    if not any(p.alive and p.role == Role.DON for p in game.players.values()):
        mafioso = next((p for p in game.alive() if p.role == Role.MAFIA), None)
        if mafioso:
            mafioso.role = Role.DON
            notes.append(LocMsg("pub.promote_don", {"name": mafioso.display()}))
    return notes


def _dm(report: NightReport, user_id: int, key: str, **kwargs) -> None:
    report.dms.setdefault(user_id, []).append(LocMsg(key, kwargs))


def resolve_night(game: Game) -> NightReport:
    report = NightReport()
    actions = game.night_actions
    alive = {p.user_id: p for p in game.alive()}
    blocked_id: int | None = None

    # Любовница
    mistress = game.by_role(Role.MISTRESS)
    if mistress and actions.mistress_target in alive and actions.mistress_target != mistress.user_id:
        blocked_id = actions.mistress_target
        target = alive[blocked_id]
        target.blocked_until_day_end = True
        report.visits.append((mistress.user_id, blocked_id, "visit.mistress"))
        _dm(report, blocked_id, "priv.mistress_block")
        _dm(report, mistress.user_id, "priv.mistress_ok", name=target.display())

    def blocked(uid: int) -> bool:
        return uid == blocked_id

    # Адвокат
    lawyer = game.by_role(Role.LAWYER)
    lawyer_client: int | None = None
    if lawyer and not blocked(lawyer.user_id) and actions.lawyer_target in alive:
        lawyer_client = actions.lawyer_target
        report.visits.append((lawyer.user_id, lawyer_client, "visit.lawyer"))
        _dm(report, lawyer.user_id, "priv.lawyer_client", name=alive[lawyer_client].display())

    kills: dict[int, str] = {}

    # Мафия
    mafia_ok = [p for p in game.mafia() if not blocked(p.user_id)]
    if mafia_ok:
        actions.mafia_votes = {
            uid: tid for uid, tid in actions.mafia_votes.items() if uid in {p.user_id for p in mafia_ok}
        }
        target_id = resolve_mafia_target(game)
        if target_id in alive:
            kills[target_id] = "mafia"
            actor = next((p for p in mafia_ok if p.role == Role.DON), mafia_ok[0])
            report.visits.append((actor.user_id, target_id, "visit.mafia"))

    # Если убили любовницу — блок снимается
    if mistress and mistress.user_id in kills and blocked_id and blocked_id in alive:
        alive[blocked_id].blocked_until_day_end = False
        blocked_id = None

    # Маньяк
    maniac = game.by_role(Role.MANIAC)
    if maniac and not blocked(maniac.user_id) and actions.maniac_target in alive:
        kills[actions.maniac_target] = "maniac"
        report.visits.append((maniac.user_id, actions.maniac_target, "visit.maniac"))

    # Комиссар
    commissioner = game.by_role(Role.COMMISSIONER)
    sergeant = game.by_role(Role.SERGEANT)
    if commissioner and not blocked(commissioner.user_id) and actions.commissioner_target in alive:
        tid = actions.commissioner_target
        report.visits.append((commissioner.user_id, tid, "visit.commissioner"))
        if actions.commissioner_mode == "shoot":
            kills[tid] = "commissioner"
        elif actions.commissioner_mode == "check":
            target = alive[tid]
            protected = lawyer_client == tid
            for uid in [commissioner.user_id] + ([sergeant.user_id] if sergeant else []):
                lang = get_user_lang(uid)
                label = check_result_label(target.role, protected, lang)  # type: ignore[arg-type]
                key = "priv.comm_check" if uid == commissioner.user_id else "priv.sergeant_check"
                _dm(report, uid, key, name=target.display(), label=label)

    # Доктор
    doctor = game.by_role(Role.DOCTOR)
    healed_id: int | None = None
    if doctor and not blocked(doctor.user_id) and actions.doctor_target in alive:
        tid = actions.doctor_target
        if tid == doctor.user_id and doctor.doctor_self_used:
            _dm(report, doctor.user_id, "priv.doctor_self_used")
        else:
            healed_id = tid
            report.visits.append((doctor.user_id, tid, "visit.doctor"))
            if tid == doctor.user_id:
                doctor.doctor_self_used = True
            _dm(report, doctor.user_id, "priv.doctor_went", name=alive[tid].display())

    # Бомж
    homeless = game.by_role(Role.HOMELESS)
    if homeless and not blocked(homeless.user_id):
        lang = get_user_lang(homeless.user_id)
        lines = []
        for actor_id, target_id, visit_key in report.visits:
            if actor_id == homeless.user_id:
                continue
            target = game.get(target_id)
            if target:
                lines.append(
                    t(
                        "priv.homeless_visit",
                        lang,
                        label=t(visit_key, lang),
                        name=target.display(),
                    )
                )
        if lines:
            _dm(report, homeless.user_id, "priv.homeless_seen", lines="\n".join(lines))
        else:
            _dm(report, homeless.user_id, "priv.homeless_quiet")

    # Смерти
    for target_id, killer in kills.items():
        player = alive.get(target_id)
        if not player or not player.role:
            continue
        if healed_id == target_id:
            report.saved.append(player.display())
            continue
        if player.role == Role.LUCKY and random.random() < 0.45:
            report.lucky.append(player.display())
            continue
        report.deaths.append(DeathEvent(target_id, player.role, killer))
        player.alive = False

    report.quiet = not (report.deaths or report.saved or report.lucky)
    report.promotes = promote_roles(game)
    return report


def tally_votes(game: Game) -> int | None:
    allowed = {p.user_id for p in game.voters()}
    votes = [tid for uid, tid in game.votes.items() if uid in allowed and tid > 0]
    if not votes:
        return None
    top = Counter(votes).most_common()
    if len(top) > 1 and top[0][1] == top[1][1]:
        return None
    return top[0][0]


def confirm_counts(game: Game) -> tuple[int, int]:
    allowed = {p.user_id for p in game.voters()}
    yes = sum(1 for uid, v in game.confirm_votes.items() if uid in allowed and v)
    no = sum(1 for uid, v in game.confirm_votes.items() if uid in allowed and not v)
    return yes, no


def confirm_passed(game: Game) -> bool:
    voters = game.voters()
    if not voters:
        return False
    yes, _ = confirm_counts(game)
    return yes > len(voters) / 2


def check_winners(game: Game) -> list[str]:
    alive = game.alive()
    if not alive:
        return ["win.draw"]

    mafia = [p for p in alive if p.role and is_mafia(p.role)]
    maniac = [p for p in alive if p.role == Role.MANIAC]
    others = len(alive) - len(mafia)

    if maniac and len(alive) == len(maniac):
        return ["win.maniac"]
    if mafia and len(mafia) >= others and not maniac:
        return ["win.mafia"]
    if mafia and maniac and len(mafia) > len(maniac) and len(alive) == len(mafia) + len(maniac):
        return ["win.mafia"]
    if not mafia and not maniac:
        return ["win.town"]
    return []


def apply_lynch(game: Game, victim_id: int) -> tuple[Player | None, list[LocMsg]]:
    victim = game.get(victim_id)
    if not victim or not victim.alive:
        return None, [LocMsg("pub.already_dead")]

    victim.alive = False
    lines = [
        LocMsg(
            "pub.lynch_reveal",
            {"name": victim.display(), "role": victim.role.value if victim.role else "?"},
        )
    ]
    if victim.role == Role.SUICIDE:
        game.winners = ["win.suicide"]
        lines.append(LocMsg("pub.suicide_win"))
    lines.extend(promote_roles(game))
    return victim, lines


def render_lines(lines: list[LocMsg], lang: Lang | str) -> str:
    out = []
    for msg in lines:
        if msg.key == "pub.lynch_reveal" and "role" in msg.kwargs:
            try:
                role = Role(msg.kwargs["role"])
                out.append(
                    t(
                        "pub.lynch_reveal",
                        lang,
                        name=msg.kwargs["name"],
                        role=role_title(role, lang),
                    )
                )
                continue
            except ValueError:
                pass
        out.append(msg.render(lang))
    return "\n".join(out)


def death_text(event: DeathEvent, name: str, lang: Lang | str) -> str:
    killer_role = KILLER_ROLE.get(event.killer)
    killer = role_title(killer_role, lang) if killer_role else event.killer
    return t(
        "pub.death",
        lang,
        role=role_title(event.role, lang),
        name=name,
        killer=killer,
    )


def role_card(player: Player, lang: Lang | str | None = None) -> str:
    assert player.role is not None
    lang = lang or get_user_lang(player.user_id)
    info = ROLE_INFO[player.role]
    return t(
        "role.card",
        lang,
        emoji=info.emoji,
        title=t(f"role.{player.role.value}.title", lang),
        desc=t(f"role.{player.role.value}.desc", lang),
    )


def winners_text(keys: list[str], lang: Lang | str) -> str:
    return ", ".join(t(k, lang) for k in keys)


def format_alive_list(players: list[Player]) -> str:
    return "\n".join(f"{i}. {p.display()}" for i, p in enumerate(players, 1))


def role_composition(players: list[Player], lang: Lang) -> str:
    counts = Counter(p.role for p in players if p.role)
    parts: list[str] = []
    for role, n in (
        (Role.CIVILIAN, counts.get(Role.CIVILIAN, 0)),
        (Role.MAFIA, counts.get(Role.MAFIA, 0)),
    ):
        if n:
            parts.append(f"{role_title(role, lang)} - {n}")
    for role in (
        Role.DON,
        Role.COMMISSIONER,
        Role.SERGEANT,
        Role.DOCTOR,
        Role.MANIAC,
        Role.MISTRESS,
        Role.LAWYER,
        Role.HOMELESS,
        Role.LUCKY,
        Role.KAMIKAZE,
        Role.SUICIDE,
    ):
        n = counts.get(role, 0)
        if n == 1:
            parts.append(role_title(role, lang))
        elif n > 1:
            parts.append(f"{role_title(role, lang)} - {n}")
    return ", ".join(parts)


def sleep_left(seconds: int, lang: Lang) -> str:
    minutes = max(1, (seconds + 59) // 60)
    if minutes == 1:
        return t("night.sleep_left_1", lang)
    return t("night.sleep_left_n", lang, n=minutes)
