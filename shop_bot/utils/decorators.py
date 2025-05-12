from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from aiogram.types import Message, CallbackQuery
from redis.exceptions import RedisError, ConnectionError, TimeoutError
import asyncio
import logging

from db.init import async_session_maker


logger = logging.getLogger(__name__)

def handle_db_errors():
    def decorator(func):
        @wraps(func)
        async def wrapper(event: Message|CallbackQuery, **kwargs):
            try:
                return await func(event, **kwargs)
            except (SQLAlchemyError, OSError, ConnectionError, asyncio.TimeoutError) as e:
                logger.error(f'!--- Ошибка при обращении к базе данных: {e}', exc_info=False)
                await event.answer('⚠️ Произошла ошибка при обращении к базе данных. Попробуйте позже.')
        return wrapper
    return decorator


def db_errors(log_message: str = ''):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except SQLAlchemyError as e:
                logger.exception(f'!--- Ошибка в {func.__name__}: {log_message or str(e)}')
                raise
        return wrapper
    return decorator


def redis_errors(log_message: str = ''):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except (ConnectionError, TimeoutError, RedisError) as e:
                logger.warning(f'Redis error in {func.__name__}: {log_message or str(e)}')
        return wrapper
    return decorator


def make_async_session(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                return await func(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()  
                raise e 
            finally:
                await session.close()  
    return wrapper
