from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile, ContentType
import os
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from config import MEDIA_FOLDER_PATH
import keyboards.user_kb as kb
from texts import product_text
from db import crud, cart
from utils.decorators import handle_db_errors


logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith('category_'))
@handle_db_errors()
async def show_products(callback: CallbackQuery, session: AsyncSession):
    category_id = int(callback.data.split('_')[1])
    category = await crud.get_category_with_products(session, category_id)
    
    if callback.message.content_type == ContentType.TEXT:
        await callback.message.edit_text(f'Товары в категории {category.name}', 
                                     reply_markup=kb.products_keyboard(category.products)
                                     )
    elif callback.message.content_type == ContentType.PHOTO:
            await callback.message.delete()
            await callback.message.answer(f'Товары в категории {category.name}', 
                                     reply_markup=kb.products_keyboard(category.products)
                                     )
    logger.info(f'📂 Пользователь {callback.from_user.id} просматривает товары из категории {category_id} - {category.name}')
            

@router.callback_query(F.data.startswith('product_'))
@handle_db_errors()
async def show_product(callback: CallbackQuery, session: AsyncSession):
    product_id = int(callback.data.split('_')[1])
    user_id = callback.from_user.id
    product = await crud.get_product(session, product_id)
    quantity = await cart.get_product_quantity(user_id, product_id)
    is_favorite = await crud.is_in_favorites(session, user_id, product_id)

    if product:
        if product.image:
            photo_path = os.path.join(MEDIA_FOLDER_PATH, product.image)
        else:
            photo_path = os.path.join(MEDIA_FOLDER_PATH, 'no_photo.png')
        photo = FSInputFile(photo_path)
        await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=photo,
                    caption=product_text(product) 
                ),
                reply_markup=kb.product_keyboard(product, is_favorite, quantity)
            )
    logger.info(f'🍏 Пользователь {callback.from_user.id} просматривает товар {product_id} - {product.name} из категории {product.category_id} - {product.category.name}')