from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
import re

import keyboards.user_kb as kb
from db import crud, cart
from db.cart import ProductInCart
from utils.decorators import handle_db_errors
from utils.validators import is_valid_phone, normalize_phone, is_valid_name, is_valid_address
from texts import order_text
from exceptions.products import ProductOutOfStockError


logger = logging.getLogger(__name__)
router = Router()


class PlaceAnOrder(StatesGroup):
    waiting_for_address = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_confirmation = State()


@router.callback_query(F.data == 'details_for_order')
async def add_order_details(callback: CallbackQuery, state: FSMContext):
    logger.info(f'📦 Пользователь {callback.from_user.id} начал оформлять заказ.')
    await callback.message.answer('Укажите адрес доставки: \nУлицу, дом, подъезд, квартиру и этаж:')
    await state.set_state(PlaceAnOrder.waiting_for_address)


@router.message(PlaceAnOrder.waiting_for_address)
async def add_order_address(message: Message, state: FSMContext):
    address = message.text.strip()
    if not is_valid_address(address):
        await message.answer('Некорректный формат фдреса. Введите еще раз.')
        logger.warning(f'ℹ️ Пользователь {message.from_user.id} ввел некорректный адрес: {message.text}.')
        return
    
    logger.info(f'ℹ️ Пользователь {message.from_user.id} ввел адрес: {message.text}.')
    await state.update_data(address=address)
    await message.answer('Введите ваше имя:')
    await state.set_state(PlaceAnOrder.waiting_for_name)


@router.message(PlaceAnOrder.waiting_for_name)
async def add_order_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not is_valid_name(name):
        await message.answer('Некорректный формат имени. Введите еще раз.')
        logger.warning(f'ℹ️ Пользователь {message.from_user.id} ввел некорректное имя: {message.text}.')
        return
    
    logger.info(f'ℹ️ Пользователь {message.from_user.id} ввел имя: {message.text}.')
    await state.update_data(name=name)
    await message.answer('Введите ваш номер телефона:')
    await state.set_state(PlaceAnOrder.waiting_for_phone)


@router.message(PlaceAnOrder.waiting_for_phone)
async def add_order_phone(message: Message, state: FSMContext):
    phone = message.text.strip()    
    if not is_valid_phone(phone):
        await message.answer('❌ Некорректный номер телефона. Введите в формате: +7XXXXXXXXXX')
        logger.warning(f'ℹ️ Пользователь {message.from_user.id} ввел некорректный номер телефона: {message.text}.')
        return
    
    await state.update_data(phone=normalize_phone(phone))
    logger.info(f'ℹ️ Пользователь {message.from_user.id} ввел телефон: {message.text}.')
    data = await state.get_data()

    text = (
        f'Проверьте ваши данные:\n\n'
        f'📍 Адрес: {data['address']}\n'
        f'👤 Имя: {data['name']}\n'
        f'📞 Телефон: {data['phone']}\n\n'
        f'Все верно?'
    )
    await message.answer(text, reply_markup=kb.confirm_order_details_keyboard())
    await state.set_state(PlaceAnOrder.waiting_for_confirmation)


@router.callback_query(F.data == 'confirm_order')
@handle_db_errors()
async def place_an_order(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_id = callback.from_user.id

    # to do: check data 
    data = await state.get_data()
    products: List[ProductInCart] = await cart.get_cart(session, user_id)
    if not products:
        await callback.answer('⚠️🛒 Невозможно оформить заказ: ваша корзина пуста.')
        return
    
    try:
        order = await crud.create_order(session, user_id, data)
        await cart.clear_cart(user_id)
        await state.clear()
        await callback.message.edit_text(f'✅ Заказ №{order.id} оформлен! Мы свяжемся с вами.')
        logger.info(f'✅📦 Пользователь {user_id} оформил заказ №{order.id}')
    except ProductOutOfStockError as e:
        await callback.message.answer('⚠️Недостаточно товара в наличии чтобы оформить заказ')
        logger.error(f'❌ Недостаточно товара в наличии чтобы оформить заказ: {e}', exc_info=True)
    except Exception as e:
        await callback.message.answer(f'❌ Произошла ошибка при оформлении заказа. Попробуйте еще раз.')
        logger.error(f'❌ Произошла ошибка при оформлении заказа: {e}', exc_info=True)


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