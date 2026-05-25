import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database.repository import init_db
from handlers import admin, common, user
from handlers import fallback                    # ← NEW: catch-all, included last
from middlewares.ban_check import BanCheckMiddleware
from middlewares.logging_mw import LoggingMiddleware  # ← NEW: activity logger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)-8s]  %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    await init_db()
    logger.info("Database initialised.")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Middleware order: logging fires first, then ban-check
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(BanCheckMiddleware())

    # Router order matters — fallback MUST be last
    dp.include_router(common.router)
    dp.include_router(user.router)
    dp.include_router(admin.router)
    dp.include_router(fallback.router)           # ← always last

    logger.info("Starting polling…")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
