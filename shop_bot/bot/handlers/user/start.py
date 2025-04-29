from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

import keyboards.user_kb as kb
from db import crud


router = Router()


@router.message(F.text == '/start')
async def start(message: Message, session: AsyncSession):
    await crud.get_or_create_user(session, message.from_user.id, message.from_user.full_name)
    await message.answer('Добро пожаловать в магазин!', reply_markup=kb.main_keyboard())