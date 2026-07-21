from __future__ import annotations

from aiogram import F, Router
from aiogram.types import Message

from game.models import Phase
from game.store import get_game
from services.chat_control import mute_user, safe_delete

router = Router(name="moderation")


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def silence_enforcer(message: Message) -> None:
    """Ночью — полная тишина. Днём — мёртвые и заблокированные молчат."""
    if not message.from_user or message.from_user.is_bot:
        return
    # Команды обрабатываются другими хендлерами; здесь только текст/медиа без команд
    if message.text and message.text.startswith("/"):
        return

    game = get_game(message.chat.id)
    if not game or game.phase in (Phase.LOBBY, Phase.ENDED):
        return

    player = game.get(message.from_user.id)
    # Неигроки тоже глушим во время игры
    should_mute = False
    reason_mute_seconds = 45

    if game.phase == Phase.NIGHT:
        should_mute = True
        reason_mute_seconds = 60
    elif player is None:
        should_mute = True
    elif not player.alive:
        should_mute = True
    elif player.blocked_until_day_end and game.phase in (
        Phase.DAY,
        Phase.VOTE,
        Phase.CONFIRM,
    ):
        should_mute = True

    if not should_mute:
        return

    await safe_delete(message.bot, message.chat.id, message.message_id)
    await mute_user(message.bot, message.chat.id, message.from_user.id, reason_mute_seconds)
