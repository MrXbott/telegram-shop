from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import keyboards.user_kb as kb
from texts import product_text, cart_text
from db import crud, cart


router = Router()


@router.message(F.text == '⚙️ Настройки')
async def show_settings(message: Message):
    await message.answer('Здесь будут настройки.')