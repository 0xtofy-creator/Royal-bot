from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import LEADS_CHAT_ID, LEADS_THREAD_ID
from utils.logger import set_lead_status

router = Router()


async def send_lead_card(bot, lead_id, user, teamlead):
    """Отправка карточки нового лида в тред"""

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔵 Взять в работу", callback_data=f"take_{lead_id}")]
    ])

    await bot.send_message(
        chat_id=LEADS_CHAT_ID,
        message_thread_id=LEADS_THREAD_ID,
        text=(
            f"🆕 <b>Новый лид #{lead_id}</b>\n\n"
            f"<b>Пользователь:</b> {user}\n"
            f"<b>Назначен тимлиду:</b> {teamlead}"
        ),
        reply_markup=kb,
        parse_mode="HTML"
    )


# Тимлид нажимает «Взять в работу»
@router.callback_query(lambda c: c.data.startswith("take_"))
async def take_lead(callback):
    lead_id = callback.data.split("_")[1]
    set_lead_status(lead_id, "IN_PROGRESS")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Успех", callback_data=f"done_{lead_id}")],
        [InlineKeyboardButton(text="🔴 Неуспех", callback_data=f"fail_{lead_id}")]
    ])

    await callback.message.edit_text(
        callback.message.text + "\n\n🔵 <b>Статус:</b> В РАБОТЕ",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer("Принято в работу")


# Закрытие лида
@router.callback_query(lambda c: c.data.startswith("done_") or c.data.startswith("fail_"))
async def close_lead(callback):
    lead_id = callback.data.split("_")[1]
    status = "SUCCESS" if callback.data.startswith("done_") else "FAILED"

    set_lead_status(lead_id, status)

    emoji = "🟢 УСПЕХ" if status == "SUCCESS" else "🔴 НЕУСПЕХ"

    await callback.message.edit_text(
        callback.message.text + f"\n\n<b>Результат:</b> {emoji}",
        parse_mode="HTML"
    )
    await callback.answer("Лид закрыт")
