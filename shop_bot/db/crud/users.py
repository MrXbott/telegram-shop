from typing import List

from db.init import async_session
from db.models import User


async def get_or_create_user(user_id: int, name: str) -> User:
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, name=name)
            session.add(user)
            await session.commit()
        return user

    