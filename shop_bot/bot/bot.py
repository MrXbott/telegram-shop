import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from decouple import config
from handlers import user, admin
from db.init import init_db, async_session
from middlewares.session import DBSessionMiddleware
from middlewares.error import ErrorLoggingMiddleware
from commands import set_commands
from logging_config import setup_logging

setup_logging()

async def main():
    await init_db()
    bot = Bot(token=config('BOT_TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()

    dp.update.middleware(DBSessionMiddleware(async_session))
    dp.update.middleware(ErrorLoggingMiddleware())

    dp.include_routers(admin.router)
    for r in user.routers:
        dp.include_router(r)

    await set_commands(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
