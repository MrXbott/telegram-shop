from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

import keyboards.user_kb as kb
from db import crud


router = Router()


@router.message(F.text.in_(['/addresses', '🏠 Мои адреса']))
async def show_addresses(message: Message, session: AsyncSession):
    await message.answer('Здесь будут ваши адреса.')