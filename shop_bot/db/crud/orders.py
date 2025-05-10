from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List
import logging

from db.models import Order, OrderItem, OrderStatus, Address
from db.cart import get_cart
from utils.decorators import db_errors
from exceptions.orders import InvalidOrderTotalPriceError
from exceptions.products import ProductOutOfStockError


logger = logging.getLogger(__name__)

@db_errors()
async def create_order(session: AsyncSession, user_id: int, data: dict) -> Order:   
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

    items = await get_cart(session, user_id)
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
async def get_orders(session: AsyncSession, user_id: int) -> List[Order]:
    result = await session.execute(
                            select(Order)
                            .where(Order.user_id==user_id)
                            .order_by(Order.created.desc())
                            )
    return result.scalars().all()


@db_errors()
async def get_order(session: AsyncSession, user_id: int, order_id: int):
    result = await session.execute(
                            select(Order)
                            .where(Order.user_id==user_id, Order.id==order_id)
                            .options(selectinload(Order.items).selectinload(OrderItem.product))
    )
    return result.scalar_one_or_none() 