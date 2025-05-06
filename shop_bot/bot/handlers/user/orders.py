from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

import keyboards.user_kb as kb
from db import crud, cart
from db.cart import ProductInCart
from utils.decorators import handle_db_errors
from texts import order_text


logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == 'place_an_order')
@handle_db_errors()
async def place_an_order(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    logger.info(f'Пользователь {user_id} начал оформление заказа')
    products: List[ProductInCart] = await cart.get_cart(session, user_id)
    
    if not products:
        await callback.answer('⚠️🛒 Невозможно оформить заказ: ваша корзина пуста.')
        return
    
    try:
        order = await crud.create_order(session, user_id)
    except ValueError as e:
        await callback.answer('⚠️Недостаточно товара в наличии чтобы оформить заказ')
        await callback.message.answer('⚠️Недостаточно товара в наличии чтобы оформить заказ')
        logger.error(f'❌ Недостаточно товара в наличии чтобы оформить заказ: {e}', exc_info=False)
    if order:
        await cart.clear_cart(user_id)
        await callback.message.edit_text(f'✅ Заказ №{order.id} оформлен! Мы свяжемся с вами.')
        logger.info(f'✅📦 Пользователь {user_id} оформил заказ №{order.id}')
    else:
        await callback.message.answer(f'❌ Произошла ошибка при оформлении заказа. Попробуйте еще раз.')
        logger.warning(f'❌📦 Пользователь {user_id} не смог оформить заказ')


@router.callback_query(F.data.startswith('order_'))
@handle_db_errors()
async def show_order(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    order_id = int(callback.data.split('_')[1])
    logger.info(f'📦 Пользователь {user_id} хочет просмотреть заказ №{order_id}')

    order = await crud.get_order(session, user_id, order_id)
    if order:
        await callback.message.edit_text(text=order_text(order, order.items), reply_markup=kb.order_keyboard()) 


async def show_orders(msg: Message|CallbackQuery, session: AsyncSession):
    user_id = msg.from_user.id
    orders = await crud.get_orders(session, user_id)
    text = 'Вот ваши заказы: ' if orders else 'У вас пока нет зказов'
    keyboard = kb.orders_keyboard(orders) if orders else None
    if isinstance(msg, Message):
        await msg.answer(text, reply_markup=keyboard)
    else:
        await msg.message.edit_text(text, reply_markup=keyboard)

@router.message(F.text.in_(['/orders', '📦 Мои заказы']))
@handle_db_errors()
async def show_all_orders(message: Message, session: AsyncSession):
    logger.info(f'📦 Пользователь {message.from_user.id} вызвал команду /orders')
    await show_orders(message, session)




@router.callback_query(F.data == 'back_to_orders')
async def back_to_orders(callback: CallbackQuery, session: AsyncSession):
    logger.info(f'📦 Пользователь {callback.from_user.id} вернулся к списку заказов')
    await show_orders(callback, session)