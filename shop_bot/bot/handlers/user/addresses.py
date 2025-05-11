from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
import logging

import bot.keyboards.addresses as kb
from db import crud
from db.models import Address
from utils.validators import is_valid_address
from utils.decorators import handle_db_errors


logger = logging.getLogger(__name__)
router = Router()

class AddNewAddress(StatesGroup):
    waiting_for_address = State()


async def user_addresses(msg: Message|CallbackQuery, session: AsyncSession):
    user_id = msg.from_user.id
    addresses = await crud.get_user_addresses(session, user_id)
    if not addresses:
        await msg.answer('Здесь будут ваши адреса доставки. Пока адресов нет.', reply_markup=kb.add_address_keyboard())
        return
    text = 'Список ваших адресов доставки:'
    keyboard = kb.address_list_keyboard(addresses)
    if isinstance(msg, Message):
        await msg.answer(text, reply_markup=keyboard)
    else:
        await msg.message.edit_text(text, reply_markup=keyboard)

@router.message(F.text.in_(['/addresses', '🏠 Мои адреса']))
@handle_db_errors()
async def show_user_addresses(message: Message, session: AsyncSession):
    logger.info(f'🏠 Пользователь {message.from_user.id} вызвал команду /addresses')
    await user_addresses(message, session)

@router.callback_query(F.data == 'back_to_addresses')
@handle_db_errors()
async def back_to_addresses(callback: CallbackQuery, session: AsyncSession):
    logger.info(f'🏠 Пользователь {callback.from_user.id} вернулся к списку адресов')
    await user_addresses(callback, session)

@router.callback_query(F.data == 'new_address')
async def add_new_address(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_id = callback.from_user.id
    logger.info(f'🏠 Пользователь {user_id} хочет добавить новый адрес.')
    address_count = await crud.count_user_addresses(session, user_id)
    if address_count < 5:
        await callback.message.answer('Введите адрес: улица, дом, подъезд, квартира и этаж')
        await state.set_state(AddNewAddress.waiting_for_address)
    else:
        await callback.message.answer(text='У вас максимальное количество адресов')

@router.message(AddNewAddress.waiting_for_address)
@handle_db_errors()
async def save_new_address(message: Message, state: FSMContext, session: AsyncSession):
    address = message.text.strip()
    if not is_valid_address(address):
        await message.answer('Некорректный формат фдреса. Введите еще раз.')
        logger.warning(f'ℹ️ Пользователь {message.from_user.id} ввел некорректный адрес: {message.text}.')
        return
    
    logger.info(f'ℹ️ Пользователь {message.from_user.id} ввел адрес: {address}.')
    await state.update_data(address=address)
    
    data = await state.get_data()
    user_id = message.from_user.id
    try:
        new_address: Address = await crud.add_new_address(session, user_id, data.get('address'))
        await state.clear()
        await message.answer(f'✅ Ваш адрес добавлен: {new_address.address}')
        logger.info(f'✅ Пользователь {user_id} добавил адрес с id {new_address.id}')
    except Exception as e:
        logger.error(f'❌ Произошла ошибка при добавлении адреса: {e}', exc_info=True)

@router.callback_query(F.data.startswith('address_'))
@handle_db_errors()
async def show_address(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    address_id = int(callback.data.split('_')[1])
    logger.info(f'📦 Пользователь {user_id} хочет просмотреть адрес {address_id}')
    address = await crud.get_address(session, user_id, address_id)
    await callback.message.edit_text(text=address.address, reply_markup=kb.address_details_keyboard(address))

@router.callback_query(F.data.startswith('delete_address_'))
@handle_db_errors()
async def delete_address(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    address_id = int(callback.data.split('_')[-1])
    logger.info(f'❌🏠 Пользователь {user_id} хочет удалить адрес {address_id}')
    address: Address = await crud.delete_address(session, user_id, address_id)
    if address.is_deleted:
        await callback.message.edit_text(text='🏠❌ Адрес удален')
    else:
        await callback.message.edit_text(text='⚠️ Что-то пошло не так во время удаления адреса')

