from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List
from db.models import Favorite

def favorites_keyboard(favorites: List[Favorite]):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=favorite.product.name, callback_data=f'product_{favorite.product.id}')] for favorite in favorites
        ]
    )