from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.logger import get_ad_stats

router = Router()


@router.message(Command("adstats"))
async def adstats(message: Message):
    """
    Показывает статистику по источникам трафика.
    """
    stats = get_ad_stats()

    if not stats:
        await message.answer("Пока никто не приходил по рекламе.")
        return

    text = "📊 <b>Статистика по источникам трафика:</b>\n\n"
    total = 0

    for source, count in stats.items():
        text += f"• <code>{source}</code> — <b>{count}</b>\n"
        total += count

    text += f"\n🧮 <b>Всего:</b> {total}"

    await message.answer(text)
