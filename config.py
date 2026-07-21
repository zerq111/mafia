import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    night_seconds: int = 90
    day_seconds: int = 180
    vote_seconds: int = 60
    confirm_seconds: int = 30
    min_players: int = 4
    max_players: int = 20


def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Укажите BOT_TOKEN в файле .env")

    return Settings(
        bot_token=token,
        night_seconds=int(os.getenv("NIGHT_SECONDS", "90")),
        day_seconds=int(os.getenv("DAY_SECONDS", "180")),
        vote_seconds=int(os.getenv("VOTE_SECONDS", "60")),
        confirm_seconds=int(os.getenv("CONFIRM_SECONDS", "30")),
        min_players=int(os.getenv("MIN_PLAYERS", "4")),
        max_players=int(os.getenv("MAX_PLAYERS", "20")),
    )
