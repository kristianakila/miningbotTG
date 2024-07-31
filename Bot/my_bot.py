from .cfg import *
from aiogram import Dispatcher
from . import main_handler, wallet_handler, mining_handler, task_handler
import logging

logging.basicConfig(level=logging.DEBUG, filename="log.log")


async def start_bot():
    bot_data = await bot.get_me()
    print(f"[#DEBUG] Telegram bot (@{bot_data.username}) module is active...")
    dp = Dispatcher()

    dp.include_routers(
        main_handler.app, wallet_handler.app, mining_handler.app, task_handler.app
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
