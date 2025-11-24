# main.py

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers.start import router as start_router
from handlers.callbacks import router as callbacks_router
from handlers.leads import router as leads_router
from handlers.stats import router as stats_router
from handlers.id import router as id_router


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(callbacks_router)
    dp.include_router(leads_router)
    dp.include_router(stats_router)
    dp.include_router(id_router)

    print("Royal Finance bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped")
