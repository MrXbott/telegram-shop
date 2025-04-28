from sqlalchemy import select, delete
from typing import List

from db.init import async_session
from db.models import Favorite


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