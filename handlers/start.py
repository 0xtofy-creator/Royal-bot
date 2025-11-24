from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main_menu import main_menu
from utils.logger import save_user_source

router = Router()


@router.message(CommandStart(deep_link=True))
async def start_with_source(message: Message, command: CommandStart):
    """
    Пользователь перешёл по deep-link: /start <source>
    """
    source = command.args or "organic"

    await save_user_source(
        user_id=message.from_user.id,
        username=message.from_user.username,
        source=source
    )

    await message.answer(
        "👋 Привет! Это официальный бот Royal Finance.\n\n"
        "Выбери нужный раздел ниже:",
        reply_markup=main_menu()
    )


@router.message(CommandStart())
async def start_clean(message: Message):
    """
    Пользователь ввёл /start без параметров
    """
    await save_user_source(
        user_id=message.from_user.id,
        username=message.from_user.username,
        source="organic"
    )

    await message.answer(
        "👋 Привет! Это официальный бот Royal Finance.\n\n"
        "Выбери нужный раздел ниже:",
        reply_markup=main_menu()
    )
