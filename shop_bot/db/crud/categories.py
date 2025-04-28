from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload, selectinload
from typing import List

from db.init import async_session
from db.models import Category


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