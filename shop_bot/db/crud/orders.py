from sqlalchemy.ext.asyncio import AsyncSession
import logging

from db.models import Order, OrderItem
from db.cart import get_cart
from utils.decorators import db_errors


logger = logging.getLogger(__name__)

@db_errors()
async def create_order(session: AsyncSession, user_id: int) -> Order:
    order = Order(user_id=user_id)
    session.add(order)
    await session.flush()

    items = await get_cart(session, user_id)
    order_items = [OrderItem(order_id=order.id, product_id=item.product.id, quantity=item.quantity) for item in items]
    session.add_all(order_items)

    await session.commit()
    await session.refresh(order)
    return order
