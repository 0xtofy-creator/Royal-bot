# handlers/id.py

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("id"))
async def cmd_id(message: Message):
    chat = message.chat
    user = message.from_user
    thread_id = message.message_thread_id

    text = (
        "ID информация\n\n"
        f"chat_id: {chat.id}\n"
        f"thread_id: {thread_id}\n"
        f"user_id: {user.id}\n"
    )

    await message.answer(text)
