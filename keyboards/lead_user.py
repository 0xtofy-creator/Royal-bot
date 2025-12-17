from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def user_lead_menu(lead_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Изменить текст",
                    callback_data=f"user_lead_edit:{lead_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отменить заявку",
                    callback_data=f"user_lead_cancel:{lead_id}"
                ),
            ]
        ]
    )
