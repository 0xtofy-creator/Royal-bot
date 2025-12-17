from aiogram.exceptions import TelegramBadRequest


async def safe_edit_text(message, text: str, reply_markup=None) -> None:
    """
    Telegram запрещает edit_text, если текст и reply_markup не меняются.
    В таком случае TelegramBadRequest: message is not modified.
    Мы это считаем нормой и гасим.
    """
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            return
        raise
