import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
from handlers import router as main_router

logger = logging.getLogger("KrasokAI.Main")


async def main():
    logger.info("Initializing KrasokAI Telegram Bot...")

    if not config.validate_config():
        logger.critical("Initialization failed due to invalid configuration. Exiting.")
        sys.exit(1)

    bot = Bot(
        token=config.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    dp.include_router(main_router)

    async def on_startup(bot: Bot):
        bot_info = await bot.get_me()
        logger.info(f"Bot @{bot_info.username} is now online and polling!")

    async def on_shutdown(bot: Bot):
        logger.info("Shutting down polling and closing bot session...")
        await bot.session.close()
        logger.info("Bot session closed successfully. Goodbye!")

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook deleted and pending updates dropped.")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"An error occurred during bot polling: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped manually via KeyboardInterrupt.")
    except Exception as err:
        logger.critical(f"Critical unhandled error: {err}")
