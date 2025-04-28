import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from decouple import config
from handlers import user, admin
from db.init import init_db
from commands import set_commands


async def main():
    await init_db()
    bot = Bot(token=config('BOT_TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()

    dp.include_routers(admin.router)
    for r in user.routers:
        dp.include_router(r)

    await set_commands(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
