import random
from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.main_menu import main_menu
from keyboards.back_menu import back_menu
from utils.texts import (
    JOIN_TEMPLATE,
    MANUALS_TEXT,
    MENTORS_TEXT,
    REPRESENTATIVES_TEXT
)

router = Router()

SUPPORT_ACCOUNTS = [
    "Royal_Trader_Support_1",
    "Royal_Trader_Support_2",
    "Royal_Trader_Support_3",
    "Royal_Trader_Support_4"
]

# --- Главное меню ---
@router.callback_query(lambda c: c.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выбери нужный раздел ниже 👇",
        reply_markup=main_menu()
    )


# --- Назад ---
@router.callback_query(lambda c: c.data == "back")
async def cb_back(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выбери нужный раздел ниже 👇",
        reply_markup=main_menu()
    )


# --- Подключиться на площадку ---
@router.callback_query(lambda c: c.data == "join")
async def cb_join(callback: CallbackQuery):

    random_support = random.choice(SUPPORT_ACCOUNTS)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💬 Написать менеджеру",
            url=f"https://t.me/{random_support}"
        )],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")]
    ])

    await callback.message.edit_text(
        JOIN_TEMPLATE.format(
            username=callback.from_user.username,
            user_id=callback.from_user.id
        ),
        reply_markup=kb
    )


# --- Актуальный оффер ---
@router.callback_query(lambda c: c.data == "offer")
async def cb_offer(callback: CallbackQuery):

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💬 Открыть чат с ботом",
            url="https://t.me/royal_servebot"
        )],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu")]
    ])

    await callback.message.edit_text(
        "🔥 Актуальный оффер Royal Finance:\n\n"
        "— Мобильная коммерция до 16%\n"
        "— Поток 24/7\n"
        "— Готовые банки\n",
        reply_markup=kb
    )


# --- Мануалы ---
@router.callback_query(lambda c: c.data == "manuals")
async def cb_manuals(callback: CallbackQuery):
    await callback.message.edit_text(MANUALS_TEXT, reply_markup=back_menu())


# --- Тимлиды ---
@router.callback_query(lambda c: c.data == "teamleads")
async def cb_teamleads(callback: CallbackQuery):
    await callback.message.edit_text(REPRESENTATIVES_TEXT, reply_markup=back_menu())


# --- Менторы ---
@router.callback_query(lambda c: c.data == "mentors")
async def cb_mentors(callback: CallbackQuery):
    await callback.message.edit_text(MENTORS_TEXT, reply_markup=back_menu())
