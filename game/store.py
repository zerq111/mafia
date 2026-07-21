from __future__ import annotations

from game.models import Game

# chat_id -> Game
GAMES: dict[int, Game] = {}

# user_id -> chat_id активной игры
USER_GAME: dict[int, int] = {}

# chat_id -> последний тип уведомления о статусе бота ("need_admin" | "need_rights" | "ready")
BOT_STATUS_NOTICE: dict[int, str] = {}


def get_game(chat_id: int) -> Game | None:
    return GAMES.get(chat_id)


def get_user_game(user_id: int) -> Game | None:
    chat_id = USER_GAME.get(user_id)
    if chat_id is None:
        return None
    return GAMES.get(chat_id)


def create_game(chat_id: int, host_id: int) -> Game:
    game = Game(chat_id=chat_id, host_id=host_id)
    GAMES[chat_id] = game
    return game


def bind_user(user_id: int, chat_id: int) -> None:
    USER_GAME[user_id] = chat_id


def unbind_user(user_id: int) -> None:
    USER_GAME.pop(user_id, None)


def end_game(chat_id: int) -> None:
    game = GAMES.pop(chat_id, None)
    if not game:
        return
    for uid in list(game.players):
        if USER_GAME.get(uid) == chat_id:
            USER_GAME.pop(uid, None)
