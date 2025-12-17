from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main_menu import main_menu
from utils.texts import START_TEXT
from utils.logger import log_user_start

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user

    parts = (message.text or "").split(maxsplit=1)
    source = parts[1] if len(parts) > 1 else "organic"

    log_user_start(
        user_id=user.id,
        username=user.username,
        source=source,
    )

    await message.answer(
        START_TEXT,
        reply_markup=main_menu(user_id=user.id)
    )
