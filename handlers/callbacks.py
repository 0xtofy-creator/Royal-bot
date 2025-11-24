from aiogram import Router, F
from aiogram.types import CallbackQuery
from urllib.parse import quote
import random

from keyboards.main_menu import main_menu
from utils.logger import log_lead
from handlers.leads import send_lead_card

router = Router()

TL_LIST = [
    "Royal_Trader_Support_1",
    "Royal_Trader_Support_2",
    "Royal_Trader_Support_3",
    "Royal_Trader_Support_4",
]


# 🔹 1. Подключиться на площадку
@router.callback_query(F.data == "connect")
async def connect(callback: CallbackQuery):
    user = callback.from_user

    assigned_tl = random.choice(TL_LIST)

    # текст для тимлида
    text = "Привет! Хочу подключиться к площадке Royal Finance."
    deep_link = f"https://t.me/{assigned_tl}?text={quote(text)}"

    # лог лидов (в тред)
    lead_id = await log_lead(
        bot=callback.bot,
        user_id=user.id,
        username=f"@{user.username}" if user.username else f"id:{user.id}",
        teamlead=f"@{assigned_tl}",
    )

    await send_lead_card(
        bot=callback.bot,
        lead_id=lead_id,
        user_id=user.id,
        username=f"@{user.username}" if user.username else f"id:{user.id}",
        teamlead=f"@{assigned_tl}",
    )

    # обновление главного меню (edit_message)
    await callback.message.edit_text(
        f"🚀 Для подключения нажмите:\n\n👉 [Открыть чат с тимлидом](<{deep_link}>)",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

    await callback.answer()


# 🔹 2. Актуальный оффер
@router.callback_query(F.data == "offer")
async def offer(callback: CallbackQuery):
    text = (
        "🔥 *Актуальный оффер Royal Finance:*\n\n"
        "*Россия:*\n"
        "• 100–999₽ → *13%*\n"
        "• 1 000–4 999₽ → *9%*\n"
        "• 5 000–9 999₽ → *7.5%*\n"
        "• 10 000₽+ → *6.5%*\n\n"
        "*Азербайджан:*\n"
        "• Приём — *4%*\n"
        "• Вывод — *1%*\n"
        "• Оптимальные суммы: *5 000–30 000₽*\n\n"
        "*Узбекистан:*\n"
        "• Приём — *2%*\n"
        "• Вывод — *1%*\n"
        "• Лучший диапазон чеков: *2 000–12 000₽*"
    )

    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

    await callback.answer()


# 🔹 3. Мануалы
@router.callback_query(F.data == "manuals")
async def manuals(callback: CallbackQuery):

    text = (
        "📚 *Актуальные мануалы:*\n\n"
        "ПСБ\nГазпром\nГазпром армия\nОзон ферма\nОзон озон\n"
        "Альфа Агроферма\nАльфа «в круг»\nТиньк ферма в круг"
    )

    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

    await callback.answer()


# 🔹 4. Тимлиды
@router.callback_query(F.data == "teamleads")
async def teamleads(callback: CallbackQuery):

    text = (
        "👑 *Официальные тимлиды:*\n\n"
        "@Royal_Trader_Support_1\n"
        "@Royal_Trader_Support_2\n"
        "@Royal_Trader_Support_3\n"
        "@Royal_Trader_Support_4"
    )

    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

    await callback.answer()


# 🔹 5. Ментор
@router.callback_query(F.data == "mentor")
async def mentor(callback: CallbackQuery):

    deep = quote("Привет! Нужен мануал для работы.")
    link = f"https://t.me/Royal_mentoringA?text={deep}"

    await callback.message.edit_text(
        f"🧠 Для получения мануала нажмите:\n👉 [Открыть чат](<{link}>)",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

    await callback.answer()
