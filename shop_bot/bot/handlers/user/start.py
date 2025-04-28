from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import keyboards.user_kb as kb
from texts import product_text, cart_text
from db import crud, cart


router = Router()


@router.message(F.text == '/start')
async def start(message: Message):
    await crud.get_or_create_user(message.from_user.id, message.from_user.full_name)
    await message.answer('Добро пожаловать в магазин!', reply_markup=kb.main_keyboard())