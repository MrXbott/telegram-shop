from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db.models import Category


async def get_categories(session: AsyncSession) -> List[Category]:
    result = await session.execute(select(Category))
    return result.scalars().all()


async def get_category_with_products(session: AsyncSession, category_id: int) -> Category:
    result = await session.execute(
                            select(Category)
                            .where(Category.id == category_id)
                            .options(selectinload(Category.products))
                        )
    category = result.scalar_one()
    return category