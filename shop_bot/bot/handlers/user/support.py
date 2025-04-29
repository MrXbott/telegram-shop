from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

import keyboards.user_kb as kb


router = Router()


@router.message(F.text.in_(['/help', '💬 Поддержка']))
async def contact_support(message: Message, session: AsyncSession):
    await message.answer('Здесь будут способы связи с поддержкой.')