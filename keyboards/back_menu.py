from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")]
    ])
