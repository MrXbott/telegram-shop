from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from utils.decorators import db_errors


@db_errors()
async def get_or_create_user(session: AsyncSession, user_id: int, name: str) -> User:
    user = await session.get(User, user_id)
    if not user:
        user = User(id=user_id, name=name)
        session.add(user)
        await session.commit()
    return user

    