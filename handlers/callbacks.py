import random
from urllib.parse import quote

from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import TEAMLEADS, PROBLEM_CHAT_ID, PROBLEM_THREAD_ID
from keyboards.main_menu import main_menu
from utils.texts import (
    OFFER_TEXT, MANUALS_TEXT, REPRESENTATIVES_TEXT,
    MENTORS_TEXT, PROBLEM_TEXT
)
from utils.logger import create_lead, get_user_source
from handlers.leads import send_lead_card

router = Router()


# ————————————————————————————————————————
# 1. Подключиться на площадку
# ————————————————————————————————————————
@router.callback_query(F.data == "connect")
async def connect(callback: CallbackQuery):
    user = callback.from_user
    username_display = f"@{user.username}" if user.username else f"id:{user.id}"

    source = get_user_source(user.id)

    assigned_username = random.choice(TEAMLEADS)
    assigned_tag = f"@{assigned_username}"

    lead_id, lead = create_lead(
        user_id=user.id,
        username_display=username_display,
        source=source,
        assigned_tl=assigned_tag,
    )

    await send_lead_card(callback.bot, lead)

    text = "Привет! Хочу подключиться к площадке Royal Finance."
    deep_link = f"https://t.me/{assigned_username}?text={quote(text)}"

    await callback.message.edit_text(
        f"🚀 <b>Для подключения нажмите:</b>\n\n"
        f"👉 <a href='{deep_link}'>Открыть чат с тимлидом</a>",
        reply_markup=main_menu()
    )
    await callback.answer()


# ————————————————————————————————————————
# 2. Оффер
# ————————————————————————————————————————
@router.callback_query(F.data == "offer")
async def offer(callback: CallbackQuery):
    await callback.message.edit_text(OFFER_TEXT, reply_markup=main_menu())
    await callback.answer()


# ————————————————————————————————————————
# 3. Мануалы
# ————————————————————————————————————————
@router.callback_query(F.data == "manuals")
async def manuals(callback: CallbackQuery):
    await callback.message.edit_text(MANUALS_TEXT, reply_markup=main_menu())
    await callback.answer()


# ————————————————————————————————————————
# 4. Тимлиды
# ————————————————————————————————————————
@router.callback_query(F.data == "teamleads")
async def teamleads(callback: CallbackQuery):
    await callback.message.edit_text(REPRESENTATIVES_TEXT, reply_markup=main_menu())
    await callback.answer()


# ————————————————————————————————————————
# 5. Каналы менторов
# ————————————————————————————————————————
@router.callback_query(F.data == "mentors")
async def mentors(callback: CallbackQuery):
    await callback.message.edit_text(MENTORS_TEXT, reply_markup=main_menu())
    await callback.answer()


# ————————————————————————————————————————
# 6. Проблема в работе
# ————————————————————————————————————————
@router.callback_query(F.data == "problem")
async def problem(callback: CallbackQuery):
    user = callback.from_user

    # сообщение пользователю
    await callback.message.edit_text(
        PROBLEM_TEXT,
        reply_markup=main_menu()
    )

    # лог в тред 6
    await callback.bot.send_message(
        chat_id=PROBLEM_CHAT_ID,
        message_thread_id=PROBLEM_THREAD_ID,
        text=(
            f"⚠️ <b>Проблема от пользователя</b>\n"
            f"👤 {user.full_name}\n"
            f"🆔 {user.id}\n"
            f"🔗 @{user.username if user.username else '—'}\n\n"
            f"<i>Ожидаем сообщение…</i>"
        )
    )

    await callback.answer()
