from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
import logging

import keyboards.user_kb as kb
from db import crud


logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text.in_(['/addresses', '🏠 Мои адреса']))
async def show_addresses(message: Message, session: AsyncSession):
    logger.info(f'Пользователь {message.from_user.id} вызвал команду /addresses')
    await message.answer('Здесь будут ваши адреса.')