from typing import List
from sqlalchemy import select, delete, update
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from db.models import Product
from utils.decorators import db_errors, make_async_session


logger = logging.getLogger(__name__)


@db_errors()
@make_async_session
async def get_all_products(session: AsyncSession) -> List[Product]:
    result = await session.execute(
                            select(Product)
                            .options(selectinload(Product.category))
                            .order_by(Product.name)
                        )
    return result.scalars().all()


@db_errors()
@make_async_session
async def get_product(product_id: int, session: AsyncSession) -> Product:
    product = await session.execute(
                                select(Product)
                                .where(Product.id == product_id)
                                .options(selectinload(Product.category))
                                )
    return product.scalar_one() 


@db_errors()
@make_async_session
async def get_products_by_ids(product_ids: List[int], session: AsyncSession) -> List[Product]:
    result = await session.execute(
                            select(Product)
                            .where(Product.id.in_(product_ids))
                            .order_by(Product.name)
                            .with_for_update()
                            )
    return result.scalars().all()


@db_errors()
@make_async_session
async def get_products_by_category_and_offset(category_id: int, offset: int, limit: int, session: AsyncSession) -> List[Product]:
    result = await session.execute(
                            select(Product)
                            .where(Product.category_id == category_id)
                            .order_by(Product.name)
                            .offset(offset)
                            .limit(limit)
                        )
    return result.scalars().all()


@db_errors()
@make_async_session
async def add_product(name: str, price: int, session: AsyncSession) -> None:
    if price < 0:
        raise ValueError('Цена не может быть отрицательной')
    session.add(Product(name=name, price=price))
    await session.commit()


@db_errors()
@make_async_session
async def update_product_image_id(product_id: int, image_id: str, session: AsyncSession):
    await session.execute(update(Product).where(Product.id==product_id).values(image_id=image_id))
    await session.commit()