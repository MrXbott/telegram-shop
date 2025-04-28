from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import keyboards.user_kb as kb
from db import crud


router = Router()


async def get_catalog(msg: Message|CallbackQuery):
    categories = await crud.categories.get_categories()
    text = 'Вот каталог товаров!'
    keyboard = kb.categories_keyboard(categories)
    if isinstance(msg, Message):
        await msg.answer(text, reply_markup=keyboard)
    else:
        await msg.message.edit_text(text, reply_markup=keyboard)


@router.message(F.text.in_(['/catalog', '🛍️ Каталог']))
async def show_catalog(message: Message):
    await get_catalog(message)


@router.callback_query(F.data == 'back_to_catalog')
async def back_to_catalog(callback: CallbackQuery):
    await get_catalog(callback)