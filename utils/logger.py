# utils/logger.py

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Базовая папка проекта
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

USERS_FILE = DATA_DIR / "users.json"
LEADS_FILE = DATA_DIR / "leads.json"

MSK_TZ = timezone(timedelta(hours=3))  # МСК


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(path: Path):
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_json(path: Path, data):
    _ensure_data_dir()
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def now_msk_str() -> str:
    return datetime.now(MSK_TZ).strftime("%Y-%m-%d %H:%M:%S")


# -------- USERS (источники трафика) --------

def log_user_start(user_id: int, username: str | None, source: str | None):
    users = _load_json(USERS_FILE)
    users[str(user_id)] = {
        "username": f"@{username}" if username else None,
        "source": source or "organic",
        "first_seen": now_msk_str(),
    }
    _save_json(USERS_FILE, users)


def get_users() -> dict:
    return _load_json(USERS_FILE)


def get_user_source(user_id: int) -> str:
    users = get_users()
    return users.get(str(user_id), {}).get("source", "organic")


def get_ad_stats() -> dict:
    users = get_users()
    stats: dict[str, int] = {}
    for u in users.values():
        src = u.get("source", "unknown")
        stats[src] = stats.get(src, 0) + 1
    return stats


# -------- LEADS (лиды) --------

def get_leads() -> dict:
    return _load_json(LEADS_FILE)


def get_lead(lead_id: int | str) -> dict | None:
    leads = get_leads()
    return leads.get(str(lead_id))


def create_lead(user_id: int, username_display: str, source: str, assigned_tl: str):
    leads = get_leads()
    lead_id = str(len(leads) + 1)

    leads[lead_id] = {
        "lead_id": int(lead_id),
        "user_id": user_id,
        "username": username_display,
        "source": source,
        "assigned_tl": assigned_tl,
        "status": "NEW",

        "created_at": now_msk_str(),

        "taken_by_id": None,
        "taken_by_username": None,
        "taken_at": None,

        "closed_by_id": None,
        "closed_by_username": None,
        "closed_at": None,
    }

    _save_json(LEADS_FILE, leads)
    return int(lead_id), leads[lead_id]


def _update_lead(lead_id: int | str, **fields) -> dict | None:
    leads = get_leads()
    key = str(lead_id)
    lead = leads.get(key)
    if not lead:
        return None
    lead.update(fields)
    _save_json(LEADS_FILE, leads)
    return lead


def set_lead_taken(lead_id: int, staff_id: int, staff_username: str) -> dict | None:
    return _update_lead(
        lead_id,
        status="IN_PROGRESS",
        taken_by_id=staff_id,
        taken_by_username=staff_username,
        taken_at=now_msk_str(),
    )


def set_lead_closed(lead_id: int, staff_id: int, staff_username: str, status: str) -> dict | None:
    if status not in ("SUCCESS", "FAILED"):
        status = "FAILED"
    return _update_lead(
        lead_id,
        status=status,
        closed_by_id=staff_id,
        closed_by_username=staff_username,
        closed_at=now_msk_str(),
    )
