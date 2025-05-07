from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import User, Address
from utils.decorators import db_errors


@db_errors()
async def get_user_addresses(session: AsyncSession, user_id: int) -> List[Address]:
    result = await session.execute(
                        select(Address)
                        .where(Address.user_id==user_id)
                        .order_by(Address.address)
                        )
    return result.scalars().all()


@db_errors()
async def add_new_address(session: AsyncSession, user_id: int, address_str: str) -> Address:
    new_address = Address(user_id=user_id, address=address_str)
    session.add(new_address)
    await session.commit()
    await session.refresh(new_address)
    return new_address
