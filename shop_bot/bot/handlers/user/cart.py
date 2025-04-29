from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
import logging

import keyboards.user_kb as kb
from texts import cart_text
from db import crud, cart


logger = logging.getLogger(__name__)
router = Router()


@router.message(F.text.in_(['/cart', '🛒 Корзина']))
async def show_cart(message: Message, session: AsyncSession):
    products = await cart.get_cart(session, message.from_user.id)
    if not products:
        await message.answer('Корзина пуста.')
        return
    await message.answer(cart_text(products), reply_markup=kb.cart_keyboard())
    logger.info(f'🛒 Пользователь {message.from_user.id} вызвал команду /cart')


@router.callback_query(F.data.startswith('add_'))
async def add_product_to_cart(callback: CallbackQuery, session: AsyncSession):
    product_id = int(callback.data.split('_')[1])
    user_id = callback.from_user.id
    product = await crud.get_product(session, product_id)
    is_favorite = await crud.is_in_favorites(session, user_id, product_id)
    if product:
        await cart.add_to_cart(user_id, product_id, 1)
        await callback.message.edit_reply_markup(reply_markup=kb.product_keyboard(product, is_favorite, 1))
        await callback.answer('Добавлено в корзину')
    logger.info(f'📥 Пользователь {callback.from_user.id} добавил в корзину продукт {product_id}')
    

@router.callback_query(F.data.startswith('increase_'))
async def increase_product_quantity(callback: CallbackQuery, session: AsyncSession):
    product_id = int(callback.data.split('_')[1])
    user_id = callback.from_user.id
    quantity = await cart.get_product_quantity(user_id, product_id)
    new_quantity = await cart.increase_quantity(user_id, product_id)
    product = await crud.get_product(session, product_id)
    is_favorite = await crud.is_in_favorites(session, user_id, product_id)
    if product:
        await callback.message.edit_reply_markup(reply_markup=kb.product_keyboard(product, is_favorite, new_quantity))
    await callback.answer()
    logger.info(f'🔺 Пользователь {callback.from_user.id} увеличил количество продукта {product_id}: {quantity} -> {new_quantity}')


@router.callback_query(F.data.startswith('decrease_'))
async def decrease_product_quantity(callback: CallbackQuery, session: AsyncSession):
    product_id = int(callback.data.split('_')[1])
    user_id = callback.from_user.id
    quantity = await cart.get_product_quantity(user_id, product_id)
    new_quantity = await cart.decrease_quantity(user_id, product_id)
    product = await crud.get_product(session, product_id)
    is_favorite = await crud.is_in_favorites(session, user_id, product_id)
    if product:
        await callback.message.edit_reply_markup(reply_markup=kb.product_keyboard(product, is_favorite, new_quantity))
    await callback.answer()
    logger.info(f'🔻 Пользователь {callback.from_user.id} уменьшил количество продукта {product_id}: {quantity} -> {new_quantity}')


@router.callback_query(F.data.startswith('remove_'))
async def remove_product_from_cart(callback: CallbackQuery, session: AsyncSession):
    product_id = int(callback.data.split('_')[1])
    user_id = callback.from_user.id
    await cart.remove_from_cart(user_id, product_id)
    product = await crud.get_product(session, product_id)
    is_favorite = await crud.is_in_favorites(session, user_id, product_id)
    if product:
        await callback.message.edit_reply_markup(reply_markup=kb.product_keyboard(product, is_favorite, quantity=0))
    await callback.answer('Удалено из корзины!')
    logger.info(f'📤 Пользователь {callback.from_user.id} удалил из корзины продукт {product_id}')


@router.callback_query(F.data == 'ignore')
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()
    logger.info(f'Пользователь {callback.from_user.id} нажал кнопку с количеством')


@router.callback_query(F.data == 'clear_cart')
async def clear_cart(callback: CallbackQuery):
    await cart.clear_cart(callback.from_user.id)
    await callback.message.edit_text('Корзина очищена.')
    logger.info(f'🛒❌ Пользователь {callback.from_user.id} очистил корзину')
