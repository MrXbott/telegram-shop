from typing import List
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload, selectinload

from db.models import Product
from db.init import async_session


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