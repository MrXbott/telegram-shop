from sqlalchemy import select, delete, func
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db.models import Category, Product
from utils.decorators import db_errors, make_async_session


@db_errors()
@make_async_session
async def get_categories(session: AsyncSession) -> List[Category]:
    result = await session.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


@db_errors()
@make_async_session
async def get_category(category_id: int, session: AsyncSession) -> Category:
    result = await session.execute(
                            select(Category)
                            .where(Category.id == category_id)
                        )
    return result.scalar_one()


@db_errors()
@make_async_session
async def get_category_with_products(category_id: int, session: AsyncSession) -> Category:
    result = await session.execute(
                            select(Category)
                            .where(Category.id == category_id)
                            .options(selectinload(Category.products))
                        )
    return result.scalar_one()



@db_errors()
@make_async_session
async def count_products_in_category(category_id: int, session: AsyncSession) -> int:
    result = await session.execute(
        select(func.count()).select_from(Product).where(Product.category_id == category_id)
    )
    return result.scalar()