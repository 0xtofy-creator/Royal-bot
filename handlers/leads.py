# handlers/leads.py

from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import LEADS_CHAT_ID, LEADS_THREAD_ID
from utils.logger import set_lead_taken, set_lead_closed, get_lead

router = Router()


def _kb_take(lead_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔵 Взять в работу", callback_data=f"lead_take:{lead_id}")]
    ])


def _kb_close(lead_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Успех", callback_data=f"lead_success:{lead_id}")],
        [InlineKeyboardButton(text="🔴 Неуспех", callback_data=f"lead_fail:{lead_id}")]
    ])


def _format_lead_text(lead: dict) -> str:
    lid = lead["lead_id"]
    lines = [
        f"🆕 <b>Новый лид #{lid}</b>",
        "",
        f"<b>Пользователь:</b> {lead['username']}",
        f"<b>Источник:</b> {lead['source']}",
        f"<b>Назначен тимлиду:</b> {lead['assigned_tl']}",
        "",
    ]

    status = lead["status"]

    if status == "NEW":
        lines.append(f"<b>Статус:</b> NEW")
        lines.append(f"🕒 <b>Создан:</b> {lead['created_at']}")
    elif status == "IN_PROGRESS":
        lines.append("🔵 <b>Статус:</b> В РАБОТЕ")
        lines.append(f"👤 <b>Взял:</b> {lead['taken_by_username']}")
        lines.append(f"🕒 <b>Взято:</b> {lead['taken_at']}")
    else:
        lines.append("🔚 <b>Статус:</b> ЗАВЕРШЁН")
        result = "🟢 УСПЕХ" if status == "SUCCESS" else "🔴 НЕУСПЕХ"
        lines.append(f"<b>Результат:</b> {result}")
        lines.append(f"👤 <b>Обработал:</b> {lead['closed_by_username']}")
        lines.append(f"🕒 <b>Завершено:</b> {lead['closed_at']}")

    return "\n".join(lines)


async def send_lead_card(bot, lead: dict):
    text = _format_lead_text(lead)
    msg = await bot.send_message(
        chat_id=LEADS_CHAT_ID,
        message_thread_id=LEADS_THREAD_ID,
        text=text,
        reply_markup=_kb_take(lead["lead_id"])
    )
    return msg


@router.callback_query(F.data.startswith("lead_take:"))
async def take_lead(callback: CallbackQuery):
    lead_id = int(callback.data.split(":", 1)[1])
    user = callback.from_user
    staff_username = f"@{user.username}" if user.username else f"id:{user.id}"

    lead = set_lead_taken(
        lead_id=lead_id,
        staff_id=user.id,
        staff_username=staff_username,
    )
    if not lead:
        await callback.answer("Лид не найден", show_alert=True)
        return

    text = _format_lead_text(lead)
    await callback.message.edit_text(text, reply_markup=_kb_close(lead_id))
    await callback.answer("Лид взят в работу")


@router.callback_query(F.data.startswith("lead_success:"))
async def success_lead(callback: CallbackQuery):
    await _close_lead(callback, final_status="SUCCESS")


@router.callback_query(F.data.startswith("lead_fail:"))
async def fail_lead(callback: CallbackQuery):
    await _close_lead(callback, final_status="FAILED")


async def _close_lead(callback: CallbackQuery, final_status: str):
    lead_id = int(callback.data.split(":", 1)[1])
    user = callback.from_user
    staff_username = f"@{user.username}" if user.username else f"id:{user.id}"

    lead = set_lead_closed(
        lead_id=lead_id,
        staff_id=user.id,
        staff_username=staff_username,
        status=final_status,
    )
    if not lead:
        await callback.answer("Лид не найден", show_alert=True)
        return

    text = _format_lead_text(lead)
    await callback.message.edit_text(text, reply_markup=None)
    await callback.answer("Лид закрыт")
