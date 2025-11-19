from aiogram import Router, F
from aiogram.types import Message
from keyboards.main_menu import main_menu

router = Router()

@router.message(F.text == "В меню")
async def back_to_menu(message: Message):
    await message.answer("Главное меню:", reply_markup=main_menu())
