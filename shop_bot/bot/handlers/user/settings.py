from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import bot.keyboards as kb

router = Router()

@router.message(F.text == '⚙️ Настройки')
async def show_settings(message: Message):
    await message.answer('Здесь будут настройки.')