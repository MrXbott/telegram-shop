from typing import List
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Product


async def get_all_products(session: AsyncSession) -> List[Product]:
    result = await session.execute(
                            select(Product)
                            .options(selectinload(Product.category))
                        )
    return result.scalars().all()


async def get_product(session: AsyncSession, product_id: int) -> Product:
    product = await session.execute(
                                select(Product)
                                .where(Product.id == product_id)
                                .options(selectinload(Product.category))
                                )
    return product.scalar_one_or_none() 


async def get_products_by_ids(session: AsyncSession, product_ids: List[int]) -> List[Product]:
    result = await session.execute(
                            select(Product)
                            .where(Product.id.in_(product_ids))
                            )
    return result.scalars().all()


async def add_product(session: AsyncSession, name: str, price: int) -> None:
    session.add(Product(name=name, price=price))
    await session.commit()