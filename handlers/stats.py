# handlers/stats.py

import json
import os
from datetime import datetime, timedelta
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

DATA_DIR = "data"


def load_json(filename: str):
    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    return [json.loads(line) for line in lines if line.strip()]


def count_today(entries):
    today = datetime.now().date()
    return [e for e in entries if datetime.fromisoformat(e["timestamp"]).date() == today]


def count_week(entries):
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    return [
        e for e in entries
        if week_ago <= datetime.fromisoformat(e["timestamp"]).date() <= today
    ]


def top_teamleads(leads_new):
    result = {}
    for lead in leads_new:
        tl = lead.get("assigned_teamlead", "unknown")
        result[tl] = result.get(tl, 0) + 1
    return result


def top_sources(users):
    result = {}
    for e in users:
        source = e.get("ref", "") or "unknown"
        result[source] = result.get(source, 0) + 1
    return result


@router.message(Command("stats"))
async def stats(message: Message):
    """ Главная команда статистики """

    args = message.text.split()

    users = load_json("users.json")
    leads_all = load_json("leads.json")
    events = load_json("events.json")

    # Только новые лиды (lead_new)
    leads_new = [l for l in leads_all if l.get("event") == "lead_new"]

    if len(args) == 1:
        await message.answer(
            "📊 *Статистика*\n\n"
            "Доступные команды:\n"
            "• `/stats today` — за сегодня\n"
            "• `/stats week` — за неделю\n"
            "• `/stats leads` — лиды\n"
            "• `/stats teamleads` — эффективность тимлидов\n"
            "• `/stats sources` — источники рекламы",
            parse_mode="Markdown"
        )
        return

    cmd = args[1]

    # /stats today
    if cmd == "today":
        users_today = count_today(users)
        leads_today = count_today(leads_new)

        conv = (len(leads_today) / len(users_today) * 100) if users_today else 0

        await message.answer(
            "📆 *Статистика за сегодня*\n\n"
            f"👤 Новые пользователи: *{len(users_today)}*\n"
            f"📥 Лиды: *{len(leads_today)}*\n"
            f"📈 Конверсия: *{conv:.1f}%*",
            parse_mode="Markdown"
        )
        return

    # /stats week
    if cmd == "week":
        users_week = count_week(users)
        leads_week = count_week(leads_new)

        conv = (len(leads_week) / len(users_week) * 100) if users_week else 0

        await message.answer(
            "📆 *Статистика за неделю*\n\n"
            f"👤 Новые пользователи: *{len(users_week)}*\n"
            f"📥 Лиды: *{len(leads_week)}*\n"
            f"📈 Конверсия: *{conv:.1f}%*",
            parse_mode="Markdown"
        )
        return

    # /stats leads
    if cmd == "leads":
        text_lines = []
        for lead in leads_new[-20:]:
            lead_id = lead.get("lead_id")
            username = lead.get("username", "—")
            tl = lead.get("assigned_teamlead", "unknown")
            text_lines.append(f"#{lead_id}: {username} → @{tl}")

        await message.answer(
            "📥 *Лиды (последние 20)*\n\n" + "\n".join(text_lines),
            parse_mode="Markdown"
        )
        return

    # /stats teamleads
    if cmd == "teamleads":
        tl_stats = top_teamleads(leads_new)

        text = "👥 *Эффективность тимлидов*\n\n"
        for tl, count in tl_stats.items():
            text += f"• @{tl}: *{count} лидов*\n"

        await message.answer(text, parse_mode="Markdown")
        return

    # /stats sources
    if cmd == "sources":
        sources = top_sources(users)

        text = "🌐 *Источники переходов (/start ref)*\n\n"
        for src, count in sources.items():
            text += f"• `{src}` — *{count}*\n"

        await message.answer(text, parse_mode="Markdown")
        return

    await message.answer("Неизвестная подкоманда. Используй `/stats`.")
