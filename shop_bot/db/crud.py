from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload, selectinload
from typing import List

from db.init import async_session
from db.models import User, Product, Category


async def get_or_create_user(user_id: int, name: str):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, name=name)
            session.add(user)
            await session.commit()
        return user

    
async def get_all_products():
    async with async_session() as session:
        result = await session.execute(
                                select(Product)
                                .options(selectinload(Product.category))
                            )
        return result.scalars().all()

async def get_product(product_id: int) -> Product:
    async with async_session() as session:
        product = await session.execute(
                                    select(Product)
                                    .where(Product.id == product_id)
                                    .options(selectinload(Product.category))
                                    )
        return product.scalar_one_or_none() 
    
async def get_products_by_ids(product_ids: List[int]):
    async with async_session() as session:
        result = await session.execute(
                                select(Product)
                                .where(Product.id.in_(product_ids))
                                )
    return result.scalars().all()

async def add_product(name: str, price: int):
    async with async_session() as session:
        session.add(Product(name=name, price=price))
        await session.commit()


async def get_categories():
    async with async_session() as session:
        result = await session.execute(select(Category))
    return result.scalars().all()

async def get_category_with_products(category_id: int):
    async with async_session() as session:
        result = await session.execute(
                                select(Category)
                                .where(Category.id == category_id)
                                .options(selectinload(Category.products))
                            )
        category = result.scalar_one()
        return category