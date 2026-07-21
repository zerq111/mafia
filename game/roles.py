from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from i18n import Lang, t


class Team(str, Enum):
    TOWN = "town"
    MAFIA = "mafia"
    NEUTRAL = "neutral"
    AUX = "aux"


class Role(str, Enum):
    CIVILIAN = "civilian"
    DON = "don"
    MAFIA = "mafia"
    COMMISSIONER = "commissioner"
    SERGEANT = "sergeant"
    DOCTOR = "doctor"
    MANIAC = "maniac"
    MISTRESS = "mistress"
    LAWYER = "lawyer"
    SUICIDE = "suicide"
    HOMELESS = "homeless"
    LUCKY = "lucky"
    KAMIKAZE = "kamikaze"


# emoji, team, has_night_action
ROLE_META: dict[Role, tuple[str, Team, bool]] = {
    Role.CIVILIAN: ("👤", Team.TOWN, False),
    Role.DON: ("🤵", Team.MAFIA, True),
    Role.MAFIA: ("😎", Team.MAFIA, True),
    Role.COMMISSIONER: ("🔍", Team.TOWN, True),
    Role.SERGEANT: ("👮", Team.TOWN, False),
    Role.DOCTOR: ("💊", Team.TOWN, True),
    Role.MANIAC: ("🔪", Team.NEUTRAL, True),
    Role.MISTRESS: ("💋", Team.AUX, True),
    Role.LAWYER: ("💼", Team.AUX, True),
    Role.SUICIDE: ("💀", Team.NEUTRAL, False),
    Role.HOMELESS: ("🚶", Team.AUX, True),
    Role.LUCKY: ("🍀", Team.TOWN, False),
    Role.KAMIKAZE: ("💣", Team.TOWN, False),
}


@dataclass(frozen=True)
class RoleInfo:
    role: Role
    emoji: str
    team: Team
    has_night_action: bool = False


ROLE_INFO = {
    role: RoleInfo(role, emoji, team, night)
    for role, (emoji, team, night) in ROLE_META.items()
}


def role_emoji(role: Role) -> str:
    return ROLE_META[role][0]


def role_team(role: Role) -> Team:
    return ROLE_META[role][1]


def has_night_action(role: Role) -> bool:
    return ROLE_META[role][2]


def is_mafia(role: Role) -> bool:
    return role_team(role) == Team.MAFIA


def role_title(role: Role, lang: Lang | str | None = None) -> str:
    return f"{role_emoji(role)} {t(f'role.{role.value}.title', lang)}"


def check_result_label(target_role: Role, protected_by_lawyer: bool, lang: Lang | str) -> str:
    if protected_by_lawyer:
        return t("role.civilian.short", lang)
    if is_mafia(target_role) or target_role in {
        Role.MANIAC,
        Role.COMMISSIONER,
        Role.SERGEANT,
    }:
        return role_title(target_role, lang)
    return t("role.civilian.short", lang)
