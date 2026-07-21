from __future__ import annotations

from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile, InlineKeyboardMarkup, Message

ROOT = Path(__file__).resolve().parent.parent
ASSETS = {
    "sunset": ROOT / "sunset.mp4",
    "sunrise": ROOT / "sunrise.mp4",
}

# file_id cache after first upload
_FILE_IDS: dict[str, str] = {}


async def send_animation(
    bot: Bot,
    chat_id: int,
    kind: str,
    caption: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> Message | None:
    path = ASSETS.get(kind)
    cached = _FILE_IDS.get(kind)
    try:
        if cached:
            return await bot.send_animation(
                chat_id,
                animation=cached,
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
        if path and path.is_file():
            msg = await bot.send_animation(
                chat_id,
                animation=FSInputFile(path),
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
            if msg.animation:
                _FILE_IDS[kind] = msg.animation.file_id
            return msg
    except Exception:
        pass
    # fallback — текст без видео
    return await bot.send_message(
        chat_id,
        caption,
        parse_mode="HTML",
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )
