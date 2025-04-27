from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, FSInputFile, ContentType
import os

from db import crud
import keyboards.user_kb as kb
from texts import product_text, cart_text
from config import MEDIA_FOLDER_PATH
import cart


router = Router()


async def get_catalog(msg: Message|CallbackQuery):
    categories = await crud.get_categories()
    text = 'Вот каталог товаров!'
    keyboard = kb.categories_keyboard(categories)
    if isinstance(msg, Message):
        await msg.answer(text, reply_markup=keyboard)
    else:
        await msg.message.edit_text(text, reply_markup=keyboard)


@router.message(F.text == '/start')
async def start(message: Message):
    await crud.get_or_create_user(message.from_user.id, message.from_user.full_name)
    await message.answer('Добро пожаловать в магазин!', reply_markup=kb.main_keyboard())


@router.message(F.text.in_(['/catalog', '🛍️ Каталог']))
async def show_catalog(message: Message):
    await get_catalog(message)


@router.message(F.text.in_(['/cart', '🛒 Корзина']))
async def show_cart(message: Message):
    products = await cart.get_cart(message.from_user.id)
    if not products:
        await message.answer('Корзина пуста.')
        return
    await message.answer(cart_text(products), reply_markup=kb.cart_keyboard())


@router.message(F.text == '📦 Мои заказы')
async def show_orders(message: Message):
    await message.answer('Здесь будут ваши заказы.')


@router.message(F.text == '🏠 Мои адреса')
async def show_addresses(message: Message):
    await message.answer('Здесь будут ваши адреса.')


@router.message(F.text == '⚙️ Настройки')
async def show_settings(message: Message):
    await message.answer('Здесь будут настройки.')


@router.message(F.text == '💬 Поддержка')
async def contact_support(message: Message):
    await message.answer('Здесь будут способы связи с поддержкой.')


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
    product = await crud.get_product(product_id)
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
                reply_markup=kb.product_keyboard(product)
            )

@router.callback_query(F.data.startswith('add_'))
async def add_to_cart(callback: CallbackQuery):
    product_id = int(callback.data.split('_')[1])
    user_id = callback.from_user.id
    await cart.add_to_cart(user_id, product_id, 1)
    await callback.answer('Добавлено в корзину')


@router.callback_query(F.data == 'back_to_catalog')
async def back_to_catalog(callback: CallbackQuery):
    await get_catalog(callback)


@router.callback_query(F.data == 'clear_cart')
async def clear_cart(callback: CallbackQuery):
    await cart.clear_cart(callback.from_user.id)
    await callback.message.edit_text('Корзина очищена.')
