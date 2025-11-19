from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.texts import JOIN_TEMPLATE
from keyboards.back_menu import back_menu

router = Router()

@router.callback_query(lambda c: c.data == "join")
async def join(callback: CallbackQuery):

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Открыть чат с менеджером", url="https://t.me/placeholder")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")]
    ])

    await callback.message.edit_text(
        JOIN_TEMPLATE.format(
            username=callback.from_user.username,
            user_id=callback.from_user.id
        ),
        reply_markup=kb
    )
