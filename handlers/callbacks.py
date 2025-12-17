from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.main_menu import main_menu
from utils.texts import (
    OFFER_TEXT,
    MANUALS_TEXT,
    REPRESENTATIVES_TEXT,
    MENTORS_TEXT,
    PROBLEM_TEXT,
)
from utils.safe_edit import safe_edit_text
from config import PROBLEM_CHAT_ID, PROBLEM_THREAD_ID

router = Router()


@router.callback_query(F.data == "offer")
async def offer(callback: CallbackQuery):
    await callback.answer(cache_time=1)
    await safe_edit_text(callback.message, OFFER_TEXT, reply_markup=main_menu(callback.from_user.id))


@router.callback_query(F.data == "manuals")
async def manuals(callback: CallbackQuery):
    await callback.answer(cache_time=1)
    await safe_edit_text(callback.message, MANUALS_TEXT, reply_markup=main_menu(callback.from_user.id))


@router.callback_query(F.data == "teamleads")
async def teamleads(callback: CallbackQuery):
    await callback.answer(cache_time=1)
    await safe_edit_text(callback.message, REPRESENTATIVES_TEXT, reply_markup=main_menu(callback.from_user.id))


@router.callback_query(F.data == "mentors")
async def mentors(callback: CallbackQuery):
    await callback.answer(cache_time=1)
    await safe_edit_text(callback.message, MENTORS_TEXT, reply_markup=main_menu(callback.from_user.id))


@router.callback_query(F.data == "problem")
async def problem(callback: CallbackQuery):
    await callback.answer(cache_time=1)

    user = callback.from_user

    await safe_edit_text(
        callback.message,
        PROBLEM_TEXT,
        reply_markup=main_menu(user.id),
    )

    await callback.bot.send_message(
        chat_id=PROBLEM_CHAT_ID,
        message_thread_id=PROBLEM_THREAD_ID,
        text=(
            "⚠️ <b>Проблема от пользователя</b>\n"
            f"👤 {user.full_name}\n"
            f"🆔 {user.id}\n"
            f"🔗 @{user.username if user.username else '—'}\n\n"
            "<i>Ожидаем сообщение…</i>"
        ),
    )
