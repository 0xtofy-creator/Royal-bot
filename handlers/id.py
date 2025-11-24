# handlers/id.py

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("id"))
async def cmd_id(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = f"chat_id = <code>{chat_id}</code>\nuser_id = <code>{user_id}</code>"
    await message.answer(text, parse_mode="HTML")
