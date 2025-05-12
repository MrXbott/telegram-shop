from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from utils.decorators import db_errors, make_async_session


@db_errors()
@make_async_session
async def get_or_create_user(user_id: int, name: str, session: AsyncSession) -> User:
    user = await session.get(User, user_id)
    if not user:
        user = User(id=user_id, name=name)
        session.add(user)
        await session.commit()
    return user

    