from sqlalchemy import select, delete
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Favorite
from utils.decorators import db_errors, make_async_session


@db_errors()
@make_async_session
async def add_to_favorites(user_id: int, product_id: int, session: AsyncSession) -> None:
    favorite = Favorite(user_id=user_id, product_id=product_id)
    session.add(favorite)
    await session.commit()


@db_errors()
@make_async_session
async def remove_from_favorites(user_id: int, product_id: int, session: AsyncSession) -> None:
    await session.execute(
                    delete(Favorite)
                    .where(Favorite.user_id == user_id, Favorite.product_id == product_id))
    await session.commit()


@db_errors()
@make_async_session
async def is_in_favorites(user_id: int, product_id: int, session: AsyncSession) -> bool:
    result = await session.execute(
                            select(Favorite)
                            .where(Favorite.user_id == user_id, Favorite.product_id == product_id))
    return result.scalar_one_or_none() is not None
    

@db_errors()
@make_async_session
async def get_user_favorites(user_id: int, session: AsyncSession) -> List[Favorite]:
    result = await session.execute(
                            select(Favorite)
                            .where(Favorite.user_id == user_id))
    return result.scalars().all()