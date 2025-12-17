import random

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import TEAMLEADS
from keyboards.main_menu import main_menu
from utils.logger import (
    create_lead,
    get_user_source,
    get_open_lead_for_user,
    cancel_lead,
)
from handlers.leads import send_lead_card

router = Router()


# =====================================================
# FSM
# =====================================================

class LeadFSM(StatesGroup):
    waiting_for_text = State()
    confirm = State()


# =====================================================
# Keyboards
# =====================================================

def kb_cancel_only() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="lead_cancel_fsm")]
        ]
    )


def kb_confirm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Отправить заявку", callback_data="lead_confirm")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="lead_cancel_fsm")],
        ]
    )


def kb_active_lead(lead_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отменить заявку", callback_data=f"lead_user_cancel:{lead_id}")],
            [InlineKeyboardButton(text="⬅️ В меню", callback_data="lead_back_to_menu")],
        ]
    )


# =====================================================
# Helpers
# =====================================================

def status_text(lead: dict) -> str:
    status = lead.get("status")
    return {
        "NEW": "🟡 <b>на рассмотрении</b>",
        "IN_PROGRESS": "🔵 <b>в работе</b>",
        "CANCELLED": "❌ <b>отменена</b>",
        "SUCCESS": "🟢 <b>успех</b>",
        "FAILED": "🔴 <b>неуспех</b>",
    }.get(status, f"<b>{status}</b>")


# =====================================================
# Start FSM
# =====================================================

@router.callback_query(F.data == "connect")
async def connect_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer(cache_time=1)

    user_id = callback.from_user.id
    open_lead = get_open_lead_for_user(user_id)

    if open_lead:
        await callback.message.edit_text(
            "❗ У вас уже есть активная заявка.\n\n"
            f"Номер: <b>#{open_lead['lead_id']}</b>\n"
            f"Статус: {status_text(open_lead)}",
            reply_markup=kb_active_lead(open_lead["lead_id"]),
        )
        return

    await state.clear()
    await state.set_state(LeadFSM.waiting_for_text)

    await callback.message.edit_text(
        "✍️ <b>Опишите заявку</b>\n\n"
        "Отправьте текст, который увидят тимлиды.",
        reply_markup=kb_cancel_only(),
    )


# =====================================================
# Collect text
# =====================================================

@router.message(LeadFSM.waiting_for_text, F.text)
async def collect_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(LeadFSM.confirm)

    await message.answer(
        "📨 <b>Проверьте заявку:</b>\n\n"
        f"{message.text}",
        reply_markup=kb_confirm(),
    )


# =====================================================
# Confirm new lead
# =====================================================

@router.callback_query(F.data == "lead_confirm")
async def confirm_lead(callback: CallbackQuery, state: FSMContext):
    await callback.answer(cache_time=1)

    data = await state.get_data()
    text = data.get("text")

    user = callback.from_user
    username_display = f"@{user.username}" if user.username else f"id:{user.id}"
    source = get_user_source(user.id)

    assigned_tl = f"@{random.choice(TEAMLEADS)}"

    lead_id, lead = create_lead(
        user_id=user.id,
        username_display=username_display,
        source=source,
        assigned_tl=assigned_tl,
        user_comment=text,
    )

    await send_lead_card(callback.bot, lead)
    await state.clear()

    await callback.message.edit_text(
        "✅ <b>Заявка отправлена</b>\n\n"
        f"Номер: <b>#{lead_id}</b>\n"
        "Статус: 🟡 <b>на рассмотрении</b>",
        reply_markup=main_menu(user_id=user.id),
    )


# =====================================================
# User cancel lead
# =====================================================

@router.callback_query(F.data.startswith("lead_user_cancel:"))
async def user_cancel(callback: CallbackQuery):
    await callback.answer(cache_time=1)

    lead_id = int(callback.data.split(":", 1)[1])
    lead = cancel_lead(lead_id, callback.from_user.id)

    if not lead:
        await callback.answer("Лид не найден", show_alert=True)
        return

    await callback.message.edit_text(
        f"❌ <b>Заявка #{lead_id} отменена</b>",
        reply_markup=main_menu(user_id=callback.from_user.id),
    )


# =====================================================
# FSM cancel
# =====================================================

@router.callback_query(F.data == "lead_cancel_fsm")
async def cancel_fsm(callback: CallbackQuery, state: FSMContext):
    await callback.answer(cache_time=1)
    await state.clear()
    await callback.message.edit_text(
        "❌ Действие отменено.",
        reply_markup=main_menu(user_id=callback.from_user.id),
    )


@router.callback_query(F.data == "lead_back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer(cache_time=1)
    await state.clear()
    await callback.message.edit_text(
        "Выберите действие:",
        reply_markup=main_menu(user_id=callback.from_user.id),
    )

