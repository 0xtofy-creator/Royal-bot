from aiogram import Router, F
from aiogram.types import CallbackQuery
from urllib.parse import quote
import random

from config import TEAMLEADS
from handlers.leads import send_lead_card
from utils.logger import log_lead_created

router = Router()


# 🔹 Подключиться на площадку — сразу переход к тимлиду
@router.callback_query(F.data == "connect")
async def connect(callback: CallbackQuery):
    user = callback.from_user

    # Выбираем рандомного тимлида
    assigned_tl = random.choice(TEAMLEADS)

    # Текст для отправки
    text = "Привет! Хочу подключиться к площадке Royal Finance."
    deep_link = f"https://t.me/{assigned_tl}?text={quote(text)}"

    # Логирование — создаём лид только ПО ПЕРЕХОДУ к ТимЛиду
    lead_id = log_lead_created(
        user_id=user.id,
        username=f"@{user.username}" if user.username else f"id:{user.id}",
        teamlead=f"@{assigned_tl}"
    )

    # Отправляем карточку лидов
    await send_lead_card(
        bot=callback.bot,
        lead_id=lead_id,
        user=f"@{user.username}" if user.username else f"id:{user.id}",
        teamlead=f"@{assigned_tl}"
    )

    # Сам переход — пользователю сразу открывается чат
    await callback.bot.send_message(
        chat_id=user.id,
        text=f"🚀 Для подключения нажмите:\n👉 <a href='{deep_link}'>Открыть чат с тимлидом</a>",
        parse_mode="HTML"
    )

    await callback.answer()
