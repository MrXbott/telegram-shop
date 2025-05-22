from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List
from math import ceil

from db.models import Order

# def orders_keyboard(orders: List[Order]):
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text=f'№ {order.id} - {order.created.strftime("%d.%m.%Y %H:%M")} - {order.status.status_name}', callback_data=f'order_{order.id}')] for order in orders
#         ]
#     )

def order_details_keyboard(order: Order):
    btns = []
    if order.status.status == 'waiting_for_payment':
        btns.append([InlineKeyboardButton(text='💳 Оплатить', callback_data=f'pay_for_the_order_{order.id}')])
    btns.append([InlineKeyboardButton(text='⬅️ Назад к заказам', callback_data='back_to_orders')])
    return InlineKeyboardMarkup(inline_keyboard=btns)

def order_name_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='👤 Использовать имя из профиля')]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def order_phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Отправить мой номер', request_contact=True)]
        ],
        resize_keyboard=True, 
        one_time_keyboard=True
    )

def confirm_order_details_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='💳 Оплатить', callback_data='confirm_order_and_pay')],
            [InlineKeyboardButton(text='⬅️ Изменить данные', callback_data='details_for_order')]
    ])

def orders_keyboard(
                orders: List[Order], 
                page_number: int, 
                orders_per_page: int, 
                ):
    start = (page_number - 1) * orders_per_page
    end = start + orders_per_page
    page_orders = orders[start:end]
    total_orders = len(orders)
    total_pages = ceil(total_orders/orders_per_page)

    keyboard=[[InlineKeyboardButton(text=f'№ {order.id} - {order.created.strftime("%d.%m.%Y %H:%M")} - {order.status.status_name}', callback_data=f'order_{order.id}')] for order in page_orders]
    
    pagination_btns = []
    if page_number > 1:
        pagination_btns.append(InlineKeyboardButton(text='⬅️', callback_data=f'orderspage_{page_number - 1}'))
    
    pagination_btns.append(InlineKeyboardButton(text=f'page {page_number} / {total_pages}', callback_data='ignore'))

    if page_number < total_pages:
        pagination_btns.append(InlineKeyboardButton(text='➡️', callback_data=f'orderspage_{page_number + 1}'))
    keyboard.append(pagination_btns)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)