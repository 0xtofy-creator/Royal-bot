from aiogram.exceptions import TelegramBadRequest


async def safe_edit_text(message, text: str, reply_markup=None) -> None:
   
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            return
        raise
