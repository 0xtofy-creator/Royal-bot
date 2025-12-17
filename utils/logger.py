import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Tuple, Optional, Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

USERS_FILE = DATA_DIR / "users.json"
LEADS_FILE = DATA_DIR / "leads.json"

SOURCE_CLICKS_FILE = DATA_DIR / "source_clicks.json"
SOURCE_STATS_FILE = DATA_DIR / "source_stats.json"

MSK_TZ = timezone(timedelta(hours=3))  # МСК


def now_msk_str() -> str:
    return datetime.now(MSK_TZ).strftime("%Y-%m-%d %H:%M:%S")


def _ensure_file(path: Path, default: Any) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=4)


def _load_json(path: Path, default: Any) -> Any:
    _ensure_file(path, default)
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, type(default)) else default
    except (json.JSONDecodeError, OSError):
        return default


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# ---------------------------------------------------------------------------
# USERS
# ---------------------------------------------------------------------------

def get_users() -> Dict[str, Dict[str, Any]]:
    return _load_json(USERS_FILE, {})


def save_users(users: Dict[str, Dict[str, Any]]) -> None:
    _save_json(USERS_FILE, users)


def _log_source_click(user_id: int, source: str) -> None:
    clicks = _load_json(SOURCE_CLICKS_FILE, {})
    key = str(user_id)

    if key not in clicks:
        clicks[key] = []

    clicks[key].append({
        "source": source or "organic",
        "timestamp": now_msk_str(),
    })
    _save_json(SOURCE_CLICKS_FILE, clicks)

    stats = _load_json(SOURCE_STATS_FILE, {})
    src = source or "organic"
    if src not in stats:
        stats[src] = {"clicks": 0, "leads": 0}

    stats[src]["clicks"] += 1
    _save_json(SOURCE_STATS_FILE, stats)


def log_user_start(user_id: int, username: Optional[str], source: str) -> bool:
    users = get_users()
    key = str(user_id)

    username_display = f"@{username}" if username else f"id:{user_id}"
    now = now_msk_str()
    new_source = source or "organic"

    prev = users.get(key)
    prev_source = prev.get("source") if prev else None
    first_seen = prev.get("first_seen") if prev else now

    is_new_ad_user = False
    if new_source != "organic":
        if prev is None:
            is_new_ad_user = True
        elif prev_source == "organic":
            is_new_ad_user = True
        elif prev_source != new_source:
            is_new_ad_user = True

    if prev_source and prev_source != "organic" and new_source == "organic":
        new_source = prev_source

    users[key] = {
        "username": username_display,
        "source": new_source,
        "first_seen": first_seen,
        "last_seen": now,
    }
    save_users(users)

    _log_source_click(user_id=user_id, source=new_source)
    return is_new_ad_user


def get_user_source(user_id: int) -> str:
    users = get_users()
    info = users.get(str(user_id))
    if not info:
        return "organic"
    return info.get("source") or "organic"


def get_ad_stats() -> Dict[str, int]:
    users = get_users()
    stats: Dict[str, int] = {}
    for data in users.values():
        src = data.get("source") or "organic"
        stats[src] = stats.get(src, 0) + 1
    return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))


# ---------------------------------------------------------------------------
# LEADS
# ---------------------------------------------------------------------------

def get_leads() -> Dict[str, Dict[str, Any]]:
    return _load_json(LEADS_FILE, {})


def save_leads(leads: Dict[str, Dict[str, Any]]) -> None:
    _save_json(LEADS_FILE, leads)


def _next_lead_id(leads: Dict[str, Dict[str, Any]]) -> int:
    if not leads:
        return 1
    try:
        return max(int(k) for k in leads.keys()) + 1
    except ValueError:
        return 1


def get_lead(lead_id: int | str) -> Optional[Dict[str, Any]]:
    leads = get_leads()
    return leads.get(str(lead_id))


def get_open_lead_for_user(user_id: int) -> Optional[Dict[str, Any]]:
    leads = get_leads()
    for lead in leads.values():
        try:
            if int(lead.get("user_id")) != int(user_id):
                continue
        except (TypeError, ValueError):
            continue

        status = lead.get("status")
        if status in ("NEW", "IN_PROGRESS"):
            return lead
    return None


