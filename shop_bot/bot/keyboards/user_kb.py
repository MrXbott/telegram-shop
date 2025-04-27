from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List
from db.models import Product, Category

def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🛍️ Каталог'), KeyboardButton(text='🛒 Корзина')],
            [KeyboardButton(text='📦 Мои заказы'), KeyboardButton(text='🏠 Мои адреса')],
            [KeyboardButton(text='⚙️ Настройки'), KeyboardButton(text='💬 Поддержка')]
        ],
        resize_keyboard=True
    )

def categories_keyboard(categories: List[Category]):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f'{category.name}', callback_data=f'category_{category.id}')] 
            for category in categories
        ]
    )

def products_keyboard(products: List[Product]):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            *[[InlineKeyboardButton(text=f'{product.name} - {product.price}', callback_data=f'product_{product.id}')] for product in products],
            [InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_catalog')]
            ]
    )

def product_keyboard(product: Product, quantity: int = 0):
    if quantity > 0:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='➖', callback_data=f'decrease_{product.id}'),
                    InlineKeyboardButton(text=f'{quantity}', callback_data='ignore'),
                    InlineKeyboardButton(text='➕', callback_data=f'increase_{product.id}')
                ],
                [InlineKeyboardButton(text='🗑️ Удалить из корзины', callback_data=f'remove_{product.id}')],
                [InlineKeyboardButton(text='⬅️ Назад', callback_data=f'category_{product.category_id}')]
            ]
        )
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='🛒 Добавить в корзину', callback_data=f'add_{product.id}')],
                [InlineKeyboardButton(text='⬅️ Назад', callback_data=f'category_{product.category_id}')]
            ]
        )

def cart_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='✅ Оформить заказ', callback_data='checkout')],
            [InlineKeyboardButton(text='🗑 Очистить', callback_data='clear_cart')],
        ]
    )
