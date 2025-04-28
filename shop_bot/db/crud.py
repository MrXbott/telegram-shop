from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload, selectinload
from typing import List

from db.init import async_session
from db.models import User, Product, Category, Favorite


async def get_or_create_user(user_id: int, name: str) -> User:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, name=name)
            session.add(user)
            await session.commit()
        return user

    
async def get_all_products() -> List[Product]:
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
    
async def get_products_by_ids(product_ids: List[int]) -> List[Product]:
    async with async_session() as session:
        result = await session.execute(
                                select(Product)
                                .where(Product.id.in_(product_ids))
                                )
    return result.scalars().all()

async def add_product(name: str, price: int) -> None:
    async with async_session() as session:
        session.add(Product(name=name, price=price))
        await session.commit()


async def get_categories() -> List[Category]:
    async with async_session() as session:
        result = await session.execute(select(Category))
    return result.scalars().all()


async def get_category_with_products(category_id: int) -> Category:
    async with async_session() as session:
        result = await session.execute(
                                select(Category)
                                .where(Category.id == category_id)
                                .options(selectinload(Category.products))
                            )
        category = result.scalar_one()
        return category
    

async def add_to_favorites(user_id: int, product_id: int) -> None:
    async with async_session() as session:
        favorite = Favorite(user_id=user_id, product_id=product_id)
        session.add(favorite)
        await session.commit()


async def remove_from_favorites(user_id: int, product_id: int) -> None:
    async with async_session() as session:
        await session.execute(
                        delete(Favorite)
                        .where(Favorite.user_id == user_id, Favorite.product_id == product_id))
        await session.commit()


async def is_in_favorites(user_id: int, product_id: int) -> bool:
    async with async_session() as session:
        result = await session.execute(
                                select(Favorite)
                                .where(Favorite.user_id == user_id, Favorite.product_id == product_id))
        return result.scalar_one_or_none() is not None
    

async def get_user_favorites(user_id: int) -> List[Favorite]:
    async with async_session() as session:
        result = await session.execute(
                                select(Favorite)
                                .where(Favorite.user_id == user_id))
        return result.scalars().all()