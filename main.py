from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.controller import GameController
from bot.handlers import actions, group, moderation, private
from config import load_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("mafia")


async def main() -> None:
    settings = load_settings()
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    controller = GameController(bot, settings)

    dp.include_router(private.router)
    dp.include_router(group.router)
    dp.include_router(actions.router)
    dp.include_router(moderation.router)  # last: catches chat spam during game

    me = await bot.get_me()
    logger.info("Bot @%s started", me.username)
    await dp.start_polling(bot, settings=settings, controller=controller)


if __name__ == "__main__":
    asyncio.run(main())
