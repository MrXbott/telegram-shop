from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List
from math import ceil
from db.models import Address


def address_list_keyboard(addresses: List[Address]):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            *[[InlineKeyboardButton(text=address.address, callback_data=f'address_{address.id}')] for address in addresses],
            [InlineKeyboardButton(text='🏠 Добавить адрес', callback_data='new_address')],
        ]
    )

def address_details_keyboard(address: Address):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Удалить', callback_data=f'delete_address_{address.id}')],
            [InlineKeyboardButton(text='Назад к адресам', callback_data='back_to_addresses')],
        ]
    )