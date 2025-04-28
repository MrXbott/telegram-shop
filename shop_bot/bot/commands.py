from aiogram.types import BotCommand
from aiogram import Bot


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description='Начать работу'),
        BotCommand(command='catalog', description='Каталог'),
        BotCommand(command='cart', description='Корзина'),
        BotCommand(command='favorites', description='Избранное'),
        BotCommand(command='orders', description='Заказы'),
        BotCommand(command='addresses', description='Адреса'),
        BotCommand(command='help', description='Помощь'),
    ]
    await bot.set_my_commands(commands)