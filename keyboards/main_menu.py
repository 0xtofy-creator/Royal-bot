from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS


def main_menu(user_id: int = None) -> InlineKeyboardMarkup:
    """Главное меню. Если user_id — админ, добавляем кнопку админ-панели."""

    buttons = [
        [InlineKeyboardButton(text="🚀 Подключиться на площадку", callback_data="connect")],

        # 🔗 ПРЯМАЯ ССЫЛКА НА КАНАЛ (НЕ callback!)
        [InlineKeyboardButton(
            text="📰 Royal News",
            url="https://t.me/Royal_finance_News"
        )],

        [InlineKeyboardButton(text="🔥 Актуальный оффер", callback_data="offer")],
        [InlineKeyboardButton(text="📚 Мануалы", callback_data="manuals")],
        [InlineKeyboardButton(text="👑 Офф. представители", callback_data="teamleads")],
        [InlineKeyboardButton(text="📡 Каналы менторов", callback_data="mentors")],
        [InlineKeyboardButton(text="⚠️ Проблема в работе", callback_data="problem")],
    ]

    if user_id in ADMIN_IDS:
        buttons.append([
            InlineKeyboardButton(text="👑 Админ-панель", callback_data="admin_open")
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
