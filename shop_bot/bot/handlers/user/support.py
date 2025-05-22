from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import bot.keyboards as kb

router = Router()

@router.message(F.text.in_(['/help', '💬 Поддержка']))
async def contact_support(message: Message):
    await message.answer('Здесь будут способы связи с поддержкой.')