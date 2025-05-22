from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def cart_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='✅ Оформить заказ', callback_data='details_for_order')],
            [InlineKeyboardButton(text='🗑 Очистить', callback_data='clear_cart')],
        ]
    )