from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import PROBLEM_CHAT_ID, PROBLEM_THREAD_ID
from keyboards.main_menu import main_menu

router = Router()


# =========================
# FSM
# =========================

class ProblemFSM(StatesGroup):
    waiting_for_content = State()


# =========================
# Старт проблемы
# =========================

@router.callback_query(F.data == "problem")
async def problem_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer(cache_time=1)
    await state.clear()
    await state.set_state(ProblemFSM.waiting_for_content)

    await callback.message.edit_text(
        "⚠️ <b>Опишите проблему</b>\n\n"
        "Вы можете отправить:\n"
        "• текст\n"
        "• фото\n"
        "• фото с подписью\n\n"
        "Сообщение будет передано в поддержку.",
        reply_markup=main_menu(callback.from_user.id),
    )


# =========================
# Приём текста / фото
# =========================

@router.message(ProblemFSM.waiting_for_content)
async def problem_collect(message: Message, state: FSMContext):
    user = message.from_user

    text = None
    photo_file_id = None

    if message.photo:
        photo_file_id = message.photo[-1].file_id
        text = message.caption
    elif message.text:
        text = message.text

    if not text and not photo_file_id:
        await message.answer("❗ Отправьте текст или фото.")
        return

    header = (
        "⚠️ <b>Проблема от пользователя</b>\n"
        f"👤 {user.full_name}\n"
        f"🆔 {user.id}\n"
        f"🔗 @{user.username if user.username else '—'}\n\n"
    )

    if photo_file_id:
        await message.bot.send_photo(
            chat_id=PROBLEM_CHAT_ID,
            message_thread_id=PROBLEM_THREAD_ID,
            photo=photo_file_id,
            caption=header + (text or ""),
        )
    else:
        await message.bot.send_message(
            chat_id=PROBLEM_CHAT_ID,
            message_thread_id=PROBLEM_THREAD_ID,
            text=header + text,
        )

    await state.clear()

    await message.answer(
        "✅ <b>Проблема отправлена</b>\n\n"
        "Мы уже передали сообщение в поддержку.",
        reply_markup=main_menu(user.id),
    )
