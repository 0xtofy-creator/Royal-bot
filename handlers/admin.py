# handlers/admin.py

import asyncio
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import ADMIN_IDS, TEAMLEADS
from utils.logger import (
    get_leads,
    get_lead,
    get_source_stats,
    get_users,
)

router = Router()

# Ограничиваем весь роутер администраторами
router.message.filter(lambda m: m.from_user.id in ADMIN_IDS)
router.callback_query.filter(lambda c: c.from_user.id in ADMIN_IDS)


# -------------------------------------------------------
#   FSM состояния
# -------------------------------------------------------

class AdminStates(StatesGroup):
    wait_user_leads_id = State()
    wait_lead_history_id = State()


class BroadcastStates(StatesGroup):
    wait_text = State()
    wait_buttons = State()


# -------------------------------------------------------
#   Клавиатуры
# -------------------------------------------------------

def kb_admin_menu() -> InlineKeyboardMarkup:
    """Главное меню админ-панели."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📈 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton(text="🔍 Активные лиды", callback_data="admin_active")],
            [InlineKeyboardButton(text="👤 Лиды пользователя", callback_data="admin_user_leads")],
            [InlineKeyboardButton(text="📄 История лида", callback_data="admin_lead_history")],
            [InlineKeyboardButton(text="📌 Лиды по статусу", callback_data="admin_status_menu")],
            [InlineKeyboardButton(text="👨‍💼 Лиды тимлидов", callback_data="admin_tl_menu")],
            [InlineKeyboardButton(text="📣 Источники трафика", callback_data="admin_sources")],
            [InlineKeyboardButton(text="📨 Рассылка (всем)", callback_data="admin_broadcast")],
            [InlineKeyboardButton(text="🧪 Тестовая рассылка", callback_data="admin_broadcast_test")],
            [InlineKeyboardButton(text="🗓 Отчёты 7/30 дней", callback_data="admin_period_reports")],
        ]
    )


def kb_cancel() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅ Назад", callback_data="admin_back")]
        ]
    )


def build_broadcast_keyboard(buttons):
    """
    Собираем InlineKeyboardMarkup из списка кнопок вида:
    {"text": "...", "url": "..."}
    """
    if not buttons:
        return None

    rows = []
    for b in buttons:
        text = b.get("text")
        url = b.get("url")
        if not text or not url:
            continue
        rows.append([InlineKeyboardButton(text=text, url=url)])

    if not rows:
        return None

    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_broadcast_confirm_all() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Отправить всем", callback_data="broadcast_confirm_all")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="broadcast_cancel")],
        ]
    )


def kb_broadcast_confirm_test() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🧪 Отправить только мне", callback_data="broadcast_confirm_test")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="broadcast_cancel")],
        ]
    )


# -------------------------------------------------------
#   Вход в админ-панель
# -------------------------------------------------------

@router.message(Command("admin"))
async def admin_panel_cmd(message: Message, state: FSMContext):
    # На всякий случай чистим любое старое состояние
    await state.clear()
    await message.answer(
        "🛠 Админ-панель\nВыберите раздел:",
        reply_markup=kb_admin_menu()
    )


@router.callback_query(F.data.in_({"admin_open", "admin_panel"}))
async def admin_panel_cb(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🛠 Админ-панель\nВыберите раздел:",
        reply_markup=kb_admin_menu()
    )
    await callback.answer()


# -------------------------------------------------------
#   1) Общая статистика
# -------------------------------------------------------

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    leads = get_leads()
    total = len(leads)

    new = sum(1 for x in leads.values() if x.get("status") == "NEW")
    progress = sum(1 for x in leads.values() if x.get("status") == "IN_PROGRESS")
    success = sum(1 for x in leads.values() if x.get("status") == "SUCCESS")
    failed = sum(1 for x in leads.values() if x.get("status") == "FAILED")
    repeat = sum(1 for x in leads.values() if x.get("is_repeat"))

    text = (
        "📊 <b>Общая статистика</b>\n\n"
        f"Всего лидов: <b>{total}</b>\n"
        f"🟡 Новые: {new}\n"
        f"🔵 В работе: {progress}\n"
        f"🟢 Успех: {success}\n"
        f"🔴 Неуспех: {failed}\n"
        f"♻ Повторные: {repeat}\n"
    )

    await callback.message.edit_text(text, reply_markup=kb_admin_menu())
    await callback.answer()


# -------------------------------------------------------
#   2) Активные лиды
# -------------------------------------------------------

@router.callback_query(F.data == "admin_active")
async def admin_active(callback: CallbackQuery):
    leads = get_leads()
    active = [
        l for l in leads.values()
        if l.get("status") in ("NEW", "IN_PROGRESS")
    ]

    if not active:
        text = "🔍 Активных лидов нет."
    else:
        text = "🔍 <b>Активные лиды:</b>\n\n"
        for l in active:
            text += f"• #{l.get('lead_id')} — {l.get('status')} — {l.get('username')}\n"

    await callback.message.edit_text(text, reply_markup=kb_admin_menu())
    await callback.answer()


# -------------------------------------------------------
#   3) Лиды пользователя
# -------------------------------------------------------

@router.callback_query(F.data == "admin_user_leads")
async def admin_user_leads(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.wait_user_leads_id)
    await callback.message.edit_text(
        "👤 Введите <b>ID пользователя</b>:",
        reply_markup=kb_cancel()
    )
    await callback.answer()


@router.message(StateFilter(AdminStates.wait_user_leads_id))
async def process_user_leads_id(message: Message, state: FSMContext):
    user_id = message.text.strip()

    if not user_id.isdigit():
        await message.answer("❌ Некорректный ID. Введите число.")
        return

    leads = get_leads()
    items = [
        l for l in leads.values()
        if str(l.get("user_id")) == user_id
    ]

    if not items:
        await message.answer("📭 У пользователя нет лидов.", reply_markup=kb_admin_menu())
        await state.clear()
        return

    text = f"👤 <b>Лиды пользователя {user_id}:</b>\n\n"
    for l in items:
        text += f"• #{l.get('lead_id')} — {l.get('status')} — {l.get('source')}\n"

    await message.answer(text, reply_markup=kb_admin_menu())
    await state.clear()


# -------------------------------------------------------
#   4) История лида
# -------------------------------------------------------

@router.callback_query(F.data == "admin_lead_history")
async def admin_lead_history(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.wait_lead_history_id)
    await callback.message.edit_text(
        "📄 Введите <b>номер лида</b>:",
        reply_markup=kb_cancel()
    )
    await callback.answer()


@router.message(StateFilter(AdminStates.wait_lead_history_id))
async def process_lead_history(message: Message, state: FSMContext):
    lead_id = message.text.strip()

    if not lead_id.isdigit():
        await message.answer("❌ Некорректный номер.")
        return

    lead = get_lead(lead_id)
    if not lead:
        await message.answer("❌ Лид не найден.", reply_markup=kb_admin_menu())
        await state.clear()
        return

    text = (
        f"📄 <b>История лида #{lead_id}</b>\n\n"
        f"Пользователь: {lead.get('username')}\n"
        f"ID: {lead.get('user_id')}\n"
        f"Источник: {lead.get('source')}\n"
        f"Статус: {lead.get('status')}\n"
        f"Создан: {lead.get('created_at')}\n"
    )

    if lead.get("taken_by_username"):
        text += (
            f"\n🔵 Взял: {lead.get('taken_by_username')}\n"
            f"Время: {lead.get('taken_at')}\n"
        )

    if lead.get("closed_by_username"):
        text += (
            f"\n🔚 Закрыл: {lead.get('closed_by_username')}\n"
            f"Время: {lead.get('closed_at')}\n"
        )

    if lead.get("is_repeat"):
        text += (
            f"\n♻ Повторная заявка. "
            f"Предыдущий лид #{lead.get('prev_lead_id')} — {lead.get('prev_lead_status')}\n"
        )

    if lead.get("user_comment"):
        text += f"\n💬 Комментарий трейдера:\n{lead.get('user_comment')}\n"

    await message.answer(text, reply_markup=kb_admin_menu())
    await state.clear()


# -------------------------------------------------------
#   5) Лиды по статусу
# -------------------------------------------------------

def kb_status_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🟡 NEW", callback_data="admin_status:NEW")],
            [InlineKeyboardButton(text="🔵 IN_PROGRESS", callback_data="admin_status:IN_PROGRESS")],
            [InlineKeyboardButton(text="🟢 SUCCESS", callback_data="admin_status:SUCCESS")],
            [InlineKeyboardButton(text="🔴 FAILED", callback_data="admin_status:FAILED")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="admin_back")],
        ]
    )


@router.callback_query(F.data == "admin_status_menu")
async def admin_status_menu(callback: CallbackQuery):
    await callback.message.edit_text("📌 Выберите статус:", reply_markup=kb_status_menu())
    await callback.answer()


@router.callback_query(F.data.startswith("admin_status:"))
async def admin_status_list(callback: CallbackQuery):
    status = callback.data.split(":", 1)[1]
    leads = get_leads()
    items = [l for l in leads.values() if l.get("status") == status]

    if not items:
        text = f"📌 Лидов со статусом <b>{status}</b> нет."
    else:
        text = f"📌 <b>Лиды со статусом {status}</b>:\n\n"
        for l in items:
            text += f"• #{l.get('lead_id')} — {l.get('username')}\n"

    await callback.message.edit_text(text, reply_markup=kb_admin_menu())
    await callback.answer()


# -------------------------------------------------------
#   6) Лиды тимлидов
# -------------------------------------------------------

def kb_tl_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"@{tl}", callback_data=f"admin_tl:{tl}")]
        for tl in TEAMLEADS
    ]
    rows.append([InlineKeyboardButton(text="⬅ Назад", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "admin_tl_menu")
async def admin_tl_menu(callback: CallbackQuery):
    await callback.message.edit_text("👨‍💼 Выберите тимлида:", reply_markup=kb_tl_menu())
    await callback.answer()


@router.callback_query(F.data.startswith("admin_tl:"))
async def admin_tl_leads(callback: CallbackQuery):
    tl_name = callback.data.split(":", 1)[1]  # без @
    tl_tag = f"@{tl_name}"

    leads = get_leads()
    items = [
        l for l in leads.values()
        if l.get("taken_by_username") == tl_tag or l.get("closed_by_username") == tl_tag
    ]

    if not items:
        text = f"📭 У {tl_tag} нет обработанных лидов."
    else:
        text = f"👨‍💼 <b>Лиды тимлида {tl_tag}</b>:\n\n"
        for l in items:
            text += f"• #{l.get('lead_id')} — {l.get('status')} — {l.get('username')}\n"

    await callback.message.edit_text(text, reply_markup=kb_admin_menu())
    await callback.answer()


# -------------------------------------------------------
#   7) Источники трафика (клики/лиды/конверсия)
# -------------------------------------------------------

@router.callback_query(F.data == "admin_sources")
async def admin_sources(callback: CallbackQuery):
    stats = get_source_stats()

    if not stats:
        await callback.message.edit_text(
            "📣 Источники трафика пока пусты.",
            reply_markup=kb_admin_menu()
        )
        await callback.answer()
        return

    text = "📣 <b>Источники трафика и конверсии</b>:\n\n"

    for src, v in stats.items():
        clicks = v.get("clicks", 0)
        leads = v.get("leads", 0)
        conv = round(leads / clicks * 100, 2) if clicks else 0.0

        text += (
            f"<b>{src}</b>\n"
            f"• Переходов: {clicks}\n"
            f"• Лидов: {leads}\n"
            f"• Конверсия: {conv}%\n\n"
        )

    await callback.message.edit_text(text, reply_markup=kb_admin_menu())
    await callback.answer()


# -------------------------------------------------------
#   📨 Рассылка (всем и тестовая)
# -------------------------------------------------------

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    # массовая рассылка
    await state.clear()
    await state.update_data(b_mode="all")
    await state.set_state(BroadcastStates.wait_text)

    await callback.message.edit_text(
        "📨 <b>Рассылка (всем)</b>\n\n"
        "1️⃣ Отправьте текст рассылки одним сообщением.\n"
        "Можно с HTML-разметкой.\n"
        "Если хотите картинку — отправьте фото с подписью.\n",
        reply_markup=kb_cancel()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_broadcast_test")
async def admin_broadcast_test_start(callback: CallbackQuery, state: FSMContext):
    # тестовая рассылка
    await state.clear()
    await state.update_data(b_mode="test")
    await state.set_state(BroadcastStates.wait_text)

    await callback.message.edit_text(
        "🧪 <b>Тестовая рассылка</b>\n\n"
        "1️⃣ Отправьте текст или фото с подписью.\n"
        "Сообщение будет отправлено <b>только вам</b> для проверки.",
        reply_markup=kb_cancel()
    )
    await callback.answer()


@router.message(StateFilter(BroadcastStates.wait_text))
async def admin_broadcast_get_text(message: Message, state: FSMContext):
    # поддерживаем либо текст, либо фото с подписью
    msg_type = "text"
    text = ""
    photo_id = None

    if message.photo:
        msg_type = "photo"
        photo_id = message.photo[-1].file_id
        text = message.caption or ""
    else:
        text = message.text or ""

    text = (text or "").trim() if hasattr(str, "trim") else (text or "").strip()

    if not text:
        await message.answer("❌ Текст рассылки пустой. Отправьте текст или фото с подписью.")
        return

    await state.update_data(
        b_type=msg_type,
        b_text=text,
        b_photo_id=photo_id,
        b_buttons=[],
    )

    await state.set_state(BroadcastStates.wait_buttons)
    await message.answer(
        "2️⃣ Теперь отправьте кнопки для рассылки.\n\n"
        "Формат:\n"
        "<code>Текст кнопки | https://ссылка</code>\n"
        "Каждая кнопка — с новой строки.\n\n"
        "Если кнопки не нужны — напишите <b>нет</b>.",
        reply_markup=kb_cancel()
    )


@router.message(StateFilter(BroadcastStates.wait_buttons))
async def admin_broadcast_get_buttons(message: Message, state: FSMContext):
    raw = (message.text or "").strip()

    buttons = []
    if raw.lower() not in ("нет", "no", "-", ""):
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            if "|" not in line:
                continue
            title, url = map(str.strip, line.split("|", 1))
            if not title or not url:
                continue
            buttons.append({"text": title, "url": url})

    await state.update_data(b_buttons=buttons)
    data = await state.get_data()

    msg_type = data.get("b_type", "text")
    text = data.get("b_text", "")
    photo_id = data.get("b_photo_id")
    kb_users = build_broadcast_keyboard(buttons)
    mode = data.get("b_mode", "all")

    # Показываем превью рассылки
    if msg_type == "photo" and photo_id:
        await message.answer_photo(photo_id, caption=text, reply_markup=kb_users)
    else:
        await message.answer(text, reply_markup=kb_users)

    # Кнопки подтверждения — разные для режима all/test
    if mode == "test":
        await message.answer(
            "Так будет выглядеть рассылка.\n\n"
            "Нажмите, чтобы отправить <b>только себе</b>.",
            reply_markup=kb_broadcast_confirm_test()
        )
    else:
        await message.answer(
            "Так будет выглядеть рассылка у пользователей.\n\n"
            "Нажмите, чтобы отправить <b>всем пользователям</b>.",
            reply_markup=kb_broadcast_confirm_all()
        )


@router.callback_query(F.data == "broadcast_confirm_test")
async def admin_broadcast_confirm_test(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    msg_type = data.get("b_type", "text")
    text = data.get("b_text", "")
    photo_id = data.get("b_photo_id")
    buttons = data.get("b_buttons", [])
    kb_users = build_broadcast_keyboard(buttons)

    bot = callback.message.bot
    admin_id = callback.from_user.id  # либо жёстко 7585804566, но так гибче

    try:
        if msg_type == "photo" and photo_id:
            await bot.send_photo(
                chat_id=admin_id,
                photo=photo_id,
                caption=text,
                reply_markup=kb_users,
            )
        else:
            await bot.send_message(
                chat_id=admin_id,
                text=text,
                reply_markup=kb_users,
            )
        status = "Отправлено 🟢"
    except Exception as e:
        status = f"Ошибка отправки: {e}"

    await state.clear()
    await callback.message.edit_text(
        f"🧪 Тестовая рассылка завершена.\n\nСтатус: {status}",
        reply_markup=kb_admin_menu()
    )
    await callback.answer("Готово!")


@router.callback_query(F.data == "broadcast_confirm_all")
async def admin_broadcast_confirm_all(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    msg_type = data.get("b_type", "text")
    text = data.get("b_text", "")
    photo_id = data.get("b_photo_id")
    buttons = data.get("b_buttons", [])
    kb_users = build_broadcast_keyboard(buttons)

    users = get_users()
    total = len(users)
    sent = 0
    failed = 0

    bot = callback.message.bot

    for user_id_str in users.keys():
        try:
            user_id = int(user_id_str)
        except ValueError:
            continue

        try:
            if msg_type == "photo" and photo_id:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=photo_id,
                    caption=text,
                    reply_markup=kb_users,
                )
            else:
                await bot.send_message(
                    chat_id=user_id,
                    text=text,
                    reply_markup=kb_users,
                )
            sent += 1
        except Exception:
            failed += 1

        await asyncio.sleep(0.05)

    await state.clear()
    await callback.message.edit_text(
        "📨 <b>Рассылка завершена</b>\n\n"
        f"Всего пользователей: {total}\n"
        f"Отправлено: {sent}\n"
        f"Ошибок: {failed}\n",
        reply_markup=kb_admin_menu()
    )
    await callback.answer("Рассылка выполнена.")


@router.callback_query(F.data == "broadcast_cancel")
async def admin_broadcast_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Рассылка отменена.",
        reply_markup=kb_admin_menu()
    )
    await callback.answer("Отмена.")


# -------------------------------------------------------
#   10) Отчёты 7 / 30 дней
# -------------------------------------------------------

def kb_period_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗓 Последние 7 дней", callback_data="admin_period:7")],
            [InlineKeyboardButton(text="🗓 Последние 30 дней", callback_data="admin_period:30")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="admin_back")],
        ]
    )


@router.callback_query(F.data == "admin_period_reports")
async def admin_period_reports(callback: CallbackQuery):
    await callback.message.edit_text("🗓 Выберите период:", reply_markup=kb_period_menu())
    await callback.answer()


@router.callback_query(F.data.startswith("admin_period:"))
async def admin_period_show(callback: CallbackQuery):
    days_str = callback.data.split(":", 1)[1]
    try:
        days = int(days_str)
    except ValueError:
        days = 7

    leads = get_leads()
    if not leads:
        await callback.message.edit_text("Лидов пока нет.", reply_markup=kb_admin_menu())
        await callback.answer()
        return

    now = datetime.now()
    start_date = now - timedelta(days=days)

    def parse_created(lead):
        created_at = lead.get("created_at")
        if not created_at:
            return None
        try:
            return datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None

    period_leads = []
    for l in leads.values():
        dt_val = parse_created(l)
        if not dt_val:
            continue
        if dt_val >= start_date:
            period_leads.append(l)

    if not period_leads:
        await callback.message.edit_text(
            f"🗓 За последние {days} дней лидов нет.",
            reply_markup=kb_admin_menu()
        )
        await callback.answer()
        return

    total = len(period_leads)
    success = sum(1 for l in period_leads if l.get("status") == "SUCCESS")
    failed = sum(1 for l in period_leads if l.get("status") == "FAILED")
    repeat = sum(1 for l in period_leads if l.get("is_repeat"))

    text = (
        f"🗓 <b>Отчёт за последние {days} дней</b>\n\n"
        f"Всего лидов: {total}\n"
        f"🟢 Успешных: {success}\n"
        f"🔴 Неуспешных: {failed}\n"
        f"♻ Повторных: {repeat}\n\n"
        "Последние лиды:\n"
    )

    period_leads_sorted = sorted(
        period_leads,
        key=lambda l: l.get("created_at") or "",
        reverse=True
    )[:15]

    for l in period_leads_sorted:
        text += (
            f"• #{l.get('lead_id')} — {l.get('status')} — "
            f"{l.get('username')} — {l.get('created_at')}\n"
        )

    await callback.message.edit_text(text, reply_markup=kb_admin_menu())
    await callback.answer()


# -------------------------------------------------------
#   Назад / отмена
# -------------------------------------------------------

@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🛠 Админ-панель\nВыберите раздел:",
        reply_markup=kb_admin_menu()
    )
    await callback.answer()
