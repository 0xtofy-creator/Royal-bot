# keyboards/main_menu.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Подключиться на площадку", callback_data="connect")],
        [InlineKeyboardButton(text="📰 Royal News", url="https://t.me/Royal_finance_News")],
        [InlineKeyboardButton(text="🔥 Актуальный оффер", callback_data="offer")],
        [InlineKeyboardButton(text="📚 Мануалы", callback_data="manuals")],
        [InlineKeyboardButton(text="👑 Офф. представители / Тимлиды", callback_data="teamleads")],
        [InlineKeyboardButton(text="🧠 Менторы", callback_data="mentor")],
        [InlineKeyboardButton(text="🤖 Бот с предложениями", url="https://t.me/royal_servebot")],
    ])
