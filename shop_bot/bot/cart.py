from typing import List
from db.redis import redis_client
from db import crud
from db.models import Product


class ProductInCart:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity


async def add_to_cart(user_id: int, product_id: int, quantity: int = 1) -> None:
    key = f'cart:{user_id}'
    await redis_client.hincrby(key, product_id, quantity)
    await redis_client.expire(key, 60 * 60 * 24 * 2)


async def remove_from_cart(user_id: int, product_id: int) -> None:
    key = f'cart:{user_id}'
    await redis_client.hdel(key, product_id)


async def get_cart(user_id: int) -> List[ProductInCart]:
    key = f'cart:{user_id}'
    items = await redis_client.hgetall(key)
    items = {int(k): int(v) for k, v in items.items()}
    product_ids = list(map(int, items.keys()))
    if not product_ids:
        return []
    products = await crud.get_products_by_ids(product_ids)
    return [ProductInCart(product, items[product.id]) for product in products]


async def clear_cart(user_id: int) -> None:
    key = f'cart:{user_id}'
    await redis_client.delete(key)