from aiogram import Router, F
from aiogram.types import Message
from utils.texts import TOKEN_TEXT

router = Router()

@router.message(F.text == "🏷 Ввести токен")
async def token_enter(message: Message):
    await message.answer(TOKEN_TEXT)
