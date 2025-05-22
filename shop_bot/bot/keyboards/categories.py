from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List
from db.models import Category

def categories_keyboard(categories: List[Category]):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f'{category.name}', callback_data=f'category_{category.id}')] 
            for category in categories
        ]
    )