from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from config import LEADS_CHAT_ID, LEADS_THREAD_ID
from utils.logger import set_lead_taken, set_lead_closed, set_lead_leads_message_id, get_lead
from utils.safe_edit import safe_edit_text

router = Router()


def _kb_take(lead_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔵 Взять в работу", callback_data=f"lead_take:{lead_id}")]
        ]
    )


def _kb_close(lead_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🟢 Успех", callback_data=f"lead_success:{lead_id}")],
            [InlineKeyboardButton(text="🔴 Неуспех", callback_data=f"lead_fail:{lead_id}")],
        ]
    )


def _format_lead_text(lead: dict) -> str:
    lid = lead["lead_id"]
    lines = [
        f"🆕 <b>Лид #{lid}</b>",
        "",
        f"<b>Пользователь:</b> {lead['username']}",
        f"<b>Источник:</b> {lead['source']}",
        f"<b>Назначен тимлиду:</b> {lead['assigned_tl']}",
        "",
    ]

    if lead.get("is_repeat") and lead.get("prev_lead_id"):
        prev_status = lead.get("prev_lead_status")
        if prev_status == "SUCCESS":
            result_text = "🟢 УСПЕХ"
        elif prev_status == "FAILED":
            result_text = "🔴 НЕУСПЕХ"
        else:
            result_text = str(prev_status)

        lines.append(
            f"📌 <b>Повторная заявка.</b> Предыдущий лид #{lead['prev_lead_id']} — "
            f"{result_text} ({lead.get('prev_lead_closed_at')})"
        )
        lines.append("")

    if lead.get("user_comment"):
        lines.append(f"💬 <b>Комментарий трейдера:</b> {lead['user_comment']}")
        lines.append("")

    if lead.get("photo_file_id"):
        lines.append("🖼 <b>В заявке есть фото</b>")
        lines.append("")

    status = lead["status"]
    if status == "NEW":
        lines.append("<b>Статус:</b> NEW")
        lines.append(f"🕒 <b>Создан:</b> {lead['created_at']}")
    elif status == "IN_PROGRESS":
        lines.append("🔵 <b>Статус:</b> В РАБОТЕ")
        lines.append(f"👤 <b>Взял:</b> {lead['taken_by_username']}")
        lines.append(f"🕒 <b>Взято:</b> {lead['taken_at']}")
    elif status == "CANCELLED":
        lines.append("❌ <b>Статус:</b> ОТМЕНЁН ПОЛЬЗОВАТЕЛЕМ")
        lines.append(f"🕒 <b>Отменён:</b> {lead['closed_at']}")
    else:
        lines.append("🔚 <b>Статус:</b> ЗАВЕРШЁН")
        result = "🟢 УСПЕХ" if status == "SUCCESS" else "🔴 НЕУСПЕХ"
        lines.append(f"<b>Результат:</b> {result}")
        lines.append(f"👤 <b>Обработал:</b> {lead['closed_by_username']}")
        lines.append(f"🕒 <b>Завершено:</b> {lead['closed_at']}")

    return "\n".join(lines)


async def send_lead_card(bot, lead: dict):
    """
    Отправка карточки лида в чат лидов.
    Если у лида есть photo_file_id — отправляем фото с caption.
    Сохраняем message_id, чтобы потом можно было обновлять карточку.
    """
    text = _format_lead_text(lead)

    if lead.get("photo_file_id"):
        msg = await bot.send_photo(
            chat_id=LEADS_CHAT_ID,
            message_thread_id=LEADS_THREAD_ID,
            photo=lead["photo_file_id"],
            caption=text,
            reply_markup=_kb_take(lead["lead_id"]),
        )
    else:
        msg = await bot.send_message(
            chat_id=LEADS_CHAT_ID,
            message_thread_id=LEADS_THREAD_ID,
            text=text,
            reply_markup=_kb_take(lead["lead_id"]),
        )

    set_lead_leads_message_id(lead["lead_id"], msg.message_id)
    return msg


@router.callback_query(F.data.startswith("lead_take:"))
async def take_lead(callback: CallbackQuery):
    await callback.answer(cache_time=1)

    lead_id = int(callback.data.split(":", 1)[1])
    user = callback.from_user
    staff_username = f"@{user.username}" if user.username else f"id:{user.id}"

    lead = set_lead_taken(lead_id, user.id, staff_username)
    if not lead:
        await callback.answer("Лид не найден", show_alert=True)
        return

    await safe_edit_text(
        callback.message,
        _format_lead_text(lead),
        reply_markup=_kb_close(lead_id)
    )

    try:
        await callback.bot.send_message(
            chat_id=lead["user_id"],
            text=(
                f"🔵 Ваша заявка №{lead_id} взята в работу.\n\n"
                f"Тимлид: {staff_username}"
            ),
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("lead_success:"))
async def success_lead(callback: CallbackQuery):
    await callback.answer(cache_time=1)
    await _close_lead(callback, "SUCCESS")


@router.callback_query(F.data.startswith("lead_fail:"))
async def fail_lead(callback: CallbackQuery):
    await callback.answer(cache_time=1)
    await _close_lead(callback, "FAILED")


async def _close_lead(callback: CallbackQuery, final_status: str):
    lead_id = int(callback.data.split(":", 1)[1])
    user = callback.from_user
    staff_username = f"@{user.username}" if user.username else f"id:{user.id}"

    lead = set_lead_closed(lead_id, user.id, staff_username, final_status)
    if not lead:
        await callback.answer("Лид не найден", show_alert=True)
        return

    await safe_edit_text(callback.message, _format_lead_text(lead), reply_markup=None)

    try:
        text = (
            f"🟢 Ваша заявка №{lead_id} успешно обработана."
            if final_status == "SUCCESS"
            else f"🔴 Ваша заявка №{lead_id} завершена со статусом «Неуспех»."
        )
        await callback.bot.send_message(chat_id=lead["user_id"], text=text)
    except Exception:
        pass


async def refresh_lead_card(bot, lead_id: int):
    """
    Обновить карточку лида в чате лидов (например, если пользователь изменил текст/фото).
    Работает только для message-карточек (send_message). Для фото-карточек Telegram не даст edit_text —
    поэтому делаем edit_caption.
    """
    lead = get_lead(lead_id)
    if not lead:
        return

    msg_id = lead.get("leads_message_id")
    if not msg_id:
        return

    text = _format_lead_text(lead)

    try:
        if lead.get("photo_file_id"):
            await bot.edit_message_caption(
                chat_id=LEADS_CHAT_ID,
                message_thread_id=LEADS_THREAD_ID,
                message_id=msg_id,
                caption=text,
                reply_markup=_kb_take(lead_id) if lead.get("status") == "NEW" else None,
            )
        else:
            await bot.edit_message_text(
                chat_id=LEADS_CHAT_ID,
                message_thread_id=LEADS_THREAD_ID,
                message_id=msg_id,
                text=text,
                reply_markup=_kb_take(lead_id) if lead.get("status") == "NEW" else None,
            )
    except Exception:
        # если сообщение удалили / нет прав / контент не изменился — просто игнорируем
        return
