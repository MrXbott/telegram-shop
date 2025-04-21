from sqlalchemy import select, delete
from db.init import async_session
from db.models import Product, CartItem, User
from sqlalchemy.orm import joinedload


async def get_all_products():
    async with async_session() as session:
        result = await session.execute(select(Product))
        return result.scalars().all()

async def get_product(product_id: int):
    async with async_session() as session:
        return await session.get(Product, product_id)

async def add_to_cart(user_id: int, product_id: int):
    async with async_session() as session:
        session.add(CartItem(user_id=user_id, product_id=product_id))
        await session.commit()

async def get_cart(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(CartItem).options(joinedload(CartItem.product)).where(CartItem.user_id == user_id)

        )
        return result.scalars().all()

async def clear_cart(user_id: int):
    async with async_session() as session:
        await session.execute(delete(CartItem).where(CartItem.user_id == user_id))
        await session.commit()

async def create_product(name: str, price: int):
    async with async_session() as session:
        session.add(Product(name=name, price=price))
        await session.commit()

async def get_or_create_user(user_id: int, name: str):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, name=name)
            session.add(user)
            await session.commit()
        return user
