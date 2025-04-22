import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from decouple import config
from handlers import user, admin
from db.init import init_db


async def main():
    await init_db()
    bot = Bot(token=config('BOT_TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()

    dp.include_routers(user.router, admin.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
