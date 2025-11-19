from aiogram import Router, F
from aiogram.types import Message
from utils.texts import MANUALS_TEXT

router = Router()

@router.message(F.text == "📚 Мануалы")
async def manuals(message: Message):
    await message.answer(MANUALS_TEXT)
