from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import keyboards.user_kb as kb
from texts import product_text, cart_text
from db import crud, cart


router = Router()


@router.message(F.text.in_(['/orders', '📦 Мои заказы']))
async def show_orders(message: Message):
    await message.answer('Здесь будут ваши заказы.')