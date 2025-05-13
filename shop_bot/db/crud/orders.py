from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update
from typing import List
import logging

from db.models import Order, OrderItem, OrderStatus, Address
from db.cart import get_cart
from utils.decorators import db_errors, make_async_session
from exceptions.orders import InvalidOrderTotalPriceError, OrderNotFound
from exceptions.order_statuses import OrderStatusNotFound, MultipleOrderStatusesFound
from exceptions.products import ProductOutOfStockError


logger = logging.getLogger(__name__)

@db_errors()
@make_async_session
async def create_order(user_id: int, data: dict, session: AsyncSession) -> Order:   
    address_id = data.get('address_id')
    address_text = data.get('address_text')

    if address_id:
        result = await session.execute(
                            select(Address)
                            .where(Address.user_id==user_id, Address.id==address_id)
                            )
        address = result.scalar_one_or_none() 
    elif address_text:
        # проверяем что среди адресов юзера нет точно такого же
        address = await session.scalar(
                                select(Address)
                                .where(Address.user_id == user_id, Address.address == address_text)
                        )
    else:
        raise ValueError('Данные для адреса (id или текст) не указаны')
    
    if not address:
        address = Address(user_id=user_id, address=address_text)
        session.add(address)
        await session.flush()
    
    result = await session.execute(select(OrderStatus.id).filter(OrderStatus.status == 'created'))
    default_status_id = result.scalar_one_or_none()
    if default_status_id is None:
        raise ValueError('Статус created не найден в базе данных. Невозможно создать заказ.')

    order = Order(
                user_id=user_id, 
                status_id = default_status_id,
                address_id=address.id, 
                name=data.get('name'),
                phone=data.get('phone'),
                total_price=0
                )
    session.add(order)
    await session.flush()

    items = await get_cart(user_id)
    order_items = []
    total_price = 0
    for item in items:
        if item.product.quantity_in_stock < item.quantity:
            raise ProductOutOfStockError(item.product.name)
        
        item.product.quantity_in_stock -= item.quantity
        total_price += item.product.price * item.quantity
        
        order_items.append(
            OrderItem(
                order_id=order.id, 
                product_id=item.product.id, 
                price_at_order=item.product.price, 
                quantity=item.quantity
            )
        )
    
    if total_price < 0:
        raise InvalidOrderTotalPriceError(total_price)
    order.total_price = total_price

    session.add_all(order_items)
    await session.commit()
    await session.refresh(order)
    return order


@db_errors()
@make_async_session
async def get_user_orders(user_id: int, session: AsyncSession) -> List[Order]:
    result = await session.execute(
                            select(Order)
                            .where(Order.user_id==user_id)
                            .order_by(Order.created.desc())
                            )
    return result.scalars().all()


@db_errors()
@make_async_session
async def get_order(user_id: int, order_id: int, session: AsyncSession) -> Order:
    try:
        result = await session.execute(
                                select(Order)
                                .where(Order.user_id==user_id, Order.id==order_id)
                                .options(selectinload(Order.items).selectinload(OrderItem.product))
                                )
        return result.scalar_one() 
    except NoResultFound:
        raise OrderNotFound(user_id, order_id)


@db_errors()
@make_async_session
async def get_status_id(status_code: str, session: AsyncSession) -> int:
    try:
        result = await session.execute(select(OrderStatus.id).filter(OrderStatus.status == status_code))
        return result.scalar_one()
    except NoResultFound:
        raise OrderStatusNotFound(status_code)
    except MultipleResultsFound:
        raise MultipleOrderStatusesFound(status_code)


@db_errors()
@make_async_session
async def update_order_status(user_id: int, order_id: int, status: str, session: AsyncSession) -> Order:
    try:
        status_id = await get_status_id(status)
    except (OrderStatusNotFound, MultipleOrderStatusesFound):
        raise

    await session.execute(
                    update(Order)
                    .where(Order.id==order_id, Order.user_id==user_id)
                    .values(status_id=status_id)
                    )
    await session.commit()

    try:
        result = await session.execute(select(Order).where(Order.id==order_id))
        return result.scalar_one()
    except NoResultFound:
        raise OrderNotFound(user_id, order_id)


@db_errors()
@make_async_session
async def return_cancelled_order_items(user_id: int, order_id: int, session: AsyncSession):
    order = await get_order(user_id, order_id)

    for item in order.items:
        item.product.quantity_in_stock += item.quantity

    await session.commit()


