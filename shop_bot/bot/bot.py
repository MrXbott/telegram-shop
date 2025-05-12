import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from decouple import config

from bot.handlers import user
from bot.handlers.admin import admin
from db.init import init_db, async_session_maker
# from bot.middlewares.session import DBSessionMiddleware
from bot.middlewares.error_logging import ErrorLoggingMiddleware
from bot.commands import set_commands
from logging_config import setup_logging


setup_logging()

async def main():
    # await init_db()
    bot = Bot(token=config('BOT_TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()

    # dp.update.middleware(DBSessionMiddleware(async_session_maker))
    dp.update.middleware(ErrorLoggingMiddleware())

    dp.include_routers(admin.router)
    for router in user.routers:
        dp.include_router(router)

    await set_commands(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