def get_last_closed_lead(user_id: int) -> Optional[Dict[str, Any]]:
    leads = get_leads()
    last: Optional[Dict[str, Any]] = None
    for lead in leads.values():
        try:
            if int(lead.get("user_id")) != int(user_id):
                continue
        except (TypeError, ValueError):
            continue

        status = lead.get("status")
        if status not in ("SUCCESS", "FAILED"):
            continue

        closed_at = lead.get("closed_at") or ""
        if not last:
            last = lead
        else:
            prev_closed = last.get("closed_at") or ""
            if closed_at > prev_closed:
                last = lead

    return last


def _inc_source_leads(source: str) -> None:
    stats = _load_json(SOURCE_STATS_FILE, {})
    src = source or "organic"
    if src not in stats:
        stats[src] = {"clicks": 0, "leads": 0}
    stats[src]["leads"] += 1
    _save_json(SOURCE_STATS_FILE, stats)


def create_lead(
    user_id: int,
    username_display: str,
    source: str,
    assigned_tl: str,
    user_comment: Optional[str] = None,
    photo_file_id: Optional[str] = None,
) -> Tuple[int, Dict[str, Any]]:
    leads = get_leads()
    lead_id = _next_lead_id(leads)

    prev_closed = get_last_closed_lead(user_id)
    is_repeat = prev_closed is not None

    lead = {
        "lead_id": lead_id,
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
        "is_repeat": is_repeat,
        "prev_lead_id": prev_closed.get("lead_id") if prev_closed else None,
        "prev_lead_status": prev_closed.get("status") if prev_closed else None,
        "prev_lead_closed_at": prev_closed.get("closed_at") if prev_closed else None,
        "user_comment": user_comment,
        "photo_file_id": photo_file_id,

        # чтобы можно было редактировать карточку лида в чате лидов
        "leads_message_id": None,
    }

    leads[str(lead_id)] = lead
    save_leads(leads)

    _inc_source_leads(source)

    return lead_id, lead


def _update_lead(lead_id: int, **fields: Any) -> Optional[Dict[str, Any]]:
    leads = get_leads()
    key = str(lead_id)
    lead = leads.get(key)
    if not lead:
        return None

    lead.update(fields)
    leads[key] = lead
    save_leads(leads)
    return lead


def set_lead_taken(lead_id: int, staff_id: int, staff_username: str) -> Optional[Dict[str, Any]]:
    return _update_lead(
        lead_id,
        status="IN_PROGRESS",
        taken_by_id=staff_id,
        taken_by_username=staff_username,
        taken_at=now_msk_str(),
    )


def set_lead_closed(
    lead_id: int,
    staff_id: int,
    staff_username: str,
    status: str,
) -> Optional[Dict[str, Any]]:
    if status not in ("SUCCESS", "FAILED"):
        status = "FAILED"

    return _update_lead(
        lead_id,
        status=status,
        closed_by_id=staff_id,
        closed_by_username=staff_username,
        closed_at=now_msk_str(),
    )


def cancel_lead(lead_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    lead = get_lead(lead_id)
    if not lead:
        return None

    try:
        if int(lead.get("user_id")) != int(user_id):
            return None
    except (TypeError, ValueError):
        return None

    if lead.get("status") not in ("NEW", "IN_PROGRESS"):
        return lead

    return _update_lead(
        lead_id,
        status="CANCELLED",
        closed_at=now_msk_str(),
    )


def update_lead_user_content(
    lead_id: int,
    user_id: int,
    user_comment: Optional[str],
    photo_file_id: Optional[str],
) -> Optional[Dict[str, Any]]:
    lead = get_lead(lead_id)
    if not lead:
        return None

    try:
        if int(lead.get("user_id")) != int(user_id):
            return None
    except (TypeError, ValueError):
        return None

    if lead.get("status") not in ("NEW", "IN_PROGRESS"):
        return lead

    return _update_lead(
        lead_id,
        user_comment=user_comment,
        photo_file_id=photo_file_id,
    )


def set_lead_leads_message_id(lead_id: int, message_id: int) -> Optional[Dict[str, Any]]:
    return _update_lead(lead_id, leads_message_id=message_id)


# ---------------------------------------------------------------------------
# SOURCE STATS
# ---------------------------------------------------------------------------

def get_source_stats() -> Dict[str, Dict[str, int]]:
    return _load_json(SOURCE_STATS_FILE, {})


def get_source_clicks() -> Dict[str, Any]:
    return _load_json(SOURCE_CLICKS_FILE, {})
