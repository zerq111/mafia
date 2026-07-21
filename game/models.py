from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from game.roles import Role, is_mafia
from i18n import LocMsg


class Phase(str, Enum):
    LOBBY = "lobby"
    NIGHT = "night"
    DAY = "day"
    VOTE = "vote"
    CONFIRM = "confirm"
    KAMIKAZE = "kamikaze"
    ENDED = "ended"


@dataclass
class Player:
    user_id: int
    full_name: str
    username: str | None = None
    role: Role | None = None
    alive: bool = True
    doctor_self_used: bool = False
    blocked_until_day_end: bool = False
    is_host: bool = False

    def display(self) -> str:
        return self.full_name

    def mention(self) -> str:
        if self.username:
            return f"@{self.username}"
        return f'<a href="tg://user?id={self.user_id}">{self.full_name}</a>'


@dataclass
class NightActions:
    mafia_votes: dict[int, int] = field(default_factory=dict)
    commissioner_mode: str | None = None  # check | shoot
    commissioner_target: int | None = None
    doctor_target: int | None = None
    maniac_target: int | None = None
    mistress_target: int | None = None
    lawyer_target: int | None = None
    done: set[int] = field(default_factory=set)


@dataclass
class DeathEvent:
    victim_id: int
    role: Role
    killer: str  # mafia | maniac | commissioner


@dataclass
class NightReport:
    deaths: list[DeathEvent] = field(default_factory=list)
    saved: list[str] = field(default_factory=list)  # display names
    lucky: list[str] = field(default_factory=list)
    quiet: bool = False
    promotes: list[LocMsg] = field(default_factory=list)
    dms: dict[int, list[LocMsg]] = field(default_factory=dict)
    visits: list[tuple[int, int, str]] = field(default_factory=list)


@dataclass
class Game:
    chat_id: int
    host_id: int
    players: dict[int, Player] = field(default_factory=dict)
    phase: Phase = Phase.LOBBY
    day_number: int = 0
    night_actions: NightActions = field(default_factory=NightActions)
    votes: dict[int, int] = field(default_factory=dict)
    confirm_votes: dict[int, bool] = field(default_factory=dict)
    lynch_candidate: int | None = None
    kamikaze_id: int | None = None
    winners: list[str] = field(default_factory=list)
    phase_task: Any = None
    last_night: NightReport | None = None
    mafia_announced: bool = False

    def get(self, user_id: int) -> Player | None:
        return self.players.get(user_id)

    def alive(self) -> list[Player]:
        return [p for p in self.players.values() if p.alive]

    def dead(self) -> list[Player]:
        return [p for p in self.players.values() if not p.alive]

    def alive_ids(self) -> list[int]:
        return [p.user_id for p in self.alive()]

    def mafia(self) -> list[Player]:
        return [p for p in self.alive() if p.role and is_mafia(p.role)]

    def by_role(self, role: Role) -> Player | None:
        return next((p for p in self.alive() if p.role == role), None)

    def voters(self) -> list[Player]:
        return [p for p in self.alive() if not p.blocked_until_day_end]

    def clear_mistress_blocks(self) -> None:
        for p in self.players.values():
            p.blocked_until_day_end = False

    def reset_night(self) -> None:
        self.night_actions = NightActions()
        self.mafia_announced = False
        self.last_night = None

    def reset_vote(self) -> None:
        self.votes.clear()
        self.confirm_votes.clear()
        self.lynch_candidate = None
        self.kamikaze_id = None
