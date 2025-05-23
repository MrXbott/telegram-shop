from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import logging

import bot.keyboards as kb
from db import crud, cart
from utils.decorators import handle_db_errors

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data.startswith('favorites_'))
@handle_db_errors()
async def add_to_favorites(callback: CallbackQuery):
    product_id = int(callback.data.split('_')[-1])
    user_id = callback.from_user.id
    product = await crud.get_product(product_id)
    quantity = await cart.get_product_quantity(user_id, product_id)
    is_favorite = await crud.is_in_favorites(user_id, product_id)
    if is_favorite:
        await crud.remove_from_favorites(user_id, product_id)
        await callback.answer('Удалено из избранного ❌')
        logger.info(f'❌ Пользователь {callback.from_user.id} удалил из избранного продукт {product_id}')
    else:
        await crud.add_to_favorites(user_id, product_id)
        await callback.answer('Добавлено в избранное ⭐')
        logger.info(f'⭐ Пользователь {callback.from_user.id} добавил в избранное продукт {product_id}')
    await callback.message.edit_reply_markup(reply_markup=kb.product_keyboard(product, (not is_favorite), quantity))
    


@router.message(F.text.in_(['/favorites', '⭐ Избранное']))
@handle_db_errors()
async def show_favorites(message: Message):
    logger.info(f'Пользователь {message.from_user.id} вызвал команду /favorites')
    user_id = message.from_user.id
    favorites = await crud.get_user_favorites(user_id)
    if favorites:
        await message.answer('Ваше избранное.', reply_markup=kb.favorites_keyboard(favorites))
    else:
        await message.answer('В избранном пока ничего нет. Добавьте что нравится.')