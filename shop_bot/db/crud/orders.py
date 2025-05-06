from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List
import logging

from db.models import Order, OrderItem
from db.cart import get_cart
from utils.decorators import db_errors
from exceptions.orders import InvalidOrderTotalPriceError
from exceptions.products import ProductOutOfStockError


logger = logging.getLogger(__name__)

@db_errors()
async def create_order(session: AsyncSession, user_id: int) -> Order:
    order = Order(user_id=user_id, total_price=0)
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