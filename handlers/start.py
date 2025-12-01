# handlers/start.py

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main_menu import main_menu
from utils.texts import START_TEXT
from utils.logger import log_user_start
from config import AD_SOURCES_CHAT_ID, AD_SOURCES_THREAD_ID

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user

    # /start или /start source
    parts = (message.text or "").split(maxsplit=1)
    source = parts[1] if len(parts) > 1 else "organic"

    log_user_start(
        user_id=user.id,
        username=user.username,
        source=source,
    )

    # Лог в тред рекламы
    if source != "organic":
        username_display = f"@{user.username}" if user.username else f"id:{user.id}"
        text = (
            "🆕 <b>Новый пользователь из рекламы</b>\n\n"
            f"👤 Пользователь: {username_display}\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"📲 Источник: <code>{source}</code>"
        )
        await message.bot.send_message(
            chat_id=AD_SOURCES_CHAT_ID,
            message_thread_id=AD_SOURCES_THREAD_ID,
            text=text
        )

    await message.answer(START_TEXT, reply_markup=main_menu())
