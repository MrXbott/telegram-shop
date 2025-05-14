from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.exceptions import TelegramBadRequest
from typing import List
import logging

import bot.keyboards.user_kb as kb
from bot.keyboards.addresses import choosing_address_keyboard
from db import crud, cart
from db.cart import ProductInCart
from utils.decorators import handle_db_errors
from utils.validators import is_valid_phone, normalize_phone, is_valid_name, is_valid_address
from bot.texts import order_text
from exceptions.db.products import ProductOutOfStockError
from bot.services.invoices import send_order_invoice
from bot.tasks import cancel_unpaid_order
from config import PROVIDER_TOKEN, UNPAID_ORDER_TIMEOUT
from exceptions.db.orders import OrderNotFound
from bot.services.exchange import ExchangeRateService, validate_payment_amount
from exceptions.bot.payments import TelegramPaymentLimitError

logger = logging.getLogger(__name__)
router = Router()
exchange_service = ExchangeRateService()


class PlaceAnOrder(StatesGroup):
    choosing_address = State()
    waiting_for_address_id = State()
    waiting_for_address_text = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_confirmation = State()


@router.callback_query(F.data == 'details_for_order')
async def add_order_details(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    products: List[ProductInCart] = await cart.get_cart(user_id)
    total_sum = 0
    for product in products:
        total_sum += product.quantity * product.product.price
    currency_code = 'USD'
    rate: float = await exchange_service.get_exchange_rate(currency_code)
    payment_amount: int = total_sum * 100
    try:
        validate_payment_amount(payment_amount, currency_code, rate)
    except TelegramPaymentLimitError as e:
        logger.error(f'❌ {str(e)}', exc_info=True)
        await callback.message.answer(f'❌ Невозможно оформить заказ: мин. сумма {e.min_amount} - макс. сумма {e.max_amount}')
        return
    
    addresses = await crud.get_user_addresses(user_id)
    logger.info(f'📦 Пользователь {user_id} начал оформлять заказ.')
    if addresses:
        await callback.message.edit_text('Выберите адрес доставки или введите новый:', reply_markup=choosing_address_keyboard(addresses))
        await state.set_state(PlaceAnOrder.choosing_address)
    else:
        await callback.message.answer('Укажите адрес доставки: \nУлицу, дом, подъезд, квартиру и этаж:')
        await state.set_state(PlaceAnOrder.waiting_for_address_text)


@router.callback_query(F.data.startswith('use_address_'), PlaceAnOrder.choosing_address)
async def use_saved_address(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    address_id = int(callback.data.split('_')[-1])
    address = await crud.get_address(user_id, address_id)
    
    if not address or address.is_deleted:
        await callback.message.answer('Адрес не найден.')
        return
    
    await state.update_data(address_id=address.id)
    await callback.message.edit_text(f'Вы указали адрес: <b>{address.address}</b>')
    await callback.message.answer('Введите ваше имя:', reply_markup=kb.order_name_keyboard())
    await state.set_state(PlaceAnOrder.waiting_for_name)

@router.callback_query(F.data == 'enter_new_address', PlaceAnOrder.choosing_address)
async def enter_new_address(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Укажите адрес доставки: \nУлицу, дом, подъезд, квартиру и этаж:')
    await state.set_state(PlaceAnOrder.waiting_for_address_text)

@router.message(PlaceAnOrder.waiting_for_address_text)
async def add_order_address(message: Message, state: FSMContext):
    address = message.text.strip()
    if not is_valid_address(address):
        await message.answer('Некорректный формат фдреса. Введите еще раз.')
        logger.warning(f'ℹ️ Пользователь {message.from_user.id} ввел некорректный адрес: {message.text}.')
        return
    
    logger.info(f'ℹ️ Пользователь {message.from_user.id} ввел адрес: {message.text}.')
    await state.update_data(address_text=address)
    await message.answer('Введите ваше имя:', reply_markup=kb.order_name_keyboard())
    await state.set_state(PlaceAnOrder.waiting_for_name)

@router.message(PlaceAnOrder.waiting_for_name, F.text == '👤 Использовать имя из профиля')
async def handle_user_name(message: Message, state: FSMContext):
    name = message.from_user.full_name
    await state.update_data(name=name)
    await message.answer(f'Ваше имя из профиля: <b>{name}</b>')
    await message.answer('Введите ваш номер телефона:', reply_markup=kb.order_phone_keyboard())
    await state.set_state(PlaceAnOrder.waiting_for_phone)

@router.message(PlaceAnOrder.waiting_for_name)
async def add_order_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not is_valid_name(name):
        await message.answer('Некорректный формат имени. Введите еще раз.')
        logger.warning(f'ℹ️ Пользователь {message.from_user.id} ввел некорректное имя: {message.text}.')
        return
    
    logger.info(f'ℹ️ Пользователь {message.from_user.id} ввел имя: {message.text}.')
    await state.update_data(name=name)
    await message.answer(f'Ваше имя: <b>{name}</b>')
    await message.answer('Введите ваш номер телефона:', reply_markup=kb.order_phone_keyboard())
    await state.set_state(PlaceAnOrder.waiting_for_phone)

@router.message(PlaceAnOrder.waiting_for_phone, F.contact)
async def handle_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=normalize_phone(phone))
    logger.info(f'ℹ️ Пользователь {message.from_user.id} отправил телефон: {phone}.')
    await show_order_details(message, state)

@router.message(PlaceAnOrder.waiting_for_phone, F.text)
async def add_order_phone(message: Message, state: FSMContext):
    user_id = message.from_user.id
    phone = message.text.strip()  

    if not is_valid_phone(phone):
        await message.answer('❌ Некорректный номер телефона. Введите в формате: +7XXXXXXXXXX')
        logger.warning(f'ℹ️ Пользователь {user_id} ввел некорректный номер телефона: {message.text}.')
        return
    
    await state.update_data(phone=normalize_phone(phone))
    logger.info(f'ℹ️ Пользователь {message.from_user.id} ввел телефон: {message.text}.')
    await message.answer(f'Ваш номер телефона: <b>{phone}</b>', reply_markup=ReplyKeyboardRemove())
    await show_order_details(message, state)

async def show_order_details(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    address_id = data.get('address_id')
    address_text = data.get('address_text')
    
    address = None
    if address_id:
        address = await crud.get_address(user_id, address_id)
    text = (
        f'Проверьте ваши данные:\n\n'
        f'📍 Адрес: <b>{address.address if address else address_text}</b>\n'
        f'👤 Имя: <b>{data['name']}</b>\n'
        f'📞 Телефон: <b>{data['phone']}</b>\n\n'
    )
    await message.answer(text, reply_markup=kb.confirm_order_details_keyboard())
    await state.set_state(PlaceAnOrder.waiting_for_confirmation)


@router.callback_query(F.data == 'confirm_order_and_pay')
@handle_db_errors()
async def place_an_order(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    # to do: check data 
    data = await state.get_data()

    products: List[ProductInCart] = await cart.get_cart(user_id)
    if not products:
        await callback.answer('⚠️🛒 Невозможно оформить заказ: ваша корзина пуста.')
        return

    try:
        order = await crud.create_order(user_id, data)
        await crud.update_order_status(user_id, order.id, 'waiting_for_payment')

        cancel_unpaid_order.apply_async(args=[user_id, order.id], countdown=UNPAID_ORDER_TIMEOUT)

        await cart.clear_cart(user_id)

        await send_order_invoice(callback.bot, callback.message.chat.id, order, PROVIDER_TOKEN)
        
        await state.clear()
        await callback.message.delete_reply_markup()

        logger.info(f'✅📦 Пользователь {user_id} оформил заказ №{order.id} и получил счёт на оплату.')

    except ProductOutOfStockError as e:
        await callback.message.answer('⚠️Недостаточно товара в наличии чтобы оформить заказ', reply_markup=kb.main_keyboard())
        logger.error(f'❌ Недостаточно товара в наличии чтобы оформить заказ: {e}', exc_info=True)
    except TelegramBadRequest as e:
        await callback.message.answer(f'❌ Произошла ошибка при совершении платежа. Попробуйте еще раз. Номер вашего заказа: <b>{order.id}</b>', reply_markup=kb.main_keyboard())
        logger.error(f'❌ Произошла ошибка при совершении платежа.: {e}', exc_info=True)
    except Exception as e:
        await callback.message.answer(f'❌ Произошла ошибка при оформлении заказа. Попробуйте еще раз.', reply_markup=kb.main_keyboard())
        logger.error(f'❌ Произошла ошибка при оформлении заказа: {e}', exc_info=True)


@router.callback_query(F.data.startswith('order_'))
@handle_db_errors()
async def show_order(callback: CallbackQuery):
    user_id = callback.from_user.id
    order_id = int(callback.data.split('_')[1])
    logger.info(f'📦 Пользователь {user_id} хочет просмотреть свой заказ №{order_id}')

    try:
        order = await crud.get_order(user_id, order_id)
    except OrderNotFound:
        await callback.message.answer(text='⚠️ Что-то пошло не так. Заказ не найден.') 
        return
    await callback.message.edit_text(text=order_text(order, order.items), reply_markup=kb.order_details_keyboard(order)) 


async def show_orders(msg: Message|CallbackQuery):
    user_id = msg.from_user.id
    orders = await crud.get_user_orders(user_id)
    text = 'Вот ваши заказы: ' if orders else 'У вас пока нет зказов'
    keyboard = kb.orders_keyboard(orders) if orders else None
    if isinstance(msg, Message):
        await msg.answer(text, reply_markup=keyboard)
    else:
        await msg.message.edit_text(text, reply_markup=keyboard)


@router.message(F.text.in_(['/orders', '📦 Мои заказы']))
@handle_db_errors()
async def show_user_orders(message: Message):
    logger.info(f'📦 Пользователь {message.from_user.id} вызвал команду /orders')
    await show_orders(message)


@router.callback_query(F.data == 'back_to_orders')
async def back_to_orders(callback: CallbackQuery):
    logger.info(f'📦 Пользователь {callback.from_user.id} вернулся к списку заказов')
    await show_orders(callback)