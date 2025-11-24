from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import LEADS_CHAT_ID, LEADS_THREAD_ID
from utils.logger import set_lead_status

router = Router()


async def send_lead_card(bot, lead_id: str, user: str, teamlead: str, source: str):
    """
    Отправка карточки нового лида в тред "Лиды (заявки)".
    """

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔵 Взять в работу", callback_data=f"take_{lead_id}")]
    ])

    await bot.send_message(
        chat_id=LEADS_CHAT_ID,
        message_thread_id=LEADS_THREAD_ID,
        text=(
            f"🆕 <b>Новый лид #{lead_id}</b>\n\n"
            f"<b>Пользователь:</b> {user}\n"
            f"<b>Источник:</b> {source}\n"
            f"<b>Назначен тимлиду:</b> {teamlead}\n"
            f"<b>Статус:</b> NEW"
        ),
        reply_markup=kb,
        parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data.startswith("take_"))
async def take_lead(callback: CallbackQuery):
    """
    Тимлид жмёт «Взять в работу».
    """
    lead_id = callback.data.split("_", 1)[1]

    set_lead_status(lead_id, "IN_PROGRESS")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Успех", callback_data=f"done_{lead_id}")],
        [InlineKeyboardButton(text="🔴 Неуспех", callback_data=f"fail_{lead_id}")],
    ])

    await callback.message.edit_text(
        callback.message.text + "\n\n🔵 <b>Статус:</b> В РАБОТЕ",
        parse_mode="HTML",
        reply_markup=kb
    )
    await callback.answer("Лид взят в работу")


@router.callback_query(lambda c: c.data.startswith("done_") or c.data.startswith("fail_"))
async def close_lead(callback: CallbackQuery):
    """
    Завершение лида: успех или неуспех.
    """
    lead_id = callback.data.split("_", 1)[1]
    status = "SUCCESS" if callback.data.startswith("done_") else "FAILED"

    set_lead_status(lead_id, status)

    result_text = "🟢 УСПЕХ" if status == "SUCCESS" else "🔴 НЕУСПЕХ"

    await callback.message.edit_text(
        callback.message.text + f"\n\n<b>Результат:</b> {result_text}",
        parse_mode="HTML"
    )
    await callback.answer("Лид закрыт")
