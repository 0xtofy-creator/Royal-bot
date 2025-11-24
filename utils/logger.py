import json
import os
from datetime import datetime

# Пути к JSON-файлам
BASE_DIR = "/root/Royal-bot/data"
USERS_FILE = f"{BASE_DIR}/users.json"
LEADS_FILE = f"{BASE_DIR}/leads.json"
EVENTS_FILE = f"{BASE_DIR}/events.json"

# Убедимся, что директория существует
os.makedirs(BASE_DIR, exist_ok=True)


# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ---------- ЛОГИ ПОЛЬЗОВАТЕЛЕЙ ----------

def log_user_start(user_id, username):
    data = load_json(USERS_FILE)
    data[str(user_id)] = {
        "username": username,
        "first_seen": datetime.now().isoformat()
    }
    save_json(USERS_FILE, data)


def get_users():
    """Возвращает всех пользователей."""
    return load_json(USERS_FILE)


# ---------- ЛОГИ ЛИДОВ ----------

def log_lead_created(user_id, username, teamlead):
    data = load_json(LEADS_FILE)
    lead_id = str(len(data) + 1)

    data[lead_id] = {
        "user_id": user_id,
        "username": username,
        "teamlead": teamlead,
        "status": "NEW",
        "timestamp": datetime.now().isoformat()
    }

    save_json(LEADS_FILE, data)
    return lead_id


def set_lead_status(lead_id, status):
    data = load_json(LEADS_FILE)
    if lead_id in data:
        data[lead_id]["status"] = status
        data[lead_id]["updated"] = datetime.now().isoformat()
        save_json(LEADS_FILE, data)


def get_leads():
    """Возвращает все лиды."""
    return load_json(LEADS_FILE)


# ---------- ЛОГИ СОБЫТИЙ ----------

def log_general_event(bot, text):
    """Отправляет событие в General-тред."""
    from config import GENERAL_CHAT_ID, EVENTS_THREAD_ID
    return bot.send_message(
        chat_id=GENERAL_CHAT_ID,
        message_thread_id=EVENTS_THREAD_ID,
        text=text
    )
