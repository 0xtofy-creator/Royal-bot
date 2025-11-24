from aiogram import Router, F
from aiogram.types import CallbackQuery
from urllib.parse import quote
import random

from config import TEAMLEADS
from utils.texts import OFFER_TEXT, MANUALS_TEXT, REPRESENTATIVES_TEXT, MENTORS_TEXT
from utils.logger import log_lead_created, load_json
from keyboards.main_menu import main_menu
from handlers.leads import send_lead_card

# ⬅️ ОБЯЗАТЕЛЬНО: создаём Router ДО декораторов
router = Router()


# 🚀 Подключиться на площадку
@router.callback_query(F.data == "connect")
async def connect(callback: CallbackQuery):
    user = callback.from_user
    username_display = f"@{user.username}" if user.username else f"id:{user.id}"

    assigned_tl = random.choice(TEAMLEADS)

    # deep-link
    text = "Привет! Хочу подключиться к площадке Royal Finance."
    deep_link = f"https://t.me/{assigned_tl}?text={quote(text)}"

    # читаем источник пользователя
    users = load_json("data/users.json")
    source = users.get(str(user.id), {}).get("source", "unknown")

    # логируем лид
    lead_id = log_lead_created(
        user_id=user.id,
        username=user.username,
        teamlead=f"@{assigned_tl}",
        source=source,
    )

    # отправляем карточку лида
    await send_lead_card(
        bot=callback.bot,
        lead_id=lead_id,
        user=username_display,
        teamlead=f"@{assigned_tl}",
        source=source,
    )

    # показываем deep-link
    await callback.message.edit_text(
        f"🚀 <b>Для подключения нажмите:</b>\n\n"
        f"👉 <a href=\"{deep_link}\">Открыть чат с тимлидом</a>",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

    await callback.answer()


# 🔥 Оффер
@router.callback_query(F.data == "offer")
async def offer(callback: CallbackQuery):
    await callback.message.edit_text(
        OFFER_TEXT, parse_mode="HTML", reply_markup=main_menu()
    )
    await callback.answer()


# 📚 Мануалы
@router.callback_query(F.data == "manuals")
async def manuals(callback: CallbackQuery):
    await callback.message.edit_text(
        MANUALS_TEXT, parse_mode="HTML", reply_markup=main_menu()
    )
    await callback.answer()


# 👑 Тимлиды
@router.callback_query(F.data == "teamleads")
async def teamleads(callback: CallbackQuery):
    await callback.message.edit_text(
        REPRESENTATIVES_TEXT, parse_mode="HTML", reply_markup=main_menu()
    )
    await callback.answer()


# 🧠 Ментор
@router.callback_query(F.data == "mentor")
async def mentor(callback: CallbackQuery):
    msg = "Привет! Нужен мануал для работы."
    deep_link = f"https://t.me/Royal_mentoringA?text={quote(msg)}"

    await callback.message.edit_text(
        f"{MENTORS_TEXT}\n\n👉 <a href=\"{deep_link}\">Открыть чат с ментором</a>",
        parse_mode="HTML",
        reply_markup=main_menu()
    )

    await callback.answer()
