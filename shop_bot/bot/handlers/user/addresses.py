from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
import logging

import keyboards.addresses as kb
from db import crud
from db.models import Address
from utils.validators import is_valid_address
from utils.decorators import handle_db_errors


logger = logging.getLogger(__name__)
router = Router()

class AddNewAddress(StatesGroup):
    waiting_for_address = State()

@router.message(F.text.in_(['/addresses', '🏠 Мои адреса']))
async def show_addresses(message: Message, session: AsyncSession):
    logger.info(f'Пользователь {message.from_user.id} вызвал команду /addresses')
    
    user_id = message.from_user.id
    addresses = await crud.get_user_addresses(session, user_id)
    if not addresses:
        await message.answer('Здесь будут ваши адреса доставки. Пока адресов нет.')
        return
    await message.answer(text='Список ваших адресов доставки:', reply_markup=kb.address_list_keyboard(addresses))

@router.callback_query(F.data == 'new_address')
async def add_new_address(callback: CallbackQuery, state: FSMContext):
    logger.info(f'🏠 Пользователь {callback.from_user.id} хочет добавить новый адрес.')
    await callback.message.answer('Введите адрес: улица, дом, подъезд, квартира и этаж')
    await state.set_state(AddNewAddress.waiting_for_address)

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
