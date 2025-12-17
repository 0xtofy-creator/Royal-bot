import random

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import TEAMLEADS
from states.leads import LeadStates
from utils.logger import (
    create_lead,
    get_open_lead_for_user,
    cancel_lead,
)
from handlers.leads import send_lead_card
from keyboards.lead_user import user_lead_menu

router = Router()


# ——————————————————————————————
# Получение текста заявки
# ——————————————————————————————
@router.message(LeadStates.waiting_for_text)
async def lead_text_handler(message: Message, state: FSMContext):
    user = message.from_user
    text = (message.text or "").strip()

    if len(text) < 5:
        await message.answer("❗ Опишите заявку подробнее.")
        return

    assigned = f"@{random.choice(TEAMLEADS)}"

    lead_id, lead = create_lead(
        user_id=user.id,
        username_display=f"@{user.username}" if user.username else f"id:{user.id}",
        source="organic",
        assigned_tl=assigned,
        user_comment=text,
    )

    await send_lead_card(message.bot, lead)
    await state.clear()

    await message.answer(
        f"✅ <b>Заявка №{lead_id} создана</b>\n\n"
        "📌 Статус: 🕒 На рассмотрении",
        reply_markup=user_lead_menu(lead_id),
    )


# ——————————————————————————————
# Отмена лида пользователем
# ——————————————————————————————
@router.callback_query(F.data.startswith("user_lead_cancel:"))
async def user_cancel_lead(callback: CallbackQuery):
    lead_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    lead = cancel_lead(lead_id, user_id)
    if not lead:
        await callback.answer("Нельзя отменить заявку", show_alert=True)
        return

    await callback.message.edit_text(
        f"❌ <b>Заявка №{lead_id} отменена</b>"
    )
    await callback.answer()


# ——————————————————————————————
# Редактирование текста лида
# ——————————————————————————————
@router.callback_query(F.data.startswith("user_lead_edit:"))
async def user_edit_lead(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    open_lead = get_open_lead_for_user(user_id)
    if not open_lead:
        await callback.answer("Нет активной заявки", show_alert=True)
        return

    await state.set_state(LeadStates.waiting_for_text)

    await callback.message.edit_text(
        "✏️ <b>Введите новый текст заявки</b>\n\n"
        "Он заменит предыдущий."
    )
    await callback.answer()
