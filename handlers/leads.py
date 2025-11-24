from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# Чат лидов
LEADS_CHAT = -1003489617077      # основной чат
LEADS_THREAD = 2                 # тред "Лиды с рекламы"


# Кнопки для карточки лида
def lead_buttons(lead_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔵 Взять в работу", callback_data=f"take_{lead_id}")]
    ])


# Создание карточки лида в группе
async def send_lead_card(bot, lead_id: int, user_id: int, username: str, teamlead: str):

    text = (
        f"🆕 *Новый лид #{lead_id}*\n\n"
        f"*Пользователь:* {username} (id `{user_id}`)\n"
        f"*Назначено тимлиду:* {teamlead}\n"
    )

    await bot.send_message(
        chat_id=LEADS_CHAT,
        message_thread_id=LEADS_THREAD,
        text=text,
        parse_mode="Markdown",
        reply_markup=lead_buttons(lead_id)
    )
