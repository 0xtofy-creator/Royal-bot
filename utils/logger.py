import json
import os
from datetime import datetime

USERS_FILE = "data/users.json"
LEADS_FILE = "data/leads.json"
EVENTS_FILE = "data/events.json"


# ---------- JSON helpers ----------

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ---------- USER TRACKING ----------

async def save_user_source(user_id, username, source):
    """
    Сохраняет источник трафика пользователя.
    """
    users = load_json(USERS_FILE)
    user_id = str(user_id)

    if user_id not in users:  # Новый пользователь
        users[user_id] = {
            "username": f"@{username}" if username else None,
            "source": source,
            "first_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    save_json(USERS_FILE, users)


def get_ad_stats():
    """
    Возвращает статистику по источникам трафика.
    """
    users = load_json(USERS_FILE)

    result = {}
    for u in users.values():
        src = u.get("source", "unknown")
        result[src] = result.get(src, 0) + 1

    return result


# ---------- LEAD LOGS ----------

def log_lead_created(user_id: int, username: str | None, teamlead: str, source: str | None = None) -> str:
    """
    Создаёт запись о новом лиде.
    """
    leads = load_json(LEADS_FILE)
    lead_id = str(len(leads) + 1)

    leads[lead_id] = {
        "user_id": user_id,
        "username": username,
        "teamlead": teamlead,
        "source": source,
        "status": "NEW",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_json(LEADS_FILE, leads)
    return lead_id


def set_lead_status(lead_id: str, status: str):
    """
    Обновляет статус лида.
    """
    leads = load_json(LEADS_FILE)

    if lead_id in leads:
        leads[lead_id]["status"] = status
        leads[lead_id]["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_json(LEADS_FILE, leads)


def get_leads():
    return load_json(LEADS_FILE)


# ---------- GENERIC EVENT LOGS (optional) ----------

def log_event(event_type: str, data: dict):
    """
    Логирует произвольные события бота.
    """
    events = load_json(EVENTS_FILE)

    events[str(len(events) + 1)] = {
        "event": event_type,
        "data": data,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    save_json(EVENTS_FILE, events)
