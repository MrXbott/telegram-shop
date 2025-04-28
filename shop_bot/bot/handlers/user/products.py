from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile, ContentType
import os

from config import MEDIA_FOLDER_PATH
import keyboards.user_kb as kb
from texts import product_text
from db import crud, cart


router = Router()


@router.callback_query(F.data.startswith('category_'))
async def show_products(callback: CallbackQuery):
    category_id = int(callback.data.split('_')[1])
    category = await crud.get_category_with_products(category_id)
    
    if callback.message.content_type == ContentType.TEXT:
        await callback.message.edit_text(f'Товары в категории {category.name}', 
                                     reply_markup=kb.products_keyboard(category.products)
                                     )
    elif callback.message.content_type == ContentType.PHOTO:
            await callback.message.delete()
            await callback.message.answer(f'Товары в категории {category.name}', 
                                     reply_markup=kb.products_keyboard(category.products)
                                     )
            

@router.callback_query(F.data.startswith('product_'))
async def show_product(callback: CallbackQuery):
    product_id = int(callback.data.split('_')[1])
    user_id = callback.from_user.id
    product = await crud.get_product(product_id)
    quantity = await cart.get_product_quantity(user_id, product_id)
    is_favorite = await crud.is_in_favorites(user_id, product_id)

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