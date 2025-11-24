import json
import os
from datetime import datetime

from config import (
    ADMIN_CHAT_ID,
    ADMIN_USERS_THREAD_ID,
    ADMIN_LEADS_THREAD_ID,
    ADMIN_EVENTS_THREAD_ID,
    ADMIN_ERRORS_THREAD_ID,
)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


def _write_json_line(filename: str, data: dict):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


async def log_general_event(bot, text: str):
    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=text,
        )
    except Exception as e:
        print("[WARN] log_general_event error:", e)


async def log_error(bot, where: str, error: Exception | str):
    now = datetime.now()
    data = {
        "timestamp": now.isoformat(),
        "where": where,
        "error": str(error),
    }
    _write_json_line("errors.json", data)

    msg = (
        "❗ Ошибка в боте\n\n"
        f"Где: {where}\n"
        f"Ошибка: {str(error)}\n"
        f"Время: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            message_thread_id=ADMIN_ERRORS_THREAD_ID,
            text=msg
        )
    except Exception as e:
        print("[WARN] log_error send:", e)


async def log_user(bot, user_id: int, username: str, ref: str):
    now = datetime.now()
    data = {
        "timestamp": now.isoformat(),
        "event": "new_user",
        "user_id": user_id,
        "username": username,
        "ref": ref or "",
    }
    _write_json_line("users.json", data)

    text = (
        "👤 Новый пользователь\n\n"
        f"Пользователь: {username}\n"
        f"ID: {user_id}\n"
        f"Источник: {ref if ref else '—'}\n"
        f"Время: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    try:
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            message_thread_id=ADMIN_USERS_THREAD_ID,
            text=text,
        )
    except Exception as e:
        print("[WARN] log_user send error:", e)


def _load_json_lines(filename: str):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def _get_next_lead_id():
    items = _load_json_lines("leads.json")
    if not items:
        return 1
    return max(i.get("lead_id", 0) for i in items) + 1


async def log_lead(bot, user_id: int, username: str, teamlead: str, ref="") -> int:
    now = datetime.now()
    lead_id = _get_next_lead_id()

    item = {
        "timestamp": now.isoformat(),
        "event": "lead_new",
        "lead_id": lead_id,
        "user_id": user_id,
        "username": username,
        "assigned_teamlead": teamlead,
        "ref": ref,
        "status": "new",
    }
    _write_json_line("leads.json", item)
    return lead_id


async def log_lead_status(bot, lead_id: int, username: str, status: str):
    now = datetime.now()

    item = {
        "timestamp": now.isoformat(),
        "event": "lead_status",
        "lead_id": lead_id,
        "username": username,
        "status": status,
    }
    _write_json_line("leads.json", item)
