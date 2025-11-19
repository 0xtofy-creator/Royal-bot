from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from keyboards.main_menu import main_menu
from utils.texts import WELCOME_TEXT

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(WELCOME_TEXT, reply_markup=main_menu())
