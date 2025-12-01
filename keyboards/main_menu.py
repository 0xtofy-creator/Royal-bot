from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Подключиться на площадку", callback_data="connect")],
        [InlineKeyboardButton(text="📰 Royal News", url="https://t.me/Royal_finance_News")],
        [InlineKeyboardButton(text="🔥 Актуальный оффер", callback_data="offer")],
        [InlineKeyboardButton(text="📚 Мануалы", callback_data="manuals")],
        [InlineKeyboardButton(text="👑 Офф. представители", callback_data="teamleads")],
        [InlineKeyboardButton(text="👤 Каналы менторов", callback_data="mentors")],
        [InlineKeyboardButton(text="⚠️ Проблема в работе", callback_data="problem")],
        [InlineKeyboardButton(text="💬 Обратная связь", url="https://t.me/royal_servebot")]
    ])
