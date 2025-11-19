from aiogram import Router, F
from aiogram.types import Message
from utils.texts import MENTORS_TEXT

router = Router()

@router.message(F.text == "🧠 Менторы")
async def mentors(message: Message):
    await message.answer(MENTORS_TEXT)
