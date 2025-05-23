from typing import List
from decimal import Decimal
from db.redis import redis_client
from sqlalchemy.ext.asyncio import AsyncSession

from db import crud
from db.models import Product
from utils.decorators import redis_errors, make_async_session


class ProductInCart:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity


@redis_errors()
async def add_to_cart(user_id: int, product_id: int, quantity: int = 1) -> None:
    key = f'cart:{user_id}'
    await redis_client.hincrby(key, product_id, quantity)
    await redis_client.expire(key, 60 * 60 * 24 * 2)


@redis_errors()
async def remove_from_cart(user_id: int, product_id: int) -> None:
    key = f'cart:{user_id}'
    await redis_client.hdel(key, product_id)


@redis_errors()
async def get_product_quantity(user_id: int, product_id: int) -> int:
    key = f'cart:{user_id}'
    quantity = await redis_client.hget(key, str(product_id))
    return int(quantity) if quantity else 0
    

@redis_errors()
async def decrease_quantity(user_id: int, product_id: int) -> int:
    key = f'cart:{user_id}'
    current_quantity = await get_product_quantity(user_id, product_id)
    if current_quantity > 1:
        await add_to_cart(user_id, product_id, quantity=-1)
    else:
        await redis_client.hdel(key, product_id)
    return await get_product_quantity(user_id, product_id)


@redis_errors()
async def increase_quantity(user_id: int, product_id: int) -> int:
    await add_to_cart(user_id, product_id, quantity=1)
    return await get_product_quantity(user_id, product_id)
    

@redis_errors()
@make_async_session
async def get_cart(user_id: int, session: AsyncSession) -> List[ProductInCart]:
    key = f'cart:{user_id}'
    items = await redis_client.hgetall(key)
    items = {int(k): int(v) for k, v in items.items()}
    product_ids = list(map(int, items.keys()))
    if not product_ids:
        return []
    products = await crud.get_products_by_ids(product_ids)
    return [ProductInCart(product, items[product.id]) for product in products]

@redis_errors()
async def get_cart_total_sum(user_id) -> Decimal:
    products = await get_cart(user_id)
    total_sum = 0
    for product in products:
        total_sum += product.quantity * product.product.price
    return total_sum


async def clear_cart(user_id: int) -> None:
    key = f'cart:{user_id}'
    await redis_client.delete(key)