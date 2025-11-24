# handlers/stats.py

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.logger import get_users, get_leads

router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """
    Простейшая статистика по пользователям и лидам.
    Команда: /stats
    """

    users = get_users()      # словарь {user_id: {...}}
    leads = get_leads()      # словарь {lead_id: {...}}

    total_users = len(users)
    total_leads = len(leads)

    success_leads = sum(1 for l in leads.values() if l.get("status") == "SUCCESS")
    in_progress_leads = sum(1 for l in leads.values() if l.get("status") == "IN_PROGRESS")
    failed_leads = sum(1 for l in leads.values() if l.get("status") == "FAILED")

    text = (
        "📊 <b>Статистика бота</b>\n\n"
        f"👥 Пользователей: <b>{total_users}</b>\n"
        f"📨 Всего лидов: <b>{total_leads}</b>\n\n"
        f"🟢 Успешных: <b>{success_leads}</b>\n"
        f"🟡 В работе: <b>{in_progress_leads}</b>\n"
        f"🔴 Неуспех: <b>{failed_leads}</b>"
    )

    await message.answer(text, parse_mode="HTML")
