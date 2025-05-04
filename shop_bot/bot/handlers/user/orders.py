from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

import keyboards.user_kb as kb
from db import crud, cart
from db.cart import ProductInCart


logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == 'place_an_order')
async def place_an_order(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    logger.info(f'Пользователь {user_id} начал оформление заказа')
    products: List[ProductInCart] = await cart.get_cart(session, user_id)
    
    if not products:
        await callback.answer('⚠️🛒 Невозможно оформить заказ: ваша корзина пуста.')
        return
    
    order = await crud.create_order(session, user_id)
    if order:
        await cart.clear_cart(user_id)
        await callback.message.answer(f'✅ Заказ №{order.id} оформлен! Мы свяжемся с вами.')
        logger.info(f'✅📦 Пользователь {user_id} оформил заказ №{order.id}')
    else:
        await callback.message.answer(f'❌ Произошла ошибка при оформлении заказа. Попробуйте еще раз.')
        logger.warning(f'❌📦 Пользователь {user_id} не смог оформить заказ')

@router.message(F.text.in_(['/orders', '📦 Мои заказы']))
async def show_orders(message: Message, session: AsyncSession):
    await message.answer('Здесь будут ваши заказы.')