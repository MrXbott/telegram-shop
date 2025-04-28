from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import keyboards.user_kb as kb
from db import crud, cart


router = Router()


@router.message(F.text == '🏠 Мои адреса')
async def show_addresses(message: Message):
    await message.answer('Здесь будут ваши адреса.')