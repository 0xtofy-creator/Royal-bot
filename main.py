import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN

# handlers
from handlers.start import router as start_router
from handlers.fsm_leads import router as fsm_leads_router
from handlers.problems import router as problems_router
from handlers.callbacks import router as callbacks_router
from handlers.leads import router as leads_router
from handlers.stats import router as stats_router
from handlers.id import router as id_router
from handlers.admin import router as admin_router


logging.basicConfig(level=logging.INFO)


async def main() -> None:
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    dp = Dispatcher(storage=MemoryStorage())

    # ⚠️ ПОРЯДОК РОУТЕРОВ КРИТИЧЕН
    dp.include_router(start_router)

    # FSM должны идти ДО обычных callbacks
    dp.include_router(fsm_leads_router)     # FSM лидов
    dp.include_router(problems_router)      # FSM проблем

    # обычные callbacks / логика
    dp.include_router(callbacks_router)
    dp.include_router(leads_router)
    dp.include_router(stats_router)
    dp.include_router(id_router)
    dp.include_router(admin_router)

    logging.info("Royal Finance bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")
