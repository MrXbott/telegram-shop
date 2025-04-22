from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🛍️ Каталог'), KeyboardButton(text='🛒 Корзина')],
            [KeyboardButton(text='📦 Мои заказы'), KeyboardButton(text='🏠 Мои адреса')],
            [KeyboardButton(text='⚙️ Настройки'), KeyboardButton(text='💬 Поддержка')]
        ],
        resize_keyboard=True
    )

def catalog_keyboard(products):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f'{product.name} - {product.price}', callback_data=f'product_{product.id}')]
            for product in products
        ]
    )

def product_keyboard(id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🛒 Добавить в корзину', callback_data=f'add_{id}')],
            [InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_catalog')]
        ]
    )

def cart_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='✅ Оформить заказ', callback_data='checkout')],
            [InlineKeyboardButton(text='🗑 Очистить', callback_data='clear_cart')],
        ]
    )
