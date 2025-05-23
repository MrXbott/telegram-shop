from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import logging

import bot.keyboards as kb
from db import crud
from utils.decorators import handle_db_errors

logger = logging.getLogger(__name__)
router = Router()

async def get_categories(msg: Message|CallbackQuery):
    categories = await crud.get_categories()
    text = 'Вот каталог товаров!'
    keyboard = kb.categories_keyboard(categories)
    if isinstance(msg, Message):
        await msg.answer(text, reply_markup=keyboard)
    else:
        await msg.message.edit_text(text, reply_markup=keyboard)

@router.message(F.text.in_(['/catalog', '🛍️ Каталог']))
@handle_db_errors()
async def show_catalog(message: Message):  
    await get_categories(message)
    logger.info(f'🛍️ Пользователь {message.from_user.id} вызвал команду /catalog')

@router.callback_query(F.data == 'back_to_catalog')
@handle_db_errors()
async def back_to_catalog(callback: CallbackQuery):
    await get_categories(callback)
    logger.info(f'🛍️ Пользователь {callback.from_user.id} вернулся в каталог из категории')