from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from db import crud
from db.redis import redis_client
from keyboards.user_kb import catalog_keyboard, product_keyboard, cart_keyboard, main_keyboard
from texts import product_text, cart_text
import cart

router = Router()

@router.message(F.text == '/start')
async def start(message: Message):
    await crud.get_or_create_user(message.from_user.id, message.from_user.full_name)
    await message.answer('Добро пожаловать в магазин!', reply_markup=main_keyboard())


@router.message(F.text.in_(['/catalog', '🛍️ Каталог']))
async def show_catalog(message: Message):
    products = await crud.get_all_products()
    await message.answer('Вот каталог товаров!', reply_markup=catalog_keyboard(products))


@router.message(F.text.in_(['/cart', '🛒 Корзина']))
async def show_cart(message: Message):
    products = await cart.get_cart(message.from_user.id)
    if not products:
        await message.answer('Корзина пуста.')
        return
    await message.answer(cart_text(products), reply_markup=cart_keyboard())


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


@router.callback_query(F.data.startswith('product_'))
async def show_product(callback: CallbackQuery):
    product_id = int(callback.data.split('_')[1])
    product = await crud.get_product(product_id)
    if product:
        await callback.message.edit_text(
            product_text(product),
            reply_markup=product_keyboard(product.id)
        )

@router.callback_query(F.data.startswith('add_'))
async def add_to_cart(callback: CallbackQuery):
    product_id = int(callback.data.split('_')[1])
    user_id = callback.from_user.id
    await cart.add_to_cart(user_id, product_id, 1)
    await callback.answer('Добавлено в корзину')


@router.callback_query(F.data == 'back_to_catalog')
async def back_to_catalog(callback: CallbackQuery):
    products = await crud.get_all_products()
    if not products:
        await callback.message.edit_text('Нет товаров в каталоге.')
        return
    await callback.message.edit_text('Каталог товаров', reply_markup=catalog_keyboard(products))


@router.callback_query(F.data == 'clear_cart')
async def clear_cart(callback: CallbackQuery):
    await cart.clear_cart(callback.from_user.id)
    await callback.message.edit_text('Корзина очищена.')
