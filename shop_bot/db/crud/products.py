from typing import List
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from db.models import Product
from utils.decorators import db_errors


logger = logging.getLogger(__name__)


@db_errors()
async def get_all_products(session: AsyncSession) -> List[Product]:
    result = await session.execute(
                            select(Product)
                            .options(selectinload(Product.category))
                            .order_by(Product.name)
                        )
    return result.scalars().all()


@db_errors()
async def get_product(session: AsyncSession, product_id: int) -> Product:
    product = await session.execute(
                                select(Product)
                                .where(Product.id == product_id)
                                .options(selectinload(Product.category))
                                )
    return product.scalar_one_or_none() 


@db_errors()
async def get_products_by_ids(session: AsyncSession, product_ids: List[int]) -> List[Product]:
    result = await session.execute(
                            select(Product)
                            .where(Product.id.in_(product_ids))
                            .order_by(Product.name)
                            .with_for_update()
                            )
    return result.scalars().all()


@db_errors()
async def get_products_by_category_and_offset(session: AsyncSession, category_id: int, offset: int, limit: int) -> List[Product]:
    result = await session.execute(
                            select(Product)
                            .where(Product.category_id == category_id)
                            .order_by(Product.name)
                            .offset(offset)
                            .limit(limit)
                        )
    return result.scalars().all()


@db_errors()
async def add_product(session: AsyncSession, name: str, price: int) -> None:
    if price < 0:
        raise ValueError('Цена не может быть отрицательной')
    session.add(Product(name=name, price=price))
    await session.commit()
