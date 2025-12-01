# handlers/stats.py

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.logger import get_users, get_leads, get_ad_stats

router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    users = get_users()
    leads = get_leads()

    total_users = len(users)
    total_leads = len(leads)

    success = sum(1 for l in leads.values() if l.get("status") == "SUCCESS")
    in_progress = sum(1 for l in leads.values() if l.get("status") == "IN_PROGRESS")
    failed = sum(1 for l in leads.values() if l.get("status") == "FAILED")

    text = (
        "📊 <b>Статистика бота</b>\n\n"
        f"👥 Пользователей: <b>{total_users}</b>\n"
        f"📨 Всего лидов: <b>{total_leads}</b>\n\n"
        f"🟢 Успешных: <b>{success}</b>\n"
        f"🟡 В работе: <b>{in_progress}</b>\n"
        f"🔴 Неуспех: <b>{failed}</b>"
    )
    await message.answer(text)


@router.message(Command("adstats"))
async def cmd_adstats(message: Message):
    stats = get_ad_stats()
    if not stats:
        await message.answer("Пока нет данных по источникам.")
        return

    total = sum(stats.values())
    lines = ["📊 <b>Источники трафика:</b>"]
    for src, cnt in stats.items():
        lines.append(f"• <code>{src}</code> — <b>{cnt}</b>")
    lines.append(f"\n🧮 Всего: <b>{total}</b>")

    await message.answer("\n".join(lines))
