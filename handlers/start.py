from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramForbiddenError

from keyboards.main_menu import main_menu
from utils.texts import START_TEXT
from utils.logger import log_user

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    user = message.from_user

    # Логируем пользователя только в ЛС
    if message.chat.type == "private":
        username = f"@{user.username}" if user.username else f"id:{user.id}"
        ref = message.text.replace("/start", "").strip()

        await log_user(
            bot=message.bot,
            user_id=user.id,
            username=username,
            ref=ref
        )

    try:
        await message.answer(
            START_TEXT,
            reply_markup=main_menu()
        )
    except TelegramForbiddenError:
        return
