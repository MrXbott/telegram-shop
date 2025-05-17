import asyncio
import getpass
from sqlalchemy import select
from werkzeug.security import generate_password_hash
from db.init import async_session_maker
from db.models import Admin

async def create_admin():
    username = input('Введите username: ')
    email = input('Введите email: ')
    password = getpass.getpass('Введите пароль: ')

    hashed_password = generate_password_hash(password)

    async with async_session_maker() as session:
        exists = await session.scalar(
            select(Admin).where(Admin.email == email or Admin.username == username)
        )
        if exists:
            print('Админ с таким email/username уже существует.')
            return

        admin = Admin(username=username, email=email, password=hashed_password, is_active=True)
        session.add(admin)
        await session.commit()
        print('Админ успешно создан.')


if __name__ == '__main__':
    asyncio.run(create_admin())
