from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import crud
from decouple import config

router = Router()

try:
    ADMIN_ID = int(config('ADMIN_ID'))
except:
    print('Cant convert ADMIN_ID to int type')

# Машина состояний
class AddProduct(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()


@router.message(F.text == '/add')
async def add_product_cmd(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer('У вас нет доступа.')
        return
    await message.answer('Введите название товара:')
    await state.set_state(AddProduct.waiting_for_name)


@router.message(AddProduct.waiting_for_name)
async def add_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите цену товара (в рублях):')
    await state.set_state(AddProduct.waiting_for_price)


@router.message(AddProduct.waiting_for_price)
async def add_product_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
    except ValueError:
        await message.answer('Введите цену числом.')
        return

    data = await state.get_data()
    name = data['name']
    await crud.add_product(name, price)
    await message.answer(f'Товар <b>{name}</b> за <b>{price}₽</b> добавлен в каталог.')
    await state.clear()
