from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from db.models import Address
from utils.decorators import db_errors


@db_errors()
async def get_user_addresses(session: AsyncSession, user_id: int) -> List[Address]:
    result = await session.execute(
                        select(Address)
                        .where(Address.user_id==user_id, Address.is_deleted==False)
                        .order_by(Address.address)
                        )
    return result.scalars().all()

@db_errors()
async def count_user_addresses(session: AsyncSession, user_id: int):
    result = await session.execute(
                            select(func.count())
                            .select_from(Address)
                            .where(Address.user_id == user_id, Address.is_deleted == False)
    )
    return result.scalar()

@db_errors()
async def get_address(session: AsyncSession, user_id: int, address_id: int) -> Address:
    result = await session.execute(
                            select(Address)
                            .where(Address.user_id==user_id, Address.id==address_id)
                            )
    return result.scalar_one_or_none() 

@db_errors()
async def add_new_address(session: AsyncSession, user_id: int, address_str: str) -> Address:
    new_address: Address = Address(user_id=user_id, address=address_str)
    session.add(new_address)
    await session.commit()
    await session.refresh(new_address)
    return new_address


@db_errors()
async def delete_address(session: AsyncSession, user_id: int, address_id: int) -> Address:
    result = await session.execute(
                    select(Address)
                    .where(Address.user_id == user_id, Address.id == address_id)
                    )
    address = result.scalar_one_or_none() 
    if address:
        address.is_deleted = True
        await session.commit()
        await session.refresh(address)
        return address
    else:
        raise ValueError('Адрес не найден')