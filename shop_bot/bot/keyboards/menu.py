from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🛍️ Каталог'), KeyboardButton(text='🛒 Корзина'), KeyboardButton(text='⭐ Избранное')],
            [KeyboardButton(text='📦 Мои заказы'), KeyboardButton(text='🏠 Мои адреса')],
            [KeyboardButton(text='⚙️ Настройки'), KeyboardButton(text='💬 Поддержка')]
        ],
        resize_keyboard=True
    )