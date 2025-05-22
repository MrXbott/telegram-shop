from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
import logging

import bot.keyboards as kb
from db import crud
from utils.decorators import handle_db_errors

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text == '/start')
@handle_db_errors()
async def start(message: Message):
    logger.info(f'Пользователь {message.from_user.id} вызвал команду /start')
    await crud.get_or_create_user(message.from_user.id, message.from_user.full_name)
    await message.answer('Добро пожаловать в магазин!', reply_markup=kb.menu_keyboard())