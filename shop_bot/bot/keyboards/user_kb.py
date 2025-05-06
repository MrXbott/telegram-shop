from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List
from math import ceil
from db.models import Product, Category, Favorite, Order


def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🛍️ Каталог'), KeyboardButton(text='🛒 Корзина'), KeyboardButton(text='⭐ Избранное')],
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

def products_keyboard(
                category: Category, 
                products: List[Product], 
                offset: int, 
                products_per_page: int, 
                total_products: int
                ):
    keyboard=[[InlineKeyboardButton(text=f'{product.name} - {product.price}₽', callback_data=f'product_{product.id}')] for product in products]
    
    pagination_btns = []
    if offset > 0:
        pagination_btns.append(InlineKeyboardButton(text='⬅️', callback_data=f'category_{category.id}_{offset - products_per_page}'))
    
    current_page = int(offset / products_per_page + 1)
    total_pages = ceil(total_products/products_per_page)
    pagination_btns.append(InlineKeyboardButton(text=f'page {current_page} / {total_pages}', callback_data='ignore'))

    if offset + products_per_page < total_products:
        pagination_btns.append(InlineKeyboardButton(text='➡️', callback_data=f'category_{category.id}_{offset + products_per_page}'))
    keyboard.append(pagination_btns)
    keyboard.append([InlineKeyboardButton(text='⬅️ Назад к категориям', callback_data='back_to_catalog')])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def product_keyboard(product: Product, is_favorite: bool, quantity: int = 0):
    favorite_text = '⭐ В избранном' if is_favorite else '⭐ Добавить в избранное'
    if quantity > 0:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='➖', callback_data=f'decrease_{product.id}'),
                    InlineKeyboardButton(text=f'{quantity}', callback_data='ignore'),
                    InlineKeyboardButton(text='➕', callback_data=f'increase_{product.id}')
                ],
                [InlineKeyboardButton(text='🗑️ Удалить из корзины', callback_data=f'remove_{product.id}')],
                [InlineKeyboardButton(text=favorite_text, callback_data=f'favorites_{product.id}')],
                [InlineKeyboardButton(text='⬅️ Назад', callback_data=f'category_{product.category_id}')]
            ]
        )
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='🛒 Добавить в корзину', callback_data=f'add_{product.id}')],
                [InlineKeyboardButton(text=favorite_text, callback_data=f'favorites_{product.id}')],
                [InlineKeyboardButton(text='⬅️ Назад', callback_data=f'category_{product.category_id}')]
            ]
        )
    
def not_available_product_keyboard(product: Product):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='⬅️ Назад', callback_data=f'category_{product.category_id}')]
        ]
    )

def cart_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='✅ Оформить заказ', callback_data='details_for_order')],
            [InlineKeyboardButton(text='🗑 Очистить', callback_data='clear_cart')],
        ]
    )

def favorites_keyboard(favorites: List[Favorite]):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=favorite.product.name, callback_data=f'product_{favorite.product.id}')] for favorite in favorites
        ]
    )

def orders_keyboard(orders: List[Order]):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f'№ {order.id} - {order.created.strftime("%d.%m.%Y %H:%M")}', callback_data=f'order_{order.id}')] for order in orders
        ]
    )


def order_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='⬅️ Назад к заказам', callback_data='back_to_orders')]
        ]
    )

def confirm_order_details_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='✅ Оформить', callback_data='confirm_order')],
            # [InlineKeyboardButton(text='⬅️ Назад', callback_data='edit_order')]
    ])